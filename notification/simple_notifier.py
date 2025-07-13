# -*- coding: utf-8 -*-
"""
简化通知处理器
专注于流转过程中的参与者通知
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

from .flow_rules import FlowNotificationRules
from .notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class SimpleNotifier:
    """简化通知处理器"""
    
    def __init__(self):
        from .channels.email_notifier import EmailNotifier
        from .channels.gotify_notifier import GotifyNotifier
        from .channels.inapp_notifier import InAppNotifier
        
        self.notifiers = {
            'email': EmailNotifier(),
            'gotify': GotifyNotifier(),
            'inapp': InAppNotifier()
        }
        
        logger.info("Simple notifier initialized with channels: email, gotify, inapp")
    
    def send_flow_notification(self, event_type: str, event_data: Dict[str, Any]):
        """发送流转通知"""
        try:
            # 检查服务器通知开关
            if not NotificationManager.is_notification_enabled():
                logger.info("Server notification is disabled, skipping notification")
                return
            
            # 获取通知目标
            target_user_ids = FlowNotificationRules.get_notification_targets(event_type, event_data)
            
            if not target_user_ids:
                logger.debug(f"No notification targets for event: {event_type}")
                return
            
            logger.info(f"Sending {event_type} notification to {len(target_user_ids)} users")
            
            # 为每个目标用户发送通知
            success_count = 0
            for user_id in target_user_ids:
                if self._send_to_user(event_type, event_data, user_id):
                    success_count += 1
            
            logger.info(f"Successfully sent notifications to {success_count}/{len(target_user_ids)} users")
                
        except Exception as e:
            logger.error(f"Error sending flow notification for {event_type}: {e}")
    
    def _send_to_user(self, event_type: str, event_data: Dict[str, Any], user_id: str) -> bool:
        """向单个用户发送通知"""
        try:
            # 获取用户信息
            user_info = self._get_user_info(user_id)
            if not user_info:
                logger.warning(f"User not found: {user_id}")
                return False
            
            # 检查用户通知开关
            user_preferences = NotificationManager.is_user_notification_enabled(user_id)
            
            # 生成通知内容
            content = self._generate_content(event_type, event_data, user_info)
            
            # 按渠道发送
            sent_any = False
            for channel, enabled in user_preferences.items():
                if enabled and channel in self.notifiers:
                    try:
                        success = self.notifiers[channel].send(
                            title=content['title'],
                            content=content['content'],
                            recipient=user_info,
                            priority=content['priority'],
                            metadata=content.get('metadata', {})
                        )
                        
                        if success:
                            sent_any = True
                            logger.debug(f"Sent {channel} notification to {user_info['name']}")
                        else:
                            logger.warning(f"Failed to send {channel} notification to {user_info['name']}")
                        
                    except Exception as e:
                        logger.error(f"Error sending {channel} notification to {user_id}: {e}")
            
            return sent_any
            
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {e}")
            return False
    
    def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        try:
            from db_factory import get_db_connection
            from sql_adapter import adapt_sql
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query, params = adapt_sql("""
                SELECT id, username, chinese_name, email, phone, role_en 
                FROM users WHERE id = %s
            """, (user_id,))
            
            cursor.execute(query, params)
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'name': user[2] or user[1],
                    'email': user[3],
                    'phone': user[4],
                    'role': user[5]
                }
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
        
        return None
    
    def _generate_content(self, event_type: str, event_data: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成通知内容"""
        templates = {
            "bug_created": {
                "title": "🆕 有新的提交问题",
                "content": "{creator_name}提交了新问题，请及时处理：\n\n📋 标题：{title}\n📝 描述：{description}\n👤 提交人：{creator_name}\n⏰ 时间：{created_time}",
                "priority": 2
            },
            "bug_assigned": {
                "title": "🔔 问题分配给您",
                "content": "您好 {user_name}，有问题分配给您：\n\n📋 标题：{title}\n📝 描述：{description}\n👤 分配人：{assigner_name}\n⏰ 时间：{assigned_time}",
                "priority": 3
            },
            "bug_status_changed": {
                "title": "🔄 问题状态更新",
                "content": "问题状态已更新：\n\n📋 标题：{title}\n📊 状态：{old_status} → {new_status}\n👤 操作人：{operator_name}\n⏰ 时间：{updated_time}",
                "priority": 1
            },
            "bug_resolved": {
                "title": "✅ 问题已解决",
                "content": "问题已解决：\n\n📋 标题：{title}\n💡 解决方案：{solution}\n👤 解决人：{resolver_name}\n⏰ 时间：{resolved_time}",
                "priority": 2
            },
            "bug_closed": {
                "title": "🎯 问题已关闭",
                "content": "问题已关闭：\n\n📋 标题：{title}\n📝 关闭原因：{close_reason}\n👤 关闭人：{closer_name}\n⏰ 时间：{closed_time}",
                "priority": 1
            }
        }
        
        template = templates.get(event_type, {
            "title": "📢 系统通知",
            "content": "您有新的系统通知，请查看。",
            "priority": 1
        })
        
        # 准备格式化数据
        format_data = {
            'user_name': user_info['name'],
            'title': event_data.get('title', ''),
            'description': self._truncate_text(event_data.get('description', ''), 100),
            'creator_name': event_data.get('creator_name', ''),
            'assigner_name': event_data.get('assigner_name', ''),
            'operator_name': event_data.get('operator_name', ''),
            'resolver_name': event_data.get('resolver_name', ''),
            'closer_name': event_data.get('closer_name', ''),
            'old_status': event_data.get('old_status', ''),
            'new_status': event_data.get('new_status', ''),
            'solution': self._truncate_text(event_data.get('solution', ''), 100),
            'close_reason': event_data.get('close_reason', ''),
            'created_time': self._format_time(event_data.get('created_time')),
            'assigned_time': self._format_time(event_data.get('assigned_time')),
            'updated_time': self._format_time(event_data.get('updated_time')),
            'resolved_time': self._format_time(event_data.get('resolved_time')),
            'closed_time': self._format_time(event_data.get('closed_time'))
        }
        
        try:
            return {
                'title': template['title'].format(**format_data),
                'content': template['content'].format(**format_data),
                'priority': template['priority'],
                'metadata': {
                    'event_type': event_type,
                    'bug_id': event_data.get('bug_id'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'priority': template['priority']
                }
            }
        except KeyError as e:
            logger.warning(f"Missing format key {e} for event {event_type}, using default content")
            return {
                'title': template['title'],
                'content': "您有新的通知，请查看系统。",
                'priority': template['priority'],
                'metadata': {
                    'event_type': event_type,
                    'bug_id': event_data.get('bug_id'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _format_time(self, time_str: str) -> str:
        """格式化时间"""
        if not time_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            if isinstance(time_str, str):
                # 尝试解析ISO格式
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        return str(time_str)

# 全局通知器实例
simple_notifier = SimpleNotifier()
