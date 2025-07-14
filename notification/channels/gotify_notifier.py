# -*- coding: utf-8 -*-
"""
Gotify通知器
负责发送Gotify推送通知
"""

import requests
import logging
from typing import Dict, Any
import os

from .base import BaseNotifier

logger = logging.getLogger(__name__)

class GotifyNotifier(BaseNotifier):
    """Gotify通知器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.server_url = self.config['server_url'].rstrip('/')

        logger.debug(f"Gotify notifier initialized: enabled={self.config['enabled']}, "
                    f"server={self.server_url}")

    def _load_config(self) -> Dict[str, Any]:
        """从数据库加载Gotify配置，回退到环境变量"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            from config import DB_TYPE

            conn = get_db_connection()

            # 根据数据库类型设置cursor
            if DB_TYPE == 'postgres':
                from psycopg2.extras import DictCursor
                cursor = conn.cursor(cursor_factory=DictCursor)
            else:
                cursor = conn.cursor()

            # 获取Gotify相关配置
            query, params = adapt_sql("""
                SELECT config_key, config_value
                FROM system_config
                WHERE config_key LIKE %s
            """, ('notification_gotify_%',))

            cursor.execute(query, params)
            configs = cursor.fetchall()
            conn.close()

            # 解析配置
            config_dict = {}
            for config in configs:
                # 兼容不同数据库的返回格式
                if hasattr(config, 'keys'):  # DictCursor
                    key = config['config_key'].replace('notification_gotify_', '')
                    value = config['config_value']
                else:  # 普通tuple
                    key = config[0].replace('notification_gotify_', '')
                    value = config[1]
                config_dict[key] = value

            logger.debug(f"Loaded Gotify config from database: {list(config_dict.keys())}")

            # 构建最终配置
            return {
                'enabled': config_dict.get('enabled', 'false').lower() == 'true',
                'server_url': config_dict.get('server_url', 'http://localhost:8080'),
                'app_token': config_dict.get('app_token', ''),
                'default_priority': int(config_dict.get('default_priority', '10')),
            }

        except Exception as e:
            logger.error(f"Failed to load Gotify config from database: {e}")
            # 回退到环境变量配置
            logger.debug("Falling back to environment variables")
            return {
                'enabled': os.getenv('GOTIFY_ENABLED', 'false').lower() == 'true',
                'server_url': os.getenv('GOTIFY_SERVER_URL', 'http://localhost:8080'),
                'app_token': os.getenv('GOTIFY_APP_TOKEN', ''),
                'default_priority': int(os.getenv('GOTIFY_DEFAULT_PRIORITY', '10')),
            }
    
    def is_enabled(self) -> bool:
        """检查Gotify通知是否启用"""
        # 检查全局Gotify开关
        try:
            from notification.notification_manager import NotificationManager
            if not NotificationManager.is_global_notification_enabled('gotify'):
                return False
        except Exception as e:
            logger.error(f"Failed to check global gotify notification status: {e}")

        return (self.config['enabled'] and
                bool(self.config['app_token']) and
                bool(self.config['server_url']))
    
    def send(self, title: str, content: str, recipient: Dict[str, Any],
             priority: int = 1, metadata: Dict[str, Any] = None) -> bool:
        """发送Gotify通知"""

        if not self.is_enabled():
            logger.debug("Gotify notifications disabled or not configured")
            return False

        if not self.validate_recipient(recipient):
            logger.warning(f"Invalid recipient for Gotify: {recipient}")
            return False

        try:
            # 获取用户专属的App Token
            user_app_token = self._get_user_app_token(recipient.get('id'))
            if not user_app_token:
                # 如果用户没有配置专属Token，使用全局Token但标明接收者
                logger.warning(f"No user-specific Gotify token for {recipient.get('name')}, using global token with recipient marking")
                return self._send_with_global_token(title, content, recipient, priority, metadata)

            url = f"{self.server_url}/message"

            # 所有Gotify通知都使用最高优先级10
            gotify_priority = 10

            # 格式化内容为Markdown
            formatted_content = self._format_content_markdown(content, metadata)

            data = {
                "title": title,
                "message": formatted_content,
                "priority": gotify_priority
            }

            # 添加额外信息
            if metadata:
                data["extras"] = {
                    "client::display": {
                        "contentType": "text/markdown"
                    },
                    "rebugtracker": {
                        "event_type": metadata.get('event_type', ''),
                        "bug_id": metadata.get('bug_id', ''),
                        "timestamp": metadata.get('timestamp', ''),
                        "recipient_id": recipient.get('id', '')
                    }
                }

            headers = {
                "X-Gotify-Key": user_app_token,  # 使用用户专属Token
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"Gotify notification sent to {recipient.get('name', 'unknown')} (user token): {title}")
                return True
            else:
                logger.error(f"Gotify API error: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Gotify notification (network error): {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send Gotify notification: {str(e)}")
            return False

    def _get_user_app_token(self, user_id: str) -> str:
        """获取用户专属的Gotify App Token"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql

            conn = get_db_connection()
            cursor = conn.cursor()

            query, params = adapt_sql("SELECT gotify_app_token FROM users WHERE id = %s", (user_id,))
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()

            return result[0] if result and result[0] else None

        except Exception as e:
            logger.error(f"Failed to get user app token for {user_id}: {e}")
            return None

    def _send_with_global_token(self, title: str, content: str, recipient: Dict[str, Any],
                               priority: int = 1, metadata: Dict[str, Any] = None) -> bool:
        """使用全局Token发送（标明接收者）"""
        try:
            url = f"{self.server_url}/message"

            # 在标题和内容中明确标识接收者
            recipient_name = recipient.get('name', '用户')
            marked_title = f"[{recipient_name}] {title}"
            marked_content = f"@{recipient_name}\n{content}"

            # 所有Gotify通知都使用最高优先级10
            gotify_priority = 10

            # 格式化内容为Markdown
            formatted_content = self._format_content_markdown(marked_content, metadata)

            data = {
                "title": marked_title,
                "message": formatted_content,
                "priority": gotify_priority
            }

            # 添加额外信息
            if metadata:
                data["extras"] = {
                    "client::display": {
                        "contentType": "text/markdown"
                    },
                    "rebugtracker": {
                        "event_type": metadata.get('event_type', ''),
                        "bug_id": metadata.get('bug_id', ''),
                        "timestamp": metadata.get('timestamp', ''),
                        "recipient_id": recipient.get('id', ''),
                        "global_token_used": True
                    }
                }

            headers = {
                "X-Gotify-Key": self.config['app_token'],  # 使用全局Token
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"Gotify notification sent to {recipient_name} (global token): {marked_title}")
                return True
            else:
                logger.error(f"Gotify API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Failed to send Gotify notification with global token: {str(e)}")
            return False
    
    def _format_content_markdown(self, content: str, metadata: Dict[str, Any]) -> str:
        """格式化内容为Markdown格式"""
        
        # 基本内容
        formatted = content
        
        # 添加链接
        if metadata and metadata.get('bug_id'):
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            bug_url = f"{base_url}/bug/{metadata['bug_id']}"
            formatted += f"\n\n[📋 查看详情]({bug_url})"
        
        # 添加时间戳
        if metadata and metadata.get('timestamp'):
            formatted += f"\n\n⏰ {metadata['timestamp']}"
        
        return formatted
    
    def test_connection(self) -> bool:
        """测试Gotify连接"""
        if not self.is_enabled():
            return False
        
        try:
            url = f"{self.server_url}/version"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                logger.info("Gotify connection test successful")
                return True
            else:
                logger.warning(f"Gotify connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Gotify connection test error: {e}")
            return False
