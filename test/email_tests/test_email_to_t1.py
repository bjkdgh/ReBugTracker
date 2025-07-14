#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试发送邮件通知给t1用户
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_email_config():
    """检查邮件配置"""
    print("📧 检查邮件配置...")
    print("=" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取邮件配置
        query, params = adapt_sql("""
            SELECT config_key, config_value, description 
            FROM system_config 
            WHERE config_key LIKE 'notification_email_%'
            ORDER BY config_key
        """, ())
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        conn.close()
        
        if configs:
            print("当前邮件配置:")
            config_dict = {}
            for config in configs:
                key = config[0]
                value = config[1]
                desc = config[2]
                config_dict[key] = value
                
                # 隐藏密码
                display_value = value
                if 'password' in key.lower():
                    display_value = '***已设置***' if value else '未设置'
                
                print(f"   {key}: {display_value}")
                if desc:
                    print(f"     说明: {desc}")
        
        smtp_server = config_dict.get('notification_email_smtp_server', '')
        smtp_port = int(config_dict.get('notification_email_smtp_port', '587'))
        smtp_username = config_dict.get('notification_email_smtp_username', '')
        smtp_password = config_dict.get('notification_email_smtp_password', '')
        use_tls = config_dict.get('notification_email_use_tls', 'true') == 'true'
        
        print(f"\n📧 SMTP服务器: {smtp_server}")
        print(f"🔌 端口: {smtp_port}")
        print(f"👤 用户名: {smtp_username}")
        print(f"🔒 密码: {'已设置' if smtp_password else '未设置'}")
        print(f"🔐 TLS: {'启用' if use_tls else '禁用'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查配置失败: {e}")
        return False

def test_email_notification_to_t1():
    """测试发送邮件通知给t1用户"""
    print("\n🧪 测试发送邮件通知给t1用户...")
    print("=" * 50)
    
    try:
        # 1. 检查邮件通知器状态
        print("1. 检查邮件通知器状态...")
        from notification.channels.email_notifier import EmailNotifier
        
        email_notifier = EmailNotifier()
        is_enabled = email_notifier.is_enabled()
        
        print(f"   邮件通知器状态: {'✅ 启用' if is_enabled else '❌ 禁用'}")
        
        if not is_enabled:
            print("   ⚠️ 邮件通知器未启用，请检查配置")
            return False
        
        # 2. 准备t1用户的收件人信息
        print("\n2. 准备收件人信息...")
        recipient_info = {
            'id': '27',
            'name': 't1',
            'email': '237038603@qq.com'
        }
        
        print(f"   收件人: {recipient_info['name']}")
        print(f"   邮箱: {recipient_info['email']}")
        
        # 3. 发送测试邮件
        print("\n3. 发送测试邮件...")
        
        success = email_notifier.send(
            title="🧪 ReBugTracker邮件通知测试",
            content="""您好 t1！

这是一封来自ReBugTracker系统的测试邮件。

📋 测试内容：
- 邮件通知功能正常工作
- 您的邮箱配置正确
- 系统可以向您发送问题相关通知

🔔 通知类型包括：
- 问题分配通知
- 状态变更通知  
- 问题解决通知
- 问题关闭通知

如果您收到这封邮件，说明邮件通知功能运行正常。

---
ReBugTracker 系统
测试时间: {current_time}""".format(
                current_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ),
            recipient=recipient_info,
            priority=1,
            metadata={'test_type': 'email_notification', 'user_id': '27'}
        )
        
        if success:
            print("   ✅ 邮件发送成功！")
            print("   📧 请检查t1的邮箱: 237038603@qq.com")
            return True
        else:
            print("   ❌ 邮件发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flow_notification_to_t1():
    """测试通过流程管理器发送通知给t1用户"""
    print("\n🔄 测试流程通知发送给t1用户...")
    print("=" * 50)
    
    try:
        from notification.notification_manager import NotificationManager
        
        # 1. 创建通知管理器
        print("1. 创建通知管理器...")
        notification_manager = NotificationManager()
        
        # 2. 发送测试通知
        print("2. 发送测试通知...")
        
        success = notification_manager.send_notification(
            user_id='27',
            title='🧪 ReBugTracker流程通知测试',
            content='这是一封通过流程管理器发送的测试邮件，用于验证通知系统的完整性。',
            notification_type='test',
            priority=1,
            metadata={
                'test_type': 'flow_notification',
                'user_id': '27',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
        )
        
        if success:
            print("   ✅ 流程通知发送成功！")
            return True
        else:
            print("   ❌ 流程通知发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试发送邮件通知给t1用户")
    print("📧 目标邮箱: 237038603@qq.com")
    print()
    
    # 检查配置
    check_email_config()
    
    # 测试直接邮件发送
    success1 = test_email_notification_to_t1()
    
    # 测试流程通知
    success2 = test_flow_notification_to_t1()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   直接邮件发送: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   流程通知发送: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 至少有一种方式发送成功！")
        print("📧 请检查t1的邮箱: 237038603@qq.com")
        print("📁 注意检查垃圾邮件文件夹")
    else:
        print("\n❌ 所有测试都失败了，请检查邮件配置")

if __name__ == "__main__":
    main()
