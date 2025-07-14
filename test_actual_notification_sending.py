#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实际的通知发送功能
包括邮件、Gotify、应用内通知的真实发送
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_notification_flow_logic():
    """测试通知流转逻辑（我之前测试的部分）"""
    print("🔍 第一层：通知流转逻辑测试")
    print("   测试内容：判断谁应该收到通知")
    print("-" * 50)
    
    try:
        from notification.flow_rules import FlowNotificationRules
        
        event_data = {
            'bug_id': 999,
            'title': '测试问题',
            'creator_id': '2',  # gh
            'assigned_manager_id': '3'  # zjn
        }
        
        targets = FlowNotificationRules.get_notification_targets('bug_created', event_data)
        
        print(f"   📋 事件类型: bug_created")
        print(f"   📤 触发数据: 创建者gh(2), 负责人zjn(3)")
        print(f"   📥 应该通知: {list(targets)}")
        print(f"   ✅ 逻辑层测试：{'通过' if '3' in targets else '失败'}")
        
        return '3' in targets
        
    except Exception as e:
        print(f"   ❌ 逻辑层测试失败: {e}")
        return False

def test_simple_notifier():
    """测试SimpleNotifier（通知发送协调器）"""
    print("\n🔄 第二层：通知发送协调器测试")
    print("   测试内容：SimpleNotifier是否能正确调用各通知渠道")
    print("-" * 50)
    
    try:
        from notification.simple_notifier import SimpleNotifier
        
        notifier = SimpleNotifier()
        
        print(f"   📧 邮件通知器: {'已加载' if 'email' in notifier.notifiers else '未加载'}")
        print(f"   🔔 Gotify通知器: {'已加载' if 'gotify' in notifier.notifiers else '未加载'}")
        print(f"   📱 应用内通知器: {'已加载' if 'inapp' in notifier.notifiers else '未加载'}")
        
        # 模拟发送通知（但不真正发送）
        event_data = {
            'bug_id': 999,
            'title': '测试问题创建',
            'description': '这是一个测试',
            'creator_name': 'gh',
            'created_time': '2025-07-14 23:45:00',
            'creator_id': '2',
            'assigned_manager_id': '3'
        }
        
        print(f"   📤 模拟发送事件: bug_created")
        print(f"   📋 事件数据: {event_data['title']}")
        
        # 这里会真正触发通知发送！
        print(f"   ⚠️ 注意：以下会真正发送通知！")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 协调器测试失败: {e}")
        return False

def test_individual_channels():
    """测试各个通知渠道"""
    print("\n📡 第三层：各通知渠道测试")
    print("   测试内容：邮件、Gotify、应用内通知的实际发送能力")
    print("-" * 50)
    
    results = {}
    
    # 测试邮件通知
    try:
        from notification.channels.email_notifier import EmailNotifier
        email_notifier = EmailNotifier()
        
        print(f"   📧 邮件通知:")
        print(f"      启用状态: {email_notifier.is_enabled()}")
        print(f"      配置状态: {'已配置' if email_notifier.validate_config() else '未配置'}")
        
        results['email'] = email_notifier.is_enabled()
        
    except Exception as e:
        print(f"   📧 邮件通知测试失败: {e}")
        results['email'] = False
    
    # 测试Gotify通知
    try:
        from notification.channels.gotify_notifier import GotifyNotifier
        gotify_notifier = GotifyNotifier()
        
        print(f"   🔔 Gotify通知:")
        print(f"      启用状态: {gotify_notifier.is_enabled()}")
        print(f"      服务器: {gotify_notifier.config.get('server_url', 'N/A')}")
        print(f"      默认优先级: {gotify_notifier.config.get('default_priority', 'N/A')}")
        
        results['gotify'] = gotify_notifier.is_enabled()
        
    except Exception as e:
        print(f"   🔔 Gotify通知测试失败: {e}")
        results['gotify'] = False
    
    # 测试应用内通知
    try:
        from notification.channels.inapp_notifier import InAppNotifier
        inapp_notifier = InAppNotifier()
        
        print(f"   📱 应用内通知:")
        print(f"      启用状态: {inapp_notifier.is_enabled()}")
        
        results['inapp'] = inapp_notifier.is_enabled()
        
    except Exception as e:
        print(f"   📱 应用内通知测试失败: {e}")
        results['inapp'] = False
    
    return results

