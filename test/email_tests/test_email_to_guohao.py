#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试发送邮件通知给郭浩
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_email_notification_to_guohao():
    """测试发送邮件通知给郭浩"""
    print("🧪 测试发送邮件通知给郭浩...")
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

def test_flow_notification_to_guohao():
    """测试通过流程通知发送邮件给郭浩"""
    print("\n🔄 测试流程通知发送邮件给郭浩...")
    print("=" * 50)
    
    try:
        from notification.simple_notifier import simple_notifier
        
        # 模拟问题分配给郭浩的场景
        print("1. 模拟问题分配给郭浩...")
        
        simple_notifier.send_flow_notification('bug_assigned', {
            'bug_id': 9999,
            'title': '测试邮件通知功能',
            'description': '这是一个用于测试邮件通知功能的问题',
            'assignee_name': '郭浩',
            'assignee_id': '2',
            'assigned_time': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'manager_name': '系统管理员'
        })
        
        print("   ✅ 流程通知发送完成")
        print("   📧 请检查郭浩的邮箱是否收到问题分配通知")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 流程通知测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_email_config():
    """检查邮件配置"""
    print("\n⚙️ 检查邮件配置...")
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
        email_configs = cursor.fetchall()
        
        print("📧 邮件配置:")
        for config in email_configs:
            key = config[0]
            value = config[1]
            
            # 隐藏密码
            if 'password' in key.lower():
                value = '*' * len(value) if value else '(未设置)'
            
            print(f"   {key}: {value}")
        
        # 检查郭浩的通知偏好
        print("\n👤 郭浩的通知偏好:")
        query, params = adapt_sql("""
            SELECT email_enabled, gotify_enabled, inapp_enabled 
            FROM user_notification_preferences 
            WHERE user_id = %s
        """, ('2',))
        
        cursor.execute(query, params)
        prefs = cursor.fetchone()
        
        if prefs:
            print(f"   邮件通知: {'✅ 启用' if prefs[0] else '❌ 禁用'}")
            print(f"   Gotify通知: {'✅ 启用' if prefs[1] else '❌ 禁用'}")
            print(f"   应用内通知: {'✅ 启用' if prefs[2] else '❌ 禁用'}")
        else:
            print("   ⚠️ 未找到通知偏好设置（使用默认设置：全部启用）")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 检查配置失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试发送邮件通知给郭浩")
    print("📧 目标邮箱: guoh202505@gmail.com")
    print()
    
    # 检查配置
    check_email_config()
    
    # 测试直接邮件发送
    success1 = test_email_notification_to_guohao()
    
    # 测试流程通知
    success2 = test_flow_notification_to_guohao()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   直接邮件发送: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   流程通知发送: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 至少有一种方式发送成功！")
        print("📧 请检查郭浩的邮箱: guoh202505@gmail.com")
        print("📁 注意检查垃圾邮件文件夹")
    else:
        print("\n❌ 所有测试都失败了，请检查邮件配置")

if __name__ == "__main__":
    main()
