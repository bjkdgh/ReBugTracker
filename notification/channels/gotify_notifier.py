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
        self.config = {
            'enabled': os.getenv('GOTIFY_ENABLED', 'false').lower() == 'true',
            'server_url': os.getenv('GOTIFY_SERVER_URL', 'http://localhost:8080'),
            'app_token': os.getenv('GOTIFY_APP_TOKEN', ''),
            'default_priority': int(os.getenv('GOTIFY_DEFAULT_PRIORITY', '5')),
        }
        
        self.server_url = self.config['server_url'].rstrip('/')
        
        logger.debug(f"Gotify notifier initialized: enabled={self.config['enabled']}, "
                    f"server={self.server_url}")
    
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
            url = f"{self.server_url}/message"
            
            # 转换优先级 (1-4 -> 1-10)
            gotify_priority = min(max(priority * 2, 1), 10)
            
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
                "X-Gotify-Key": self.config['app_token'],
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Gotify notification sent to {recipient.get('name', 'unknown')}: {title}")
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