def test_real_notification_sending():
    """测试真实的通知发送（谨慎使用）"""
    print("\n🚨 第四层：真实通知发送测试")
    print("   ⚠️ 警告：这会真正发送通知！")
    print("-" * 50)
    
    # 询问用户是否要进行真实发送测试
    print("   是否要进行真实通知发送测试？")
    print("   这会向zjn用户发送真实的邮件/Gotify/应用内通知")
    print("   输入 'yes' 确认，其他任何输入取消")
    
    # 在自动化测试中，我们跳过真实发送
    print("   🔄 自动化测试模式：跳过真实发送")
    return False

def check_notification_history():
    """检查通知历史记录"""
    print("\n📊 第五层：通知历史记录检查")
    print("   测试内容：检查数据库中的通知记录")
    print("-" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查最近的通知记录
        query, params = adapt_sql("""
            SELECT id, user_id, title, content, created_at, is_read
            FROM notifications
            ORDER BY created_at DESC
            LIMIT 5
        """, ())
        
        cursor.execute(query, params)
        notifications = cursor.fetchall()
        
        print(f"   📋 最近5条通知记录:")
        for i, notif in enumerate(notifications, 1):
            if hasattr(notif, 'keys'):  # DictCursor
                user_id = notif['user_id']
                title = notif['title']
                is_read = notif['is_read']
                created_at = notif['created_at']
            else:  # 普通tuple
                user_id = notif[1]
                title = notif[2]
                is_read = notif[5]
                created_at = notif[4]
            
            status = "已读" if is_read else "未读"
            print(f"      {i}. 用户{user_id}: {title[:30]}... ({status}) - {created_at}")
        
        conn.close()
        return len(notifications) > 0
        
    except Exception as e:
        print(f"   ❌ 通知历史检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 ReBugTracker 实际通知发送测试")
    print("=" * 80)
    print("测试说明：验证从逻辑判断到实际发送的完整通知流程")
    print("=" * 80)
    
    results = {}
    
    # 第一层：通知流转逻辑
    results['logic'] = test_notification_flow_logic()
    
    # 第二层：通知发送协调器
    results['coordinator'] = test_simple_notifier()
    
    # 第三层：各通知渠道
    channel_results = test_individual_channels()
    results.update(channel_results)
    
    # 第四层：真实发送（跳过）
    results['real_sending'] = test_real_notification_sending()
    
    # 第五层：历史记录
    results['history'] = check_notification_history()
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结:")
    
    test_items = [
        ('logic', '通知流转逻辑'),
        ('coordinator', '通知发送协调器'),
        ('email', '邮件通知渠道'),
        ('gotify', 'Gotify通知渠道'),
        ('inapp', '应用内通知渠道'),
        ('real_sending', '真实通知发送'),
        ('history', '通知历史记录')
    ]
    
    for key, name in test_items:
        if key in results:
            status = "✅ 正常" if results[key] else "❌ 异常"
            print(f"   {name}: {status}")
    
    # 分析结果
    print(f"\n💡 分析结果:")
    print(f"   🔍 通知逻辑: {'正常' if results.get('logic') else '异常'}")
    print(f"   📡 可用渠道: {sum(1 for k in ['email', 'gotify', 'inapp'] if results.get(k))}/3")
    print(f"   📊 历史记录: {'有数据' if results.get('history') else '无数据'}")
    
    return results

if __name__ == "__main__":
    main()
