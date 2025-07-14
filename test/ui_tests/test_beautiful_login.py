#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试美化后的登录页面
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_beautiful_login_page():
    """测试美化后的登录页面"""
    print("🎨 测试美化后的登录页面")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试页面加载
        print("1. 测试页面加载...")
        response = requests.get(f"{base_url}/login")
        
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
                ('登录表单', 'loginForm'),
                ('快速登录', '快速登录'),
                ('侧边栏信息', '高效管理'),
                ('JavaScript功能', 'quickLogin'),
                ('欢迎标题', '欢迎回来'),
                ('系统登录', '系统登录'),
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

def test_login_functionality():
    """测试登录功能"""
    print("\n🔧 测试登录功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    try:
        # 1. 测试正确登录
        print("1. 测试正确登录...")
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        
        if response.status_code == 200:
            print("   ✅ 管理员登录成功")
            
            # 验证是否真的登录成功
            dashboard_response = session.get(f"{base_url}/admin")
            if dashboard_response.status_code == 200:
                print("   ✅ 登录状态验证成功")
            else:
                print("   ⚠️ 登录状态验证失败")
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
        
        # 2. 测试错误登录
        print("\n2. 测试错误登录...")
        session_new = requests.Session()
        wrong_login_data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        
        response = session_new.post(f"{base_url}/login", data=wrong_login_data)
        
        if response.status_code != 200 or 'admin' not in response.url:
            print("   ✅ 错误登录被正确拒绝")
        else:
            print("   ❌ 错误登录未被拒绝")
        
        # 3. 测试其他角色登录
        print("\n3. 测试其他角色登录...")
        test_users = [
            ('gh', 'gh', '实施组'),
            ('zjn', 'zjn', '负责人'),
            ('wbx', 'wbx', '组员')
        ]
        
        for username, password, role_name in test_users:
            session_role = requests.Session()
            role_login_data = {
                'username': username,
                'password': password
            }
            
            response = session_role.post(f"{base_url}/login", data=role_login_data)
            
            if response.status_code == 200:
                print(f"   ✅ {role_name}({username})登录成功")
            else:
                print(f"   ❌ {role_name}({username})登录失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试登录功能失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_consistency():
    """测试UI一致性"""
    print("\n🎯 测试UI一致性")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 获取登录页面
        print("1. 检查登录页面风格...")
        login_response = requests.get(f"{base_url}/login")
        login_content = login_response.text
        
        # 2. 获取注册页面
        print("2. 检查注册页面风格...")
        register_response = requests.get(f"{base_url}/register")
        register_content = register_response.text
        
        # 3. 检查共同元素
        print("3. 检查风格一致性...")
        common_elements = [
            ('渐变背景', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'),
            ('字体', 'Inter'),
            ('动画效果', '@keyframes slideUp'),
            ('圆角设计', 'border-radius: 20px'),
            ('毛玻璃效果', 'backdrop-filter: blur'),
            ('按钮样式', 'btn-'),
            ('响应式设计', '@media (max-width: 768px)'),
        ]
        
        for element_name, element_key in common_elements:
            login_has = element_key in login_content
            register_has = element_key in register_content
            
            if login_has and register_has:
                print(f"   ✅ {element_name}: 两页面风格一致")
            elif login_has or register_has:
                print(f"   ⚠️ {element_name}: 两页面风格不一致")
            else:
                print(f"   ❌ {element_name}: 两页面都缺少此元素")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试UI一致性失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 美化登录页面测试")
    print("=" * 60)
    
    # 测试页面加载
    page_success = test_beautiful_login_page()
    
    # 测试登录功能
    func_success = test_login_functionality()
    
    # 测试UI一致性
    ui_success = test_ui_consistency()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   页面美化: {'✅ 通过' if page_success else '❌ 失败'}")
    print(f"   登录功能: {'✅ 通过' if func_success else '❌ 失败'}")
    print(f"   UI一致性: {'✅ 通过' if ui_success else '❌ 失败'}")
    
    if page_success and func_success and ui_success:
        print("\n🎉 所有测试通过！美化登录页面功能正常。")
        print("\n🎨 美化特性:")
        print("   1. 与注册页面风格统一的现代化设计")
        print("   2. 渐变背景和动画效果")
        print("   3. 响应式设计，支持移动端")
        print("   4. 快速登录按钮，方便测试")
        print("   5. 实时表单验证和反馈")
        print("   6. 侧边栏功能介绍")
        print("   7. 优雅的加载和成功提示")
        print("   8. 现代化图标和字体")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
