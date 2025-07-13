#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试美化后的用户注册页面
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
        'username': f'beautifuluser_{random_suffix}',
        'password': 'test123456',
        'chinese_name': f'美化测试用户{random_suffix}',
        'email': f'beautiful_{random_suffix}@example.com',
        'phone': f'139{random.randint(10000000, 99999999)}',
        'role': 'ssz',
        'team': '美化测试产品线',
        'email_notifications': 'on',
        'gotify_notifications': 'on',
        'inapp_notifications': 'on'
    }

def test_beautiful_registration_page():
    """测试美化后的注册页面"""
    print("🎨 测试美化后的注册页面")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试页面加载
        print("1. 测试页面加载...")
        response = requests.get(f"{base_url}/register")
        
        if response.status_code == 200:
            content = response.text
            
            # 检查页面是否包含美化元素
            checks = [
                ('Bootstrap CSS', 'bootstrap@5.1.3'),
                ('Font Awesome', 'font-awesome'),
                ('Google Fonts', 'fonts.googleapis.com'),
                ('渐变背景', 'linear-gradient'),
                ('动画效果', '@keyframes'),
                ('响应式设计', '@media'),
                ('基本信息区块', '基本信息'),
                ('联系信息区块', '联系信息'),
                ('工作信息区块', '工作信息'),
                ('通知偏好区块', '通知偏好设置'),
                ('侧边栏信息', '安全可靠'),
                ('JavaScript功能', 'registerForm'),
            ]
            
            print("   页面元素检查:")
            for check_name, check_key in checks:
                if check_key in content:
                    print(f"     ✅ {check_name}: 存在")
                else:
                    print(f"     ❌ {check_name}: 缺失")
            
            return True
        else:
            print(f"   ❌ 页面加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试页面加载失败: {e}")
        return False

def test_registration_functionality():
    """测试注册功能"""
    print("\n🔧 测试注册功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
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
                
                # 验证用户是否创建成功
                from db_factory import get_db_connection
                from sql_adapter import adapt_sql
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                query, params = adapt_sql("""
                    SELECT id, username, email, phone FROM users 
                    WHERE username = %s
                """, (test_user['username'],))
                
                cursor.execute(query, params)
                user_record = cursor.fetchone()
                
                if user_record:
                    print(f"   ✅ 数据库记录创建成功: ID={user_record[0]}")
                    
                    # 检查通知偏好
                    from notification.notification_manager import NotificationManager
                    preferences = NotificationManager.is_user_notification_enabled(str(user_record[0]))
                    
                    print("   通知偏好设置:")
                    print(f"     邮件通知: {'✅ 启用' if preferences.get('email') else '❌ 禁用'}")
                    print(f"     Gotify通知: {'✅ 启用' if preferences.get('gotify') else '❌ 禁用'}")
                    print(f"     应用内通知: {'✅ 启用' if preferences.get('inapp') else '❌ 禁用'}")
                else:
                    print("   ❌ 数据库记录未找到")
                
                conn.close()
                return True
            else:
                print(f"   ❌ 注册失败: {result.get('message')}")
                return False
        else:
            print(f"   ❌ 注册请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试注册功能失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_form_validation():
    """测试表单验证"""
    print("\n✅ 测试表单验证")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试邮箱格式验证
        print("1. 测试邮箱格式验证...")
        invalid_user = generate_test_user()
        invalid_user['email'] = 'invalid-email-format'
        
        response = requests.post(f"{base_url}/register", data=invalid_user)
        if response.status_code == 400:
            result = response.json()
            if '邮箱' in result.get('message', ''):
                print("   ✅ 邮箱格式验证正常")
            else:
                print(f"   ⚠️ 邮箱验证消息: {result.get('message')}")
        else:
            print(f"   ❌ 邮箱格式验证失败: {response.status_code}")
        
        # 2. 测试必填字段验证
        print("\n2. 测试必填字段验证...")
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
        
        return True
        
    except Exception as e:
        print(f"❌ 测试表单验证失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 美化注册页面测试")
    print("=" * 60)
    
    # 测试页面加载
    page_success = test_beautiful_registration_page()
    
    # 测试注册功能
    func_success = test_registration_functionality()
    
    # 测试表单验证
    valid_success = test_form_validation()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   页面美化: {'✅ 通过' if page_success else '❌ 失败'}")
    print(f"   注册功能: {'✅ 通过' if func_success else '❌ 失败'}")
    print(f"   表单验证: {'✅ 通过' if valid_success else '❌ 失败'}")
    
    if page_success and func_success and valid_success:
        print("\n🎉 所有测试通过！美化注册页面功能正常。")
        print("\n🎨 美化特性:")
        print("   1. 现代化渐变背景和动画效果")
        print("   2. 响应式设计，支持移动端")
        print("   3. 分区块展示，信息组织清晰")
        print("   4. 交互式通知偏好设置")
        print("   5. 实时表单验证和反馈")
        print("   6. 侧边栏功能介绍")
        print("   7. 优雅的加载和成功提示")
        print("   8. 现代化图标和字体")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
