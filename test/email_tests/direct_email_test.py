#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接邮件测试 - 不依赖复杂的导入
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def test_direct_email():
    """直接发送邮件测试"""
    print("🧪 直接邮件测试")
    print("📧 目标邮箱: 237038603@qq.com")
    print("=" * 50)
    
    # 邮件配置（使用163邮箱）
    smtp_server = "smtp.163.com"
    smtp_port = 587
    smtp_username = "bjkd_ssz@163.com"
    smtp_password = "IXQJQJQJQJQJ"  # 这里需要实际的授权码
    from_email = "bjkd_ssz@163.com"
    from_name = "ReBugTracker"
    
    # 收件人信息
    to_email = "237038603@qq.com"
    to_name = "t1"
    
    try:
        print("1. 创建邮件内容...")
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = Header("🧪 ReBugTracker直接邮件测试", 'utf-8')
        
        # 邮件内容
        content = f"""您好 {to_name}！

这是一封直接发送的测试邮件。

📧 测试信息：
- 发件人: {from_email}
- 收件人: {to_email}
- SMTP服务器: {smtp_server}
- 端口: {smtp_port}

如果您收到这封邮件，说明邮件发送功能正常！

---
ReBugTracker 系统
测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        # 添加文本内容
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        print("2. 连接SMTP服务器...")
        print(f"   服务器: {smtp_server}:{smtp_port}")
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("3. 启用TLS...")
            server.starttls()
            
            print("4. 登录邮箱...")
            server.login(smtp_username, smtp_password)
            
            print("5. 发送邮件...")
            server.send_message(msg)
        
        print("   ✅ 邮件发送成功！")
        print(f"   📧 请检查邮箱: {to_email}")
        print("   📁 如果收件箱没有，请检查垃圾邮件文件夹")
        return True
        
    except Exception as e:
        print(f"   ❌ 邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_email()
