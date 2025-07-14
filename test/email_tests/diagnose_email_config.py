#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断邮件配置问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_smtp_connection():
    """诊断SMTP连接"""
    print("🔍 诊断SMTP连接...")
    print("=" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        # 获取邮件配置
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query, params = adapt_sql("""
            SELECT config_key, config_value FROM system_config 
            WHERE config_key LIKE %s
        """, ('notification_email_%',))
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        config_dict = {}
        for config in configs:
            config_dict[config[0]] = config[1]
        
        smtp_server = config_dict.get('notification_email_smtp_server', '')
        smtp_port = int(config_dict.get('notification_email_smtp_port', '587'))
        smtp_username = config_dict.get('notification_email_smtp_username', '')
        smtp_password = config_dict.get('notification_email_smtp_password', '')
        use_tls = config_dict.get('notification_email_use_tls', 'true') == 'true'
        
        print(f"📧 SMTP服务器: {smtp_server}")
        print(f"🔌 端口: {smtp_port}")
        print(f"👤 用户名: {smtp_username}")
        print(f"🔒 密码: {'已设置' if smtp_password else '未设置'}")
        print(f"🔐 TLS: {'启用' if use_tls else '禁用'}")
        
        # 测试SMTP连接
        print("\n🔗 测试SMTP连接...")
        
        import smtplib
        import socket
        
        try:
            # 测试基本连接
            print(f"   连接到 {smtp_server}:{smtp_port}...")
            
            if smtp_port == 465:
                # SSL连接
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
                print("   ✅ SSL连接成功")
            else:
                # 普通连接后启用TLS
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
                print("   ✅ SMTP连接成功")
                
                if use_tls:
                    server.starttls()
                    print("   ✅ TLS启用成功")
            
            # 测试登录
            if smtp_username and smtp_password:
                print("   🔐 测试登录...")
                server.login(smtp_username, smtp_password)
                print("   ✅ 登录成功")
            else:
                print("   ⚠️ 未设置用户名或密码，跳过登录测试")
            
            server.quit()
            print("   ✅ SMTP连接测试完成")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ 认证失败: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            print(f"   ❌ 连接失败: {e}")
            return False
        except socket.timeout:
            print("   ❌ 连接超时")
            return False
        except Exception as e:
            print(f"   ❌ 连接错误: {e}")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        return False

def test_alternative_smtp_settings():
    """测试替代的SMTP设置"""
    print("\n🔄 测试替代SMTP设置...")
    print("=" * 50)
    
    # 163邮箱的不同配置选项
    smtp_configs = [
        {
            'name': '163邮箱 - SSL (465)',
            'server': 'smtp.163.com',
            'port': 465,
            'use_ssl': True,
            'use_tls': False
        },
        {
            'name': '163邮箱 - TLS (587)', 
            'server': 'smtp.163.com',
            'port': 587,
            'use_ssl': False,
            'use_tls': True
        },
        {
            'name': '163邮箱 - 标准 (25)',
            'server': 'smtp.163.com', 
            'port': 25,
            'use_ssl': False,
            'use_tls': False
        }
    ]
    
    import smtplib
    import socket
    
    for config in smtp_configs:
        print(f"\n📧 测试 {config['name']}...")
        try:
            if config['use_ssl']:
                server = smtplib.SMTP_SSL(config['server'], config['port'], timeout=5)
                print("   ✅ SSL连接成功")
            else:
                server = smtplib.SMTP(config['server'], config['port'], timeout=5)
                print("   ✅ SMTP连接成功")
                
                if config['use_tls']:
                    server.starttls()
                    print("   ✅ TLS启用成功")
            
            server.quit()
            print(f"   ✅ {config['name']} 连接正常")
            
        except Exception as e:
            print(f"   ❌ {config['name']} 连接失败: {e}")

def suggest_email_config_fix():
    """建议邮件配置修复方案"""
    print("\n💡 邮件配置修复建议...")
    print("=" * 50)
    
    print("🔧 可能的解决方案:")
    print()
    print("1. **检查163邮箱设置**:")
    print("   - 确保已开启SMTP服务")
    print("   - 使用授权码而不是登录密码")
    print("   - 登录163邮箱 → 设置 → POP3/SMTP/IMAP")
    print()
    print("2. **尝试不同的端口配置**:")
    print("   - SSL: smtp.163.com:465 (推荐)")
    print("   - TLS: smtp.163.com:587")
    print("   - 标准: smtp.163.com:25")
    print()
    print("3. **检查网络连接**:")
    print("   - 确保服务器可以访问外网")
    print("   - 检查防火墙设置")
    print("   - 尝试使用其他SMTP服务器")
    print()
    print("4. **验证用户名格式**:")
    print("   - 163邮箱用户名应该是完整邮箱地址")
    print("   - 例如: your_email@163.com")
    print()
    print("5. **测试其他邮箱服务**:")
    print("   - QQ邮箱: smtp.qq.com:587")
    print("   - Gmail: smtp.gmail.com:587")
    print("   - 企业邮箱等")

def main():
    """主诊断函数"""
    print("🚀 开始诊断邮件配置问题")
    print("📧 目标：修复发送给郭浩的邮件通知")
    print()
    
    # 诊断当前配置
    smtp_ok = diagnose_smtp_connection()
    
    # 测试替代配置
    test_alternative_smtp_settings()
    
    # 提供修复建议
    suggest_email_config_fix()
    
    print("\n" + "=" * 50)
    print("📋 诊断总结:")
    print(f"   当前SMTP配置: {'✅ 正常' if smtp_ok else '❌ 有问题'}")
    print()
    
    if not smtp_ok:
        print("🔧 建议操作:")
        print("1. 检查163邮箱的SMTP授权码设置")
        print("2. 尝试使用完整邮箱地址作为用户名")
        print("3. 在admin页面更新邮件配置")
        print("4. 重新测试邮件发送功能")

if __name__ == "__main__":
    main()
