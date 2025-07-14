# -*- coding: utf-8 -*-
"""
通知清理管理器
负责清理过期通知和维护通知数量限制
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NotificationCleanupManager:
    """通知清理管理器"""
    
    def __init__(self):
        self._cleanup_thread = None
        self._stop_event = threading.Event()
        self._running = False
        
    def start_cleanup_scheduler(self, interval_hours: int = 24):
        """启动清理调度器
        
        Args:
            interval_hours: 清理间隔（小时），默认24小时
        """
        if self._running:
            logger.warning("Cleanup scheduler is already running")
            return
            
        self._stop_event.clear()
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            args=(interval_hours,),
            daemon=True,
            name="NotificationCleanup"
        )
        self._cleanup_thread.start()
        self._running = True
        logger.info(f"Notification cleanup scheduler started with {interval_hours}h interval")
    
    def stop_cleanup_scheduler(self):
        """停止清理调度器"""
        if not self._running:
            return
            
        self._stop_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        self._running = False
        logger.info("Notification cleanup scheduler stopped")
    
    def _cleanup_loop(self, interval_hours: int):
        """清理循环"""
        while not self._stop_event.is_set():
            try:
                # 检查是否启用自动清理
                if self._is_auto_cleanup_enabled():
                    # 执行清理
                    self.cleanup_expired_notifications()
                    self.cleanup_excess_notifications()
                    logger.info("Auto cleanup completed")
                else:
                    logger.debug("Auto cleanup is disabled, skipping")

                # 等待下次清理
                self._stop_event.wait(interval_hours * 3600)  # 转换为秒

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                # 出错时等待1小时后重试
                self._stop_event.wait(3600)
    
    def cleanup_expired_notifications(self) -> Dict[str, Any]:
        """清理过期通知
        
        Returns:
            Dict: 清理结果统计
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            # 获取保留天数配置
            retention_days = self._get_retention_days()
            if retention_days <= 0:
                logger.debug("Retention days is 0 or negative, skipping cleanup")
                return {'deleted_count': 0, 'retention_days': retention_days}
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 计算过期时间
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # 删除过期通知
            query, params = adapt_sql("""
                DELETE FROM notifications 
                WHERE created_at < %s
            """, (cutoff_date,))
            
            cursor.execute(query, params)
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired notifications (older than {retention_days} days)")
            else:
                logger.debug(f"No expired notifications found (retention: {retention_days} days)")
            
            return {
                'deleted_count': deleted_count,
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired notifications: {e}")
            return {'error': str(e), 'deleted_count': 0}
    
    def cleanup_excess_notifications(self) -> Dict[str, Any]:
        """清理超出数量限制的通知
        
        Returns:
            Dict: 清理结果统计
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            # 获取最大通知数量配置
            max_notifications = self._get_max_notifications_per_user()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 获取所有用户
            query, params = adapt_sql("SELECT DISTINCT user_id FROM notifications", ())
            cursor.execute(query, params)
            user_ids = [row[0] for row in cursor.fetchall()]
            
            total_deleted = 0
            user_cleanup_stats = {}
            
            for user_id in user_ids:
                # 为每个用户清理超出限制的通知
                query, params = adapt_sql("""
                    DELETE FROM notifications 
                    WHERE user_id = %s 
                    AND id NOT IN (
                        SELECT id FROM (
                            SELECT id FROM notifications 
                            WHERE user_id = %s 
                            ORDER BY created_at DESC 
                            LIMIT %s
                        ) AS recent_notifications
                    )
                """, (user_id, user_id, max_notifications))
                
                cursor.execute(query, params)
                deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    total_deleted += deleted_count
                    user_cleanup_stats[user_id] = deleted_count
                    logger.debug(f"Cleaned up {deleted_count} excess notifications for user {user_id}")
            
            conn.commit()
            conn.close()
            
            if total_deleted > 0:
                logger.info(f"Cleaned up {total_deleted} excess notifications for {len(user_cleanup_stats)} users")
            
            return {
                'total_deleted': total_deleted,
                'max_notifications': max_notifications,
                'affected_users': len(user_cleanup_stats),
                'user_stats': user_cleanup_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup excess notifications: {e}")
            return {'error': str(e), 'total_deleted': 0}
    
    def _get_retention_days(self) -> int:
        """获取通知保留天数配置"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT config_value FROM system_config 
                WHERE config_key = %s
            """, ('notification_retention_days',))
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return int(result[0])
            else:
                return 30  # 默认30天
                
        except Exception as e:
            logger.error(f"Failed to get retention days config: {e}")
            return 30  # 默认30天
    
    def _get_max_notifications_per_user(self) -> int:
        """获取每用户最大通知数量配置"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            query, params = adapt_sql("""
                SELECT config_value FROM system_config
                WHERE config_key = %s
            """, ('notification_max_per_user',))

            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()

            if result:
                return int(result[0])
            else:
                return 100  # 默认100条

        except Exception as e:
            logger.error(f"Failed to get max notifications config: {e}")
            return 100  # 默认100条

    def _is_auto_cleanup_enabled(self) -> bool:
        """检查是否启用自动清理"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            query, params = adapt_sql("""
                SELECT config_value FROM system_config
                WHERE config_key = %s
            """, ('notification_auto_cleanup_enabled',))

            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()

            if result:
                return result[0].lower() == 'true'

            return False  # 默认关闭

        except Exception as e:
            logger.error(f"Failed to get auto cleanup config: {e}")
            return False  # 默认关闭
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """获取清理统计信息"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            from datetime import datetime, timedelta

            conn = get_db_connection()
            cursor = conn.cursor()

            # 总通知数
            query, params = adapt_sql("SELECT COUNT(*) FROM notifications", ())
            cursor.execute(query, params)
            total_notifications = cursor.fetchone()[0]

            # 用户通知分布
            query, params = adapt_sql("""
                SELECT user_id, COUNT(*) as count
                FROM notifications
                GROUP BY user_id
                ORDER BY count DESC
            """, ())
            cursor.execute(query, params)
            user_distribution = cursor.fetchall()

            # 最旧通知时间
            query, params = adapt_sql("""
                SELECT MIN(created_at) FROM notifications
            """, ())
            cursor.execute(query, params)
            oldest_notification = cursor.fetchone()[0]

            # 计算过期记录数
            retention_days = self._get_retention_days()
            expired_count = 0
            if retention_days > 0:
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                query, params = adapt_sql("""
                    SELECT COUNT(*) FROM notifications
                    WHERE created_at < %s
                """, (cutoff_date,))
                cursor.execute(query, params)
                expired_count = cursor.fetchone()[0]

            # 计算过量记录数
            max_per_user = self._get_max_notifications_per_user()
            excess_count = 0
            if max_per_user > 0:
                query, params = adapt_sql("""
                    SELECT user_id, COUNT(*) as count
                    FROM notifications
                    GROUP BY user_id
                    HAVING COUNT(*) > %s
                """, (max_per_user,))
                cursor.execute(query, params)
                excess_users = cursor.fetchall()

                # 计算总的过量记录数
                for user_id, count in excess_users:
                    excess_count += count - max_per_user

            conn.close()

            return {
                'total_notifications': total_notifications,
                'user_count': len(user_distribution),
                'user_distribution': [{'user_id': row[0], 'count': row[1]} for row in user_distribution],
                'oldest_notification': oldest_notification.isoformat() if oldest_notification else None,
                'retention_days': retention_days,
                'max_per_user': max_per_user,
                'expired_count': expired_count,
                'excess_count': excess_count
            }

        except Exception as e:
            logger.error(f"Failed to get cleanup stats: {e}")
            return {'error': str(e)}

# 全局清理管理器实例
cleanup_manager = NotificationCleanupManager()
