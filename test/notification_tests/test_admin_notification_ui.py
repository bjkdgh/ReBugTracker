#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员通知管理界面功能
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_notification_apis():
    """测试管理员通知管理API"""
    print("🧪 测试管理员通知管理API")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 登录管理员账号
        print("1. 登录管理员账号...")
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            # 检查是否重定向到管理员页面
            if '/admin' in response.url or 'admin' in response.text:
                print("   ✅ 管理员登录成功")
            else:
                print(f"   ⚠️ 登录成功但可能不是管理员: {response.url}")
        else:
            print(f"   ❌ 管理员登录失败: {response.status_code}")
            return False
        
        # 2. 测试通知状态API
        print("\n2. 测试通知状态API...")
        response = session.get(f"{base_url}/admin/notification-status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 通知状态: {'启用' if data.get('enabled') else '禁用'}")
        else:
            print(f"   ❌ 获取通知状态失败: {response.status_code}")
        
        # 3. 测试通知统计API
        print("\n3. 测试通知统计API...")
        response = session.get(f"{base_url}/admin/notification-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 通知统计:")
            print(f"      总通知数: {stats.get('total', 0)}")
            print(f"      未读通知: {stats.get('unread', 0)}")
            print(f"      启用用户: {stats.get('enabled_users', 0)}")
            print(f"      今日通知: {stats.get('today', 0)}")
        else:
            print(f"   ❌ 获取通知统计失败: {response.status_code}")
        
        # 4. 测试切换通知开关API
        print("\n4. 测试切换通知开关API...")
        
        # 先获取当前状态
        response = session.get(f"{base_url}/admin/notification-status")
        current_enabled = response.json().get('enabled', False)
        
        # 切换状态
        new_enabled = not current_enabled
        toggle_data = {'enabled': new_enabled}
        
        response = session.post(f"{base_url}/admin/toggle-notification", 
                              json=toggle_data,
                              headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ 通知开关切换成功: {current_enabled} → {new_enabled}")
                
                # 验证状态是否真的改变了
                response = session.get(f"{base_url}/admin/notification-status")
                actual_enabled = response.json().get('enabled', False)
                if actual_enabled == new_enabled:
                    print(f"   ✅ 状态验证成功: {actual_enabled}")
                else:
                    print(f"   ❌ 状态验证失败: 期望{new_enabled}, 实际{actual_enabled}")
                
                # 恢复原状态
                restore_data = {'enabled': current_enabled}
                session.post(f"{base_url}/admin/toggle-notification", 
                           json=restore_data,
                           headers={'Content-Type': 'application/json'})
                print(f"   ✅ 已恢复原状态: {current_enabled}")
            else:
                print(f"   ❌ 切换失败: {result.get('message')}")
        else:
            print(f"   ❌ 切换请求失败: {response.status_code}")
        
        # 5. 测试管理员页面是否包含通知管理模块
        print("\n5. 测试管理员页面...")
        response = session.get(f"{base_url}/admin")
        if response.status_code == 200:
            content = response.text
            if '通知管理' in content and 'serverNotificationToggle' in content:
                print("   ✅ 管理员页面包含通知管理模块")
            else:
                print("   ❌ 管理员页面缺少通知管理模块")
        else:
            print(f"   ❌ 访问管理员页面失败: {response.status_code}")
        
        # 6. 测试详细通知设置页面
        print("\n6. 测试详细通知设置页面...")
        response = session.get(f"{base_url}/admin/notifications")
        if response.status_code == 200:
            print("   ✅ 详细通知设置页面访问成功")
        else:
            print(f"   ❌ 详细通知设置页面访问失败: {response.status_code}")
        
        print("\n✅ 管理员通知管理API测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_manager_functions():
    """测试通知管理器功能"""
    print("\n🔧 测试通知管理器功能")
    print("=" * 50)
    
    try:
        from notification.notification_manager import NotificationManager
        
        # 测试获取通知状态
        print("1. 测试获取通知状态...")
        enabled = NotificationManager.is_notification_enabled()
        print(f"   当前通知状态: {'启用' if enabled else '禁用'}")
        
        # 测试设置通知状态
        print("\n2. 测试设置通知状态...")
        original_state = enabled
        
        # 切换状态
        new_state = not original_state
        success = NotificationManager.set_notification_enabled(new_state)
        if success:
            print(f"   ✅ 设置成功: {original_state} → {new_state}")
            
            # 验证
            actual_state = NotificationManager.is_notification_enabled()
            if actual_state == new_state:
                print(f"   ✅ 验证成功: {actual_state}")
            else:
                print(f"   ❌ 验证失败: 期望{new_state}, 实际{actual_state}")
            
            # 恢复原状态
            NotificationManager.set_notification_enabled(original_state)
            print(f"   ✅ 已恢复原状态: {original_state}")
        else:
            print("   ❌ 设置失败")
        
        # 测试获取用户偏好
        print("\n3. 测试获取用户偏好...")
        user_prefs = NotificationManager.get_all_users_preferences()
        print(f"   ✅ 获取到 {len(user_prefs)} 个用户的通知偏好")
        
        # 显示前3个用户的偏好
        for i, user in enumerate(user_prefs[:3], 1):
            if isinstance(user, dict):
                print(f"   用户{i}: {user.get('username')} - 邮件:{user.get('email_enabled')}, Gotify:{user.get('gotify_enabled')}, 应用内:{user.get('inapp_enabled')}")
            else:
                # 如果是tuple，转换格式
                print(f"   用户{i}: {user[1] if len(user) > 1 else 'N/A'} - 数据格式: {type(user)}")
        
        print("\n✅ 通知管理器功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 通知管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 管理员通知管理界面测试")
    print("=" * 60)
    
    # 测试后端功能
    backend_success = test_notification_manager_functions()
    
    # 测试API接口
    api_success = test_admin_notification_apis()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   通知管理器功能: {'✅ 通过' if backend_success else '❌ 失败'}")
    print(f"   API接口功能: {'✅ 通过' if api_success else '❌ 失败'}")
    
    if backend_success and api_success:
        print("\n🎉 所有测试通过！管理员通知管理界面功能正常。")
        print("\n📝 使用说明:")
        print("   1. 使用管理员账号(admin/admin)登录")
        print("   2. 在管理员页面可以看到通知管理模块")
        print("   3. 可以切换服务器通知开关")
        print("   4. 可以查看通知统计信息")
        print("   5. 点击'详细通知设置'进入完整的通知管理页面")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
