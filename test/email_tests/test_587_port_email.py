#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试587端口的邮件发送
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_587_smtp_connection():
    """测试587端口SMTP连接"""
    print("🔍 测试587端口SMTP连接...")
    print("=" * 50)
    
    try:
        import smtplib
        import socket
        
        # 当前配置
        smtp_server = "smtp.163.com"
        smtp_port = 587
        smtp_username = "bjkd_ssz@163.com"
        
        print(f"📧 服务器: {smtp_server}")
        print(f"🔌 端口: {smtp_port}")
        print(f"👤 用户名: {smtp_username}")
        print(f"🔐 加密: TLS")
        
        print("\n🔗 开始连接测试...")
        
        # 创建SMTP连接
        print("   1. 建立SMTP连接...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
        print("   ✅ SMTP连接成功")
        
        # 启用调试模式
        server.set_debuglevel(1)
        
        # 发送EHLO
        print("   2. 发送EHLO...")
        server.ehlo()
        print("   ✅ EHLO成功")
        
        # 启用TLS
        print("   3. 启用TLS...")
        server.starttls()
        print("   ✅ TLS启用成功")
        
        # 再次EHLO（TLS后需要重新EHLO）
        print("   4. TLS后重新EHLO...")
        server.ehlo()
        print("   ✅ TLS后EHLO成功")
        
        print("   5. 测试登录...")
        # 这里不进行实际登录，避免密码问题
        print("   ⚠️ 跳过登录测试（避免密码验证）")
        
        server.quit()
        print("   ✅ 连接测试完成")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

def test_email_with_current_config():
    """使用当前配置测试邮件发送"""
    print("\n📧 使用当前配置测试邮件发送...")
    print("=" * 50)
    
    try:
        from notification.channels.email_notifier import EmailNotifier
        
        # 创建邮件通知器
        email_notifier = EmailNotifier()
        
        print("1. 检查邮件通知器状态...")
        is_enabled = email_notifier.is_enabled()
        print(f"   状态: {'✅ 启用' if is_enabled else '❌ 禁用'}")
        
        if not is_enabled:
            print("   ❌ 邮件通知器未启用")
            return False
        
        print("\n2. 准备测试邮件...")
        recipient_info = {
            'id': '2',
            'name': '郭浩',
            'email': 'guoh202505@gmail.com'
        }
        
        print(f"   收件人: {recipient_info['name']}")
        print(f"   邮箱: {recipient_info['email']}")
        
        print("\n3. 发送测试邮件...")
        success = email_notifier.send(
            title="🧪 ReBugTracker邮件测试 (587端口)",
            content=f"""您好 郭浩！

这是一封使用587端口+TLS配置的测试邮件。

📋 当前配置信息：
- SMTP服务器: smtp.163.com
- 端口: 587
- 加密方式: TLS
- 发件人: bjkd_ssz@163.com

如果您收到这封邮件，说明587端口配置工作正常！

---
ReBugTracker 系统
测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            recipient=recipient_info,
            priority=1
        )
        
        if success:
            print("   ✅ 邮件发送成功！")
            return True
        else:
            print("   ❌ 邮件发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_network_connectivity():
    """检查网络连通性"""
    print("\n🌐 检查网络连通性...")
    print("=" * 50)
    
    import socket
    
    # 测试DNS解析
    try:
        print("1. 测试DNS解析...")
        ip = socket.gethostbyname('smtp.163.com')
        print(f"   ✅ smtp.163.com 解析为: {ip}")
    except Exception as e:
        print(f"   ❌ DNS解析失败: {e}")
        return False
    
    # 测试端口连通性
    try:
        print("2. 测试端口连通性...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.163.com', 587))
        sock.close()
        
        if result == 0:
            print("   ✅ 587端口连通")
            return True
        else:
            print(f"   ❌ 587端口不通 (错误码: {result})")
            return False
            
    except Exception as e:
        print(f"   ❌ 端口测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 测试587端口邮件配置")
    print("📧 目标：验证当前587端口+TLS配置")
    print()
    
    # 检查网络连通性
    network_ok = check_network_connectivity()
    
    # 测试SMTP连接
    smtp_ok = test_587_smtp_connection()
    
    # 测试实际邮件发送
    email_ok = test_email_with_current_config()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   网络连通性: {'✅ 正常' if network_ok else '❌ 有问题'}")
    print(f"   SMTP连接: {'✅ 正常' if smtp_ok else '❌ 有问题'}")
    print(f"   邮件发送: {'✅ 成功' if email_ok else '❌ 失败'}")
    
    if email_ok:
        print("\n🎉 587端口配置工作正常！")
        print("📧 请检查郭浩的邮箱: guoh202505@gmail.com")
    else:
        print("\n🔧 可能的问题:")
        if not network_ok:
            print("- 网络连接问题")
        if not smtp_ok:
            print("- SMTP服务器连接问题")
        print("- 163邮箱授权码可能有误")
        print("- 需要检查163邮箱的SMTP服务设置")

if __name__ == "__main__":
    main()
