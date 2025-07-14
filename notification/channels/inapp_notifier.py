# -*- coding: utf-8 -*-
"""
应用内通知器
负责保存应用内通知到数据库
"""

import logging
from datetime import datetime
from typing import Dict, Any

from .base import BaseNotifier

logger = logging.getLogger(__name__)

class InAppNotifier(BaseNotifier):
    """应用内通知器"""

    def __init__(self):
        logger.debug("In-app notifier initialized")
    
    def is_enabled(self) -> bool:
        """应用内通知总是启用"""
        return True
    
    def send(self, title: str, content: str, recipient: Dict[str, Any], 
             priority: int = 1, metadata: Dict[str, Any] = None) -> bool:
        """发送应用内通知"""
        
        if not self.validate_recipient(recipient):
            logger.warning(f"Invalid recipient for in-app notification: {recipient}")
            return False
        
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 插入通知记录
            query, params = adapt_sql("""
                INSERT INTO notifications 
                (user_id, title, content, read_status, created_at, related_bug_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                recipient['id'],
                title,
                content,
                False,  # 未读状态
                datetime.now(),
                metadata.get('bug_id') if metadata else None
            ))
            
            cursor.execute(query, params)
            
            # 清理旧通知（保持最新的通知数量）
            self._cleanup_old_notifications(cursor, recipient['id'])
            
            conn.commit()
            conn.close()
            
            logger.info(f"In-app notification saved for user {recipient['id']}: {title}")
            
            # 如果有实时推送需求，可以在这里添加WebSocket推送
            self._push_realtime_notification(recipient['id'], {
                'title': title,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save in-app notification for user {recipient.get('id', 'unknown')}: {str(e)}")
            return False
    
    def _cleanup_old_notifications(self, cursor, user_id: str):
        """清理旧通知，保持最新的通知"""
        try:
            from sql_adapter import adapt_sql

            # 从配置中获取最大通知数量
            max_notifications = self._get_max_notifications_per_user()

            # 删除超出限制的旧通知
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
                logger.debug(f"Cleaned up {deleted_count} old notifications for user {user_id} (limit: {max_notifications})")

        except Exception as e:
            logger.error(f"Failed to cleanup old notifications for user {user_id}: {str(e)}")

    def _get_max_notifications_per_user(self) -> int:
        """从配置中获取每用户最大通知数量"""
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
    
    def _push_realtime_notification(self, user_id: str, notification_data: Dict[str, Any]):
        """实时推送通知（WebSocket）"""
        try:
            # 这里可以集成WebSocket推送
            # 目前只记录日志，后续可以扩展
            logger.debug(f"Real-time notification for user {user_id}: {notification_data['title']}")
            
            # TODO: 实现WebSocket推送
            # if websocket_manager:
            #     websocket_manager.send_to_user(user_id, {
            #         'type': 'notification',
            #         'data': notification_data
            #     })
            
        except Exception as e:
            logger.error(f"Failed to push real-time notification: {str(e)}")
    
    def get_user_notifications(self, user_id: str, limit: int = 20, offset: int = 0) -> list:
        """获取用户的应用内通知"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT id, title, content, read_status, created_at, related_bug_id
                FROM notifications 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            
            cursor.execute(query, params)
            notifications = cursor.fetchall()
            conn.close()
            
            return [{
                'id': n[0],
                'title': n[1],
                'content': n[2],
                'read_status': n[3],
                'created_at': n[4],
                'related_bug_id': n[5]
            } for n in notifications]
            
        except Exception as e:
            logger.error(f"Failed to get notifications for user {user_id}: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id: int, user_id: str) -> bool:
        """标记通知为已读"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                UPDATE notifications 
                SET read_status = %s, read_at = %s
                WHERE id = %s AND user_id = %s
            """, (True, datetime.now(), notification_id, user_id))
            
            cursor.execute(query, params)
            success = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if success:
                logger.debug(f"Notification {notification_id} marked as read for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {str(e)}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """获取用户未读通知数量"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = %s AND read_status = %s
            """, (user_id, False))
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to get unread count for user {user_id}: {str(e)}")
            return 0

    def mark_all_as_read(self, user_id: str) -> bool:
        """标记用户所有通知为已读"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            query, params = adapt_sql("""
                UPDATE notifications
                SET read_status = %s, read_at = %s
                WHERE user_id = %s AND read_status = %s
            """, (True, datetime.now(), user_id, False))

            cursor.execute(query, params)
            success = cursor.rowcount > 0

            conn.commit()
            conn.close()

            if success:
                logger.debug(f"All notifications marked as read for user {user_id}")

            return True  # 即使没有未读通知也返回成功

        except Exception as e:
            logger.error(f"Failed to mark all notifications as read for user {user_id}: {str(e)}")
            return False
