#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新邮件配置为SSL模式
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_email_config_to_ssl():
    """更新邮件配置为SSL模式"""
    print("🔧 更新邮件配置为SSL模式...")
    print("=" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新配置为SSL模式
        updates = [
            ('notification_email_smtp_port', '465'),
            ('notification_email_use_tls', 'false'),  # SSL模式不需要TLS
        ]
        
        print("📝 更新配置项:")
        for config_key, config_value in updates:
            print(f"   {config_key}: {config_value}")
            
            # 更新配置
            query, params = adapt_sql("""
                UPDATE system_config 
                SET config_value = %s, updated_at = CURRENT_TIMESTAMP
                WHERE config_key = %s
            """, (config_value, config_key))
            
            cursor.execute(query, params)
            
            if cursor.rowcount == 0:
                # 如果没有更新任何行，则插入新配置
                query, params = adapt_sql("""
                    INSERT INTO system_config (config_key, config_value, description)
                    VALUES (%s, %s, %s)
                """, (config_key, config_value, f'邮件配置 - {config_key}'))
                
                cursor.execute(query, params)
                print(f"   ✅ 插入新配置: {config_key}")
            else:
                print(f"   ✅ 更新配置: {config_key}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 邮件配置更新完成！")
        print("📧 新配置:")
        print("   - 端口: 465 (SSL)")
        print("   - 加密: SSL (不使用TLS)")
        print("   - 服务器: smtp.163.com")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")
        return False

def test_ssl_connection():
    """测试SSL连接"""
    print("\n🔍 测试SSL连接...")
    print("=" * 50)
    
    try:
        import smtplib
        import ssl
        
        smtp_server = "smtp.163.com"
        smtp_port = 465
        
        print(f"📧 服务器: {smtp_server}")
        print(f"🔌 端口: {smtp_port}")
        print(f"🔐 加密: SSL")
        
        print("\n🔗 开始SSL连接测试...")
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 创建SMTP_SSL连接
        print("   1. 建立SSL连接...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=15)
        print("   ✅ SSL连接成功")
        
        # 启用调试模式
        server.set_debuglevel(1)
        
        # 发送EHLO
        print("   2. 发送EHLO...")
        server.ehlo()
        print("   ✅ EHLO成功")
        
        print("   3. 跳过登录测试（避免密码验证）")
        
        server.quit()
        print("   ✅ SSL连接测试完成")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SSL连接失败: {e}")
        return False

def test_email_with_ssl():
    """使用SSL配置测试邮件发送"""
    print("\n📧 使用SSL配置测试邮件发送...")
    print("=" * 50)
    
    try:
        from notification.channels.email_notifier import EmailNotifier
        
        # 重新创建邮件通知器（使用新配置）
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
        
        print("\n3. 发送SSL测试邮件...")
        success = email_notifier.send(
            title="🔒 ReBugTracker SSL邮件测试",
            content=f"""您好 郭浩！

这是一封使用SSL(465端口)配置的测试邮件。

📋 当前配置信息：
- SMTP服务器: smtp.163.com
- 端口: 465
- 加密方式: SSL
- 发件人: bjkd_ssz@163.com

如果您收到这封邮件，说明SSL配置工作正常！

---
ReBugTracker 系统
测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            recipient=recipient_info,
            priority=1
        )
        
        if success:
            print("   ✅ SSL邮件发送成功！")
            return True
        else:
            print("   ❌ SSL邮件发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_final_config():
    """验证最终配置"""
    print("\n📋 验证最终配置...")
    print("=" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取邮件相关配置
        query, params = adapt_sql("""
            SELECT config_key, config_value FROM system_config 
            WHERE config_key LIKE %s
            ORDER BY config_key
        """, ('notification_email_%',))
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        print("📧 当前邮件配置:")
        for config in configs:
            key = config[0]
            value = config[1]
            
            # 隐藏密码
            if 'password' in key.lower():
                value = '*' * len(value) if value else '(未设置)'
            
            print(f"   {key}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证配置失败: {e}")

def main():
    """主函数"""
    print("🚀 更新邮件配置为SSL模式")
    print("📧 目标：修复163邮箱连接问题")
    print()
    
    # 1. 更新配置
    config_ok = update_email_config_to_ssl()
    
    if not config_ok:
        print("❌ 配置更新失败，停止测试")
        return
    
    # 2. 测试SSL连接
    ssl_ok = test_ssl_connection()
    
    # 3. 测试邮件发送
    email_ok = test_email_with_ssl()
    
    # 4. 验证最终配置
    verify_final_config()
    
    print("\n" + "=" * 50)
    print("📋 SSL配置测试结果:")
    print(f"   配置更新: {'✅ 成功' if config_ok else '❌ 失败'}")
    print(f"   SSL连接: {'✅ 正常' if ssl_ok else '❌ 有问题'}")
    print(f"   邮件发送: {'✅ 成功' if email_ok else '❌ 失败'}")
    
    if email_ok:
        print("\n🎉 SSL配置工作正常！")
        print("📧 请检查郭浩的邮箱: guoh202505@gmail.com")
        print("📁 注意检查垃圾邮件文件夹")
    else:
        print("\n🔧 如果仍有问题，请检查:")
        print("- 163邮箱是否开启了SMTP服务")
        print("- 是否使用了正确的授权码")
        print("- 网络防火墙是否阻止了465端口")

if __name__ == "__main__":
    main()
