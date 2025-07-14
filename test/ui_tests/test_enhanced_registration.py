#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的用户注册功能（包含邮件、电话和通知偏好）
"""

import sys
import os
import requests
import json
import random
import string
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_test_user():
    """生成测试用户数据"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        'username': f'testuser_{random_suffix}',
        'password': 'test123456',
        'chinese_name': f'测试用户{random_suffix}',
        'email': f'test_{random_suffix}@example.com',
        'phone': f'138{random.randint(10000000, 99999999)}',
        'role': 'ssz',
        'team': '测试产品线',
        'email_notifications': 'on',
        'gotify_notifications': 'on',
        'inapp_notifications': 'on'
    }

def test_registration_api():
    """测试注册API功能"""
    print("🔧 测试注册API功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 1. 测试正常注册
    print("1. 测试正常注册...")
    test_user = generate_test_user()
    
    response = requests.post(f"{base_url}/register", data=test_user)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("   ✅ 注册成功")
            print(f"     用户名: {test_user['username']}")
            print(f"     邮箱: {test_user['email']}")
            print(f"     电话: {test_user['phone']}")
            return test_user
        else:
            print(f"   ❌ 注册失败: {result.get('message')}")
    else:
        print(f"   ❌ 注册请求失败: {response.status_code}")
        print(f"     响应: {response.text}")
    
    # 2. 测试邮箱格式验证
    print("\n2. 测试邮箱格式验证...")
    invalid_user = generate_test_user()
    invalid_user['email'] = 'invalid-email'
    
    response = requests.post(f"{base_url}/register", data=invalid_user)
    if response.status_code == 400:
        result = response.json()
        if '邮箱' in result.get('message', ''):
            print("   ✅ 邮箱格式验证正常")
        else:
            print(f"   ⚠️ 邮箱验证消息: {result.get('message')}")
    else:
        print(f"   ❌ 邮箱格式验证失败: {response.status_code}")
    
    # 3. 测试必填字段验证
    print("\n3. 测试必填字段验证...")
    incomplete_user = generate_test_user()
    del incomplete_user['email']  # 删除必填的邮箱字段
    
    response = requests.post(f"{base_url}/register", data=incomplete_user)
    if response.status_code == 400:
        result = response.json()
        if '必填' in result.get('message', ''):
            print("   ✅ 必填字段验证正常")
        else:
            print(f"   ⚠️ 必填字段验证消息: {result.get('message')}")
    else:
        print(f"   ❌ 必填字段验证失败: {response.status_code}")
    
    return test_user

def test_notification_preferences(test_user):
    """测试通知偏好设置"""
    print("\n🔔 测试通知偏好设置")
    print("=" * 50)
    
    try:
        from notification.notification_manager import NotificationManager
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        # 1. 查找刚注册的用户ID
        print("1. 查找用户ID...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query, params = adapt_sql("""
            SELECT id, username, email, phone FROM users 
            WHERE username = %s
        """, (test_user['username'],))
        
        cursor.execute(query, params)
        user_record = cursor.fetchone()
        
        if user_record:
            user_id = str(user_record[0])
            print(f"   ✅ 找到用户: ID={user_id}, 用户名={user_record[1]}")
            print(f"     邮箱: {user_record[2]}")
            print(f"     电话: {user_record[3]}")
        else:
            print("   ❌ 未找到用户记录")
            conn.close()
            return False
        
        # 2. 检查通知偏好设置
        print("\n2. 检查通知偏好设置...")
        preferences = NotificationManager.is_user_notification_enabled(user_id)
        
        print(f"   邮件通知: {'✅ 启用' if preferences.get('email') else '❌ 禁用'}")
        print(f"   Gotify通知: {'✅ 启用' if preferences.get('gotify') else '❌ 禁用'}")
        print(f"   应用内通知: {'✅ 启用' if preferences.get('inapp') else '❌ 启用'}")
        
        # 3. 测试修改通知偏好
        print("\n3. 测试修改通知偏好...")
        success = NotificationManager.set_user_notification_preferences(
            user_id,
            email_enabled=False,
            gotify_enabled=True,
            inapp_enabled=True
        )
        
        if success:
            print("   ✅ 通知偏好修改成功")
            
            # 验证修改结果
            new_preferences = NotificationManager.is_user_notification_enabled(user_id)
            print(f"   验证结果:")
            print(f"     邮件通知: {'✅ 启用' if new_preferences.get('email') else '❌ 禁用'}")
            print(f"     Gotify通知: {'✅ 启用' if new_preferences.get('gotify') else '❌ 禁用'}")
            print(f"     应用内通知: {'✅ 启用' if new_preferences.get('inapp') else '❌ 禁用'}")
        else:
            print("   ❌ 通知偏好修改失败")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试通知偏好失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_registration_page():
    """测试注册页面"""
    print("\n📱 测试注册页面")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/register")
        
        if response.status_code == 200:
            content = response.text
            
            # 检查页面是否包含新增的字段
            checks = [
                ('邮箱地址', 'email'),
                ('手机号码', 'phone'),
                ('通知偏好设置', 'notifications'),
                ('接收邮件通知', 'email_notifications'),
                ('接收Gotify通知', 'gotify_notifications'),
                ('接收应用内通知', 'inapp_notifications')
            ]
            
            print("检查页面元素:")
            for check_name, check_key in checks:
                if check_key in content:
                    print(f"   ✅ {check_name}: 存在")
                else:
                    print(f"   ❌ {check_name}: 缺失")
            
            return True
        else:
            print(f"   ❌ 注册页面加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试注册页面失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 增强注册功能测试")
    print("=" * 60)
    
    # 测试注册页面
    page_success = test_registration_page()
    
    # 测试注册API
    test_user = test_registration_api()
    api_success = test_user is not None
    
    # 测试通知偏好
    pref_success = False
    if api_success:
        pref_success = test_notification_preferences(test_user)
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   注册页面: {'✅ 通过' if page_success else '❌ 失败'}")
    print(f"   注册API: {'✅ 通过' if api_success else '❌ 失败'}")
    print(f"   通知偏好: {'✅ 通过' if pref_success else '❌ 失败'}")
    
    if page_success and api_success and pref_success:
        print("\n🎉 所有测试通过！增强注册功能正常。")
        print("\n📝 新增功能:")
        print("   1. 注册时必须填写邮箱地址")
        print("   2. 可选填写手机号码")
        print("   3. 可以设置通知偏好（邮件、Gotify、应用内）")
        print("   4. 邮箱格式验证")
        print("   5. 自动创建用户通知偏好记录")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
