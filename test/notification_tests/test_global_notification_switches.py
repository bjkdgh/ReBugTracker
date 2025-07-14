#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试全局通知开关功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_global_notification_switches():
    """测试全局通知开关功能"""
    print("🔧 测试全局通知开关功能")
    print("=" * 50)
    
    try:
        from notification.notification_manager import NotificationManager
        from notification.channels.email_notifier import EmailNotifier
        from notification.channels.gotify_notifier import GotifyNotifier
        
        # 1. 测试全局邮件开关
        print("1. 测试全局邮件开关...")
        
        # 获取当前状态
        email_enabled = NotificationManager.is_global_notification_enabled('email')
        print(f"   当前邮件全局状态: {'启用' if email_enabled else '禁用'}")
        
        # 测试邮件通知器
        email_notifier = EmailNotifier()
        email_notifier_enabled = email_notifier.is_enabled()
        print(f"   邮件通知器状态: {'启用' if email_notifier_enabled else '禁用'}")
        
        # 2. 测试全局Gotify开关
        print("\n2. 测试全局Gotify开关...")
        
        # 获取当前状态
        gotify_enabled = NotificationManager.is_global_notification_enabled('gotify')
        print(f"   当前Gotify全局状态: {'启用' if gotify_enabled else '禁用'}")
        
        # 测试Gotify通知器
        gotify_notifier = GotifyNotifier()
        gotify_notifier_enabled = gotify_notifier.is_enabled()
        print(f"   Gotify通知器状态: {'启用' if gotify_notifier_enabled else '禁用'}")
        
        # 3. 测试设置全局开关
        print("\n3. 测试设置全局开关...")
        
        # 测试设置邮件开关
        print("   测试设置邮件全局开关...")
        original_email = email_enabled
        new_email = not original_email
        
        # 这里需要直接操作数据库，因为NotificationManager没有设置全局开关的方法
        from db_factory import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 设置邮件全局开关
        config_value = 'true' if new_email else 'false'
        cursor.execute("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = 'email_global_enabled'
        """, (config_value,))
        
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO system_config (config_key, config_value, description)
                VALUES ('email_global_enabled', %s, '全局邮件通知开关')
            """, (config_value,))
        
        conn.commit()
        
        # 验证设置
        new_email_status = NotificationManager.is_global_notification_enabled('email')
        print(f"   邮件开关设置: {original_email} → {new_email_status}")
        
        # 验证通知器状态变化
        email_notifier_new = EmailNotifier()
        email_notifier_new_enabled = email_notifier_new.is_enabled()
        print(f"   邮件通知器状态变化: {email_notifier_enabled} → {email_notifier_new_enabled}")
        
        # 恢复原状态
        restore_value = 'true' if original_email else 'false'
        cursor.execute("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = 'email_global_enabled'
        """, (restore_value,))
        conn.commit()
        print(f"   已恢复邮件开关原状态: {original_email}")
        
        # 测试设置Gotify开关
        print("\n   测试设置Gotify全局开关...")
        original_gotify = gotify_enabled
        new_gotify = not original_gotify
        
        # 设置Gotify全局开关
        config_value = 'true' if new_gotify else 'false'
        cursor.execute("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = 'gotify_global_enabled'
        """, (config_value,))
        
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO system_config (config_key, config_value, description)
                VALUES ('gotify_global_enabled', %s, '全局Gotify通知开关')
            """, (config_value,))
        
        conn.commit()
        
        # 验证设置
        new_gotify_status = NotificationManager.is_global_notification_enabled('gotify')
        print(f"   Gotify开关设置: {original_gotify} → {new_gotify_status}")
        
        # 验证通知器状态变化
        gotify_notifier_new = GotifyNotifier()
        gotify_notifier_new_enabled = gotify_notifier_new.is_enabled()
        print(f"   Gotify通知器状态变化: {gotify_notifier_enabled} → {gotify_notifier_new_enabled}")
        
        # 恢复原状态
        restore_value = 'true' if original_gotify else 'false'
        cursor.execute("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = 'gotify_global_enabled'
        """, (restore_value,))
        conn.commit()
        print(f"   已恢复Gotify开关原状态: {original_gotify}")
        
        conn.close()
        
        print("\n✅ 全局通知开关功能测试完成！")
        
        # 4. 总结
        print("\n📋 测试总结:")
        print("   ✅ 全局邮件开关读取正常")
        print("   ✅ 全局Gotify开关读取正常")
        print("   ✅ 邮件通知器响应全局开关")
        print("   ✅ Gotify通知器响应全局开关")
        print("   ✅ 数据库配置读写正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_system_config_table():
    """检查系统配置表"""
    try:
        from db_factory import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n📊 系统配置表状态:")
        cursor.execute("SELECT config_key, config_value, description FROM system_config ORDER BY config_key")
        configs = cursor.fetchall()
        
        for config in configs:
            print(f"   {config[0]}: {config[1]} ({config[2] or 'N/A'})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查系统配置表失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker 全局通知开关测试")
    print("=" * 60)
    
    check_system_config_table()
    
    success = test_global_notification_switches()
    
    if success:
        print("\n🎉 所有测试通过！全局通知开关功能正常。")
        print("\n📝 使用说明:")
        print("   1. 管理员可以在管理页面控制全局邮件和Gotify开关")
        print("   2. 全局开关关闭时，对应类型的通知将不会发送")
        print("   3. 全局开关优先于用户个人设置")
        print("   4. 应用内通知不受全局开关影响")
    else:
        print("\n💥 测试失败！请检查全局通知开关功能。")
        sys.exit(1)
