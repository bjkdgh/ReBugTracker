# -*- coding: utf-8 -*-
"""
通知管理器
负责管理服务器级别和用户级别的通知开关
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class NotificationManager:
    """通知管理器"""
    
    @staticmethod
    def is_notification_enabled() -> bool:
        """
        检查服务器通知功能是否开启
        
        Returns:
            bool: 通知功能是否启用
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 检查系统配置表
            query, params = adapt_sql("""
                SELECT config_value FROM system_config 
                WHERE config_key = %s
            """, ('notification_enabled',))
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                enabled = result[0].lower() == 'true'
                logger.debug(f"Server notification enabled: {enabled}")
                return enabled
            
            # 默认开启
            logger.debug("No notification config found, defaulting to enabled")
            return True
            
        except Exception as e:
            logger.error(f"Error checking notification status: {e}")
            return True  # 出错时默认开启

    @staticmethod
    def set_notification_enabled(enabled: bool) -> bool:
        """
        设置服务器通知功能开关

        Args:
            enabled: 是否启用通知功能

        Returns:
            bool: 设置是否成功
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            # 更新或插入配置
            config_value = 'true' if enabled else 'false'

            # 先尝试更新
            cursor.execute("""
                UPDATE system_config
                SET config_value = %s, updated_at = CURRENT_TIMESTAMP
                WHERE config_key = 'notification_enabled'
            """, (config_value,))

            # 如果没有更新任何行，则插入新记录
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO system_config (config_key, config_value, description)
                    VALUES ('notification_enabled', %s, '服务器通知功能开关')
                """, (config_value,))

            conn.commit()
            conn.close()

            logger.info(f"Server notification {'enabled' if enabled else 'disabled'}")
            return True

        except Exception as e:
            logger.error(f"Failed to set notification enabled status: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

    @staticmethod
    def is_global_notification_enabled(notification_type: str) -> bool:
        """
        检查全局通知类型是否启用

        Args:
            notification_type: 通知类型 ('email' 或 'gotify')

        Returns:
            bool: 该类型通知是否全局启用
        """
        try:
            from db_factory import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            config_key = f'{notification_type}_global_enabled'
            cursor.execute("""
                SELECT config_value
                FROM system_config
                WHERE config_key = %s
            """, (config_key,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return result[0].lower() == 'true'
            else:
                return True  # 默认启用

        except Exception as e:
            logger.error(f"Failed to check global {notification_type} notification status: {e}")
            return True  # 出错时默认启用

    @staticmethod
    def is_user_notification_enabled(user_id: str) -> Dict[str, bool]:
        """
        检查用户通知开关状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, bool]: 各渠道的开关状态
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT email_enabled, gotify_enabled, inapp_enabled
                FROM user_notification_preferences 
                WHERE user_id = %s
            """, (user_id,))
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                preferences = {
                    'email': result[0],
                    'gotify': result[1],
                    'inapp': result[2]
                }
                logger.debug(f"User {user_id} notification preferences: {preferences}")
                return preferences
            
            # 默认全部开启
            default_prefs = {'email': True, 'gotify': True, 'inapp': True}
            logger.debug(f"No preferences found for user {user_id}, using defaults")
            return default_prefs
            
        except Exception as e:
            logger.error(f"Error checking user notification preferences for {user_id}: {e}")
            return {'email': True, 'gotify': True, 'inapp': True}
    
    @staticmethod
    def set_server_notification(enabled: bool, admin_user_id: str) -> bool:
        """
        设置服务器通知开关（仅管理员）
        
        Args:
            enabled: 是否启用
            admin_user_id: 管理员用户ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 检查是否为管理员
            if not NotificationManager._is_admin(admin_user_id):
                logger.warning(f"User {admin_user_id} is not admin, cannot set server notification")
                return False
            
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 更新或插入配置
            # 先尝试更新
            query, params = adapt_sql("""
                UPDATE system_config 
                SET config_value = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
                WHERE config_key = %s
            """, (str(enabled).lower(), admin_user_id, 'notification_enabled'))
            
            cursor.execute(query, params)
            
            # 如果没有更新任何行，则插入新记录
            if cursor.rowcount == 0:
                query, params = adapt_sql("""
                    INSERT INTO system_config (config_key, config_value, updated_by, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, ('notification_enabled', str(enabled).lower(), admin_user_id))
                
                cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Server notification {'enabled' if enabled else 'disabled'} by admin {admin_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting server notification: {e}")
            return False
    
    @staticmethod
    def set_user_notification(user_id: str, channel: str, enabled: bool, 
                            admin_user_id: Optional[str] = None) -> bool:
        """
        设置用户通知开关
        
        Args:
            user_id: 目标用户ID
            channel: 通知渠道 (email/gotify/inapp)
            enabled: 是否启用
            admin_user_id: 管理员用户ID（可选）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 权限检查
            if admin_user_id:
                # 管理员操作，需要验证管理员权限
                if not NotificationManager._is_admin(admin_user_id):
                    logger.warning(f"User {admin_user_id} is not admin")
                    return False
            else:
                # 用户自己操作，暂时允许（后续可以添加用户身份验证）
                pass
            
            if channel not in ['email', 'gotify', 'inapp']:
                logger.error(f"Invalid notification channel: {channel}")
                return False
            
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 检查用户是否已有偏好设置
            query, params = adapt_sql("""
                SELECT user_id FROM user_notification_preferences 
                WHERE user_id = %s
            """, (user_id,))
            
            cursor.execute(query, params)
            exists = cursor.fetchone() is not None
            
            if exists:
                # 更新现有设置
                column_name = f"{channel}_enabled"
                query, params = adapt_sql(f"""
                    UPDATE user_notification_preferences 
                    SET {column_name} = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (enabled, user_id))
                
                cursor.execute(query, params)
            else:
                # 创建新设置
                email_enabled = enabled if channel == 'email' else True
                gotify_enabled = enabled if channel == 'gotify' else True
                inapp_enabled = enabled if channel == 'inapp' else True
                
                query, params = adapt_sql("""
                    INSERT INTO user_notification_preferences 
                    (user_id, email_enabled, gotify_enabled, inapp_enabled, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (user_id, email_enabled, gotify_enabled, inapp_enabled))
                
                cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            action = "enabled" if enabled else "disabled"
            operator = f"by admin {admin_user_id}" if admin_user_id else "by user"
            logger.info(f"User {user_id} {channel} notification {action} {operator}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting user notification: {e}")
            return False
    
    @staticmethod
    def _is_admin(user_id: str) -> bool:
        """
        检查是否为管理员
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否为管理员
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT role_en FROM users WHERE id = %s
            """, (user_id,))
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            is_admin = result and result[0] == 'gly'
            logger.debug(f"User {user_id} admin check: {is_admin}")
            return is_admin
            
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_all_users_preferences() -> list:
        """
        获取所有用户的通知偏好（管理员用）
        
        Returns:
            list: 用户偏好列表
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT u.id, u.username, u.chinese_name, u.role_en,
                       COALESCE(p.email_enabled, true) as email_enabled,
                       COALESCE(p.gotify_enabled, true) as gotify_enabled,
                       COALESCE(p.inapp_enabled, true) as inapp_enabled
                FROM users u
                LEFT JOIN user_notification_preferences p ON u.id = p.user_id
                ORDER BY u.role_en, u.username
            """, ())
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            conn.close()
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users preferences: {e}")
            return []

    @staticmethod
    def set_user_notification_preferences(user_id: str, email_enabled: bool = True,
                                        gotify_enabled: bool = True, inapp_enabled: bool = True) -> bool:
        """
        设置用户通知偏好

        Args:
            user_id: 用户ID
            email_enabled: 是否启用邮件通知
            gotify_enabled: 是否启用Gotify通知
            inapp_enabled: 是否启用应用内通知

        Returns:
            bool: 设置是否成功
        """
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            # 检查是否已存在偏好设置
            query, params = adapt_sql("""
                SELECT user_id FROM user_notification_preferences
                WHERE user_id = %s
            """, (user_id,))

            cursor.execute(query, params)
            existing = cursor.fetchone()

            if existing:
                # 更新现有设置
                query, params = adapt_sql("""
                    UPDATE user_notification_preferences
                    SET email_enabled = %s, gotify_enabled = %s, inapp_enabled = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (email_enabled, gotify_enabled, inapp_enabled, user_id))
            else:
                # 插入新设置
                query, params = adapt_sql("""
                    INSERT INTO user_notification_preferences
                    (user_id, email_enabled, gotify_enabled, inapp_enabled)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, email_enabled, gotify_enabled, inapp_enabled))

            cursor.execute(query, params)
            conn.commit()
            conn.close()

            logger.info(f"Set notification preferences for user {user_id}: email={email_enabled}, gotify={gotify_enabled}, inapp={inapp_enabled}")
            return True

        except Exception as e:
            logger.error(f"Failed to set user notification preferences for user {user_id}: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
