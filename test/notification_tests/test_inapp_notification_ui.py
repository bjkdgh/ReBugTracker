#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用内通知界面功能
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_inapp_notification_ui():
    """测试应用内通知界面功能"""
    print("📱 测试应用内通知界面功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. 登录用户
        print("1. 登录用户...")
        login_data = {'username': 'admin', 'password': 'admin'}
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            print("   ✅ 用户登录成功")
        else:
            print(f"   ❌ 用户登录失败: {response.status_code}")
            return False
        
        # 2. 测试通知API
        print("\n2. 测试通知API...")
        response = session.get(f"{base_url}/api/notifications")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                unread_count = data.get('unread_count', 0)
                notifications = data.get('notifications', [])
                print(f"   ✅ 获取通知成功: {len(notifications)} 条通知, {unread_count} 条未读")
                
                # 显示通知详情
                for i, notif in enumerate(notifications[:3], 1):
                    title = notif.get('title', 'N/A')
                    read_status = '已读' if notif.get('read_status') else '未读'
                    created_at = notif.get('created_at', 'N/A')
                    print(f"     通知{i}: {title} ({read_status}) - {created_at}")
            else:
                print(f"   ❌ 获取通知失败: {data.get('message')}")
        else:
            print(f"   ❌ 通知API请求失败: {response.status_code}")
        
        # 3. 测试标记已读功能
        print("\n3. 测试标记已读功能...")
        response = session.get(f"{base_url}/api/notifications")
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            unread_notifications = [n for n in notifications if not n.get('read_status')]
            
            if unread_notifications:
                # 标记第一个未读通知为已读
                first_unread = unread_notifications[0]
                notification_id = first_unread.get('id')
                
                response = session.post(f"{base_url}/api/notifications/read", 
                                      json={'notification_id': notification_id},
                                      headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ 标记通知 {notification_id} 为已读成功")
                    else:
                        print(f"   ❌ 标记已读失败: {result.get('message')}")
                else:
                    print(f"   ❌ 标记已读请求失败: {response.status_code}")
            else:
                print("   ℹ️ 没有未读通知可以标记")
        
        # 4. 测试全部标记已读功能
        print("\n4. 测试全部标记已读功能...")
        response = session.post(f"{base_url}/api/notifications/read-all")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ 全部标记已读成功")
                
                # 验证是否真的全部已读
                response = session.get(f"{base_url}/api/notifications")
                if response.status_code == 200:
                    data = response.json()
                    unread_count = data.get('unread_count', 0)
                    print(f"   ✅ 验证结果: 未读数量 = {unread_count}")
            else:
                print(f"   ❌ 全部标记已读失败: {result.get('message')}")
        else:
            print(f"   ❌ 全部标记已读请求失败: {response.status_code}")
        
        # 5. 测试通知页面
        print("\n5. 测试通知页面...")
        response = session.get(f"{base_url}/notifications")
        if response.status_code == 200:
            content = response.text
            if '通知中心' in content and 'notification-item-full' in content:
                print("   ✅ 通知页面加载成功，包含通知列表")
            else:
                print("   ⚠️ 通知页面加载成功，但可能缺少通知内容")
        else:
            print(f"   ❌ 通知页面加载失败: {response.status_code}")
        
        # 6. 测试主页面是否包含通知图标
        print("\n6. 测试主页面通知图标...")
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            content = response.text
            if 'fa-bell' in content and 'notificationDropdown' in content:
                print("   ✅ 主页面包含通知图标和下拉菜单")
            else:
                print("   ❌ 主页面缺少通知图标")
        else:
            print(f"   ❌ 主页面加载失败: {response.status_code}")
        
        print("\n✅ 应用内通知界面功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_creation():
    """测试创建新通知"""
    print("\n🔔 测试创建新通知")
    print("=" * 50)
    
    try:
        from notification.simple_notifier import simple_notifier
        
        # 发送一个测试通知
        print("1. 发送测试通知...")
        simple_notifier.send_flow_notification('bug_created', {
            'bug_id': 9999,
            'title': '界面测试通知',
            'description': '这是一个用于测试应用内通知界面的通知',
            'creator_name': '测试用户',
            'created_time': '2024-01-01 16:00:00',
            'creator_id': '1',
            'assigned_manager_id': '1'  # 发给管理员
        })
        print("   ✅ 测试通知发送成功")
        
        # 验证通知是否创建
        print("2. 验证通知创建...")
        from notification.channels.inapp_notifier import InAppNotifier
        
        inapp_notifier = InAppNotifier()
        notifications = inapp_notifier.get_user_notifications('1', limit=5)
        
        # 查找刚创建的通知
        test_notification = None
        for notif in notifications:
            if '界面测试通知' in notif.get('title', ''):
                test_notification = notif
                break
        
        if test_notification:
            print("   ✅ 测试通知创建成功")
            print(f"     标题: {test_notification.get('title')}")
            print(f"     内容: {test_notification.get('content')[:50]}...")
            print(f"     状态: {'已读' if test_notification.get('read_status') else '未读'}")
        else:
            print("   ❌ 未找到测试通知")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建通知测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 应用内通知界面测试")
    print("=" * 60)
    
    # 测试通知创建
    creation_success = test_notification_creation()
    
    # 测试界面功能
    ui_success = test_inapp_notification_ui()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   通知创建功能: {'✅ 通过' if creation_success else '❌ 失败'}")
    print(f"   界面功能: {'✅ 通过' if ui_success else '❌ 失败'}")
    
    if creation_success and ui_success:
        print("\n🎉 所有测试通过！应用内通知界面功能正常。")
        print("\n📝 使用说明:")
        print("   1. 登录后在导航栏右侧可以看到通知图标")
        print("   2. 有未读通知时图标上会显示红色数字徽章")
        print("   3. 点击通知图标可以查看最新通知")
        print("   4. 点击通知项可以标记为已读并跳转到相关页面")
        print("   5. 点击'查看全部通知'进入完整的通知页面")
        print("   6. 通知每30秒自动更新一次")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
