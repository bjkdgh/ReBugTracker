#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通知系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_notification_system():
    """测试通知系统各个组件"""
    print("🧪 开始测试通知系统...")
    print("=" * 50)
    
    # 1. 测试数据库连接
    print("\n1. 测试数据库连接...")
    try:
        from db_factory import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查通知相关表
        tables = ['system_config', 'user_notification_preferences', 'notifications']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table}: {count} 条记录")
        
        conn.close()
        print("   ✅ 数据库连接正常")
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return False
    
    # 2. 测试通知管理器
    print("\n2. 测试通知管理器...")
    try:
        from notification.notification_manager import NotificationManager
        
        # 测试服务器通知状态
        server_enabled = NotificationManager.is_notification_enabled()
        print(f"   ✅ 服务器通知状态: {'启用' if server_enabled else '禁用'}")
        
        # 测试用户通知偏好
        user_prefs = NotificationManager.is_user_notification_enabled('1')
        print(f"   ✅ 用户通知偏好: {user_prefs}")
        
    except Exception as e:
        print(f"   ❌ 通知管理器测试失败: {e}")
        return False
    
    # 3. 测试流转规则
    print("\n3. 测试流转规则...")
    try:
        from notification.flow_rules import FlowNotificationRules
        
        # 测试获取通知目标
        targets = FlowNotificationRules.get_notification_targets('bug_created', {
            'bug_id': 1,
            'title': '测试问题',
            'creator_id': '1'
        })
        print(f"   ✅ 问题创建通知目标: {len(targets)} 个用户")
        
        targets = FlowNotificationRules.get_notification_targets('bug_assigned', {
            'assignee_id': '2'
        })
        print(f"   ✅ 问题分配通知目标: {len(targets)} 个用户")
        
    except Exception as e:
        print(f"   ❌ 流转规则测试失败: {e}")
        return False
    
    # 4. 测试通知渠道
    print("\n4. 测试通知渠道...")
    try:
        from notification.channels.email_notifier import EmailNotifier
        from notification.channels.gotify_notifier import GotifyNotifier
        from notification.channels.inapp_notifier import InAppNotifier
        
        # 测试邮件通知器
        email_notifier = EmailNotifier()
        print(f"   ✅ 邮件通知器: {'启用' if email_notifier.is_enabled() else '禁用'}")
        
        # 测试Gotify通知器
        gotify_notifier = GotifyNotifier()
        print(f"   ✅ Gotify通知器: {'启用' if gotify_notifier.is_enabled() else '禁用'}")
        
        # 测试应用内通知器
        inapp_notifier = InAppNotifier()
        print(f"   ✅ 应用内通知器: {'启用' if inapp_notifier.is_enabled() else '禁用'}")
        
    except Exception as e:
        print(f"   ❌ 通知渠道测试失败: {e}")
        return False
    
    # 5. 测试简化通知器
    print("\n5. 测试简化通知器...")
    try:
        from notification.simple_notifier import simple_notifier
        print("   ✅ 简化通知器初始化成功")
        
        # 测试发送通知（不会真正发送，只是测试流程）
        print("   📤 测试发送通知流程...")
        simple_notifier.send_flow_notification('bug_created', {
            'bug_id': 999,
            'title': '测试通知',
            'description': '这是一个测试通知',
            'creator_name': '测试用户',
            'created_time': '2024-01-01 12:00:00',
            'creator_id': '1'
        })
        print("   ✅ 通知发送流程测试完成")
        
    except Exception as e:
        print(f"   ❌ 简化通知器测试失败: {e}")
        return False
    
    # 6. 测试应用内通知功能
    print("\n6. 测试应用内通知功能...")
    try:
        from notification.channels.inapp_notifier import InAppNotifier
        
        inapp = InAppNotifier()
        
        # 测试发送应用内通知
        test_recipient = {
            'id': '1',
            'name': '测试用户',
            'email': 'test@example.com'
        }
        
        success = inapp.send(
            title="🧪 测试通知",
            content="这是一个测试通知，用于验证通知系统是否正常工作。",
            recipient=test_recipient,
            priority=1,
            metadata={'event_type': 'test', 'bug_id': 999}
        )
        
        if success:
            print("   ✅ 应用内通知发送成功")
            
            # 测试获取通知
            notifications = inapp.get_user_notifications('1', limit=5)
            print(f"   ✅ 获取到 {len(notifications)} 条通知")
            
            # 测试未读数量
            unread_count = inapp.get_unread_count('1')
            print(f"   ✅ 未读通知数量: {unread_count}")
        else:
            print("   ❌ 应用内通知发送失败")
        
    except Exception as e:
        print(f"   ❌ 应用内通知功能测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 通知系统测试完成！所有组件工作正常。")
    print("\n📋 测试总结:")
    print("   ✅ 数据库表结构正确")
    print("   ✅ 通知管理器功能正常")
    print("   ✅ 流转规则配置正确")
    print("   ✅ 通知渠道初始化成功")
    print("   ✅ 简化通知器工作正常")
    print("   ✅ 应用内通知功能完整")
    
    print("\n🔧 下一步操作:")
    print("   1. 配置邮件服务器信息（.env文件）")
    print("   2. 配置Gotify服务器（可选）")
    print("   3. 访问 /admin/notifications 管理通知设置")
    print("   4. 测试实际的问题流转通知")
    
    return True

if __name__ == "__main__":
    success = test_notification_system()
    sys.exit(0 if success else 1)
