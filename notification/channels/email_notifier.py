# -*- coding: utf-8 -*-
"""
邮件通知器
负责发送邮件通知
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Dict, Any
import os

from .base import BaseNotifier

logger = logging.getLogger(__name__)

class EmailNotifier(BaseNotifier):
    """邮件通知器"""
    
    def __init__(self):
        self.config = {
            'enabled': os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'true').lower() == 'true',
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@rebugtracker.com'),
            'from_name': os.getenv('FROM_NAME', 'ReBugTracker'),
            'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
        }
        
        logger.debug(f"Email notifier initialized: enabled={self.config['enabled']}")
    
    def is_enabled(self) -> bool:
        """检查邮件通知是否启用"""
        # 检查全局邮件开关
        try:
            from notification.notification_manager import NotificationManager
            if not NotificationManager.is_global_notification_enabled('email'):
                return False
        except Exception as e:
            logger.error(f"Failed to check global email notification status: {e}")

        return self.config['enabled'] and bool(self.config['smtp_server'])
    
    def validate_recipient(self, recipient: Dict[str, Any]) -> bool:
        """验证接收者邮箱"""
        return super().validate_recipient(recipient) and bool(recipient.get('email'))
    
    def send(self, title: str, content: str, recipient: Dict[str, Any], 
             priority: int = 1, metadata: Dict[str, Any] = None) -> bool:
        """发送邮件通知"""
        
        if not self.is_enabled():
            logger.debug("Email notifications disabled")
            return False
        
        if not self.validate_recipient(recipient):
            logger.warning(f"Invalid recipient for email: {recipient}")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = recipient['email']
            msg['Subject'] = Header(title, 'utf-8')
            
            # 生成HTML和文本版本
            text_content = self._generate_text_content(title, content, metadata)
            html_content = self._generate_html_content(title, content, metadata)
            
            # 添加邮件内容
            msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config['use_tls']:
                    server.starttls()
                
                if self.config['username'] and self.config['password']:
                    server.login(self.config['username'], self.config['password'])
                
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipient['email']}: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.get('email', 'unknown')}: {str(e)}")
            return False
    
    def _generate_text_content(self, title: str, content: str, metadata: Dict[str, Any]) -> str:
        """生成文本版本邮件内容"""
        text = f"{title}\n{'=' * len(title)}\n\n{content}\n\n"
        
        if metadata and metadata.get('bug_id'):
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            text += f"查看详情: {base_url}/bug/{metadata['bug_id']}\n\n"
        
        text += "---\n此邮件由 ReBugTracker 系统自动发送，请勿回复。"
        return text
    
    def _generate_html_content(self, title: str, content: str, metadata: Dict[str, Any]) -> str:
        """生成HTML版本邮件内容"""
        
        # 处理内容中的换行
        formatted_content = content.replace('\n', '<br>')
        
        # 生成查看详情链接
        bug_link = ""
        if metadata and metadata.get('bug_id'):
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            bug_link = f'''
            <div style="margin: 20px 0;">
                <a href="{base_url}/bug/{metadata['bug_id']}" 
                   style="background-color: #007bff; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    查看详情
                </a>
            </div>
            '''
        
        # 优先级颜色
        priority_colors = {1: '#28a745', 2: '#ffc107', 3: '#fd7e14', 4: '#dc3545'}
        priority_color = priority_colors.get(metadata.get('priority', 1) if metadata else 1, '#007bff')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                     line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 20px auto; background-color: white; 
                        border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden;">
                
                <!-- Header -->
                <div style="background-color: {priority_color}; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: 600;">{title}</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; 
                                border-left: 4px solid {priority_color}; margin: 20px 0;">
                        {formatted_content}
                    </div>
                    
                    {bug_link}
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; 
                            border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 14px; margin: 0;">
                        此邮件由 <strong>ReBugTracker</strong> 系统自动发送，请勿回复。
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
