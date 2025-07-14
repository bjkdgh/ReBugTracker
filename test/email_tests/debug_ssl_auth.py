#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试SSL认证问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_ssl_authentication():
    """调试SSL认证过程"""
    print("🔍 调试SSL认证过程...")
    print("=" * 50)
    
    try:
        import smtplib
        import ssl
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        # 获取配置
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
        
        smtp_server = config_dict.get('notification_email_smtp_server', 'smtp.163.com')
        smtp_port = int(config_dict.get('notification_email_smtp_port', '465'))
        smtp_username = config_dict.get('notification_email_smtp_username', '')
        smtp_password = config_dict.get('notification_email_smtp_password', '')
        
        print(f"📧 服务器: {smtp_server}")
        print(f"🔌 端口: {smtp_port}")
        print(f"👤 用户名: {smtp_username}")
        print(f"🔒 密码: {'已设置' if smtp_password else '未设置'}")
        
        print("\n🔗 开始详细调试...")
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 建立SSL连接
        print("1. 建立SSL连接...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30)
        
        # 启用详细调试
        server.set_debuglevel(2)
        
        print("2. 发送EHLO...")
        server.ehlo()
        
        print("3. 尝试登录...")
        try:
            server.login(smtp_username, smtp_password)
            print("   ✅ 登录成功！")
            
            # 尝试发送一封简单的测试邮件
            print("4. 发送测试邮件...")
            
            from email.mime.text import MIMEText
            from email.header import Header
            
            msg = MIMEText("这是一封SSL调试测试邮件", 'plain', 'utf-8')
            msg['Subject'] = Header('SSL调试测试', 'utf-8')
            msg['From'] = smtp_username
            msg['To'] = 'guoh202505@gmail.com'
            
            server.send_message(msg)
            print("   ✅ 邮件发送成功！")
            
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ 认证失败: {e}")
            print("   💡 可能的原因:")
            print("      - 163邮箱未开启SMTP服务")
            print("      - 使用的是登录密码而不是授权码")
            print("      - 授权码输入错误")
            
        except Exception as e:
            print(f"   ❌ 登录错误: {e}")
        
        finally:
            try:
                server.quit()
            except:
                pass
        
        conn.close()
        return False
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_163_smtp_requirements():
    """检查163邮箱SMTP要求"""
    print("\n📋 163邮箱SMTP设置要求...")
    print("=" * 50)
    
    print("🔧 163邮箱SMTP配置要求:")
    print("1. **开启SMTP服务**:")
    print("   - 登录163邮箱网页版")
    print("   - 设置 → POP3/SMTP/IMAP")
    print("   - 开启SMTP服务")
    print()
    print("2. **获取授权码**:")
    print("   - 在SMTP设置页面生成授权码")
    print("   - 使用授权码而不是登录密码")
    print("   - 授权码格式通常是16位字符")
    print()
    print("3. **正确的配置参数**:")
    print("   - 服务器: smtp.163.com")
    print("   - 端口: 465 (SSL)")
    print("   - 用户名: 完整邮箱地址")
    print("   - 密码: 授权码")
    print()
    print("4. **常见问题**:")
    print("   - 确保邮箱地址和用户名一致")
    print("   - 检查授权码是否正确复制")
    print("   - 确认SMTP服务已开启")

def suggest_next_steps():
    """建议下一步操作"""
    print("\n💡 建议的解决步骤...")
    print("=" * 50)
    
    print("🔧 请按以下步骤检查:")
    print()
    print("1. **验证163邮箱设置**:")
    print("   - 登录 mail.163.com")
    print("   - 进入 设置 → POP3/SMTP/IMAP")
    print("   - 确认SMTP服务状态为'已开启'")
    print()
    print("2. **重新生成授权码**:")
    print("   - 在SMTP设置页面点击'重新生成授权码'")
    print("   - 复制新的授权码")
    print("   - 在admin页面更新邮件密码配置")
    print()
    print("3. **测试配置**:")
    print("   - 保存新的授权码配置")
    print("   - 重新运行邮件测试")
    print()
    print("4. **备选方案**:")
    print("   - 考虑使用QQ邮箱 (smtp.qq.com:587)")
    print("   - 或使用企业邮箱服务")

def main():
    """主调试函数"""
    print("🚀 调试SSL邮件认证问题")
    print("📧 目标：找出认证失败的具体原因")
    print()
    
    # 调试认证过程
    auth_success = debug_ssl_authentication()
    
    # 显示163邮箱要求
    check_163_smtp_requirements()
    
    # 建议解决步骤
    suggest_next_steps()
    
    print("\n" + "=" * 50)
    print("📋 调试结果:")
    print(f"   SSL认证: {'✅ 成功' if auth_success else '❌ 失败'}")
    
    if auth_success:
        print("\n🎉 SSL认证成功！邮件功能应该正常工作了。")
    else:
        print("\n🔧 SSL认证失败，请按照上述建议检查163邮箱设置。")
        print("📝 重点检查：授权码是否正确设置")

if __name__ == "__main__":
    main()
