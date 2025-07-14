#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试黑色导航栏移除
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_navbar_removal():
    """测试黑色导航栏移除"""
    print("🎨 测试黑色导航栏移除")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试登录页面
        print("1. 测试登录页面...")
        response = requests.get(f"{base_url}/login")
        
        if response.status_code == 200:
            content = response.text
            
            # 检查是否移除了黑色导航栏
            navbar_checks = [
                ('黑色导航栏', 'navbar-dark bg-dark', False),
                ('Bootstrap导航栏', 'navbar navbar-expand-lg', False),
                ('导航栏品牌', 'navbar-brand', False),
                ('导航栏折叠', 'navbar-collapse', False),
            ]
            
            print("   导航栏移除检查:")
            all_removed = True
            
            for check_name, check_pattern, should_exist in navbar_checks:
                pattern_found = check_pattern in content
                if should_exist and pattern_found:
                    print(f"     ✅ {check_name}: 正确存在")
                elif not should_exist and not pattern_found:
                    print(f"     ✅ {check_name}: 已成功移除")
                else:
                    print(f"     ❌ {check_name}: {'缺失' if should_exist else '仍然存在'}")
                    all_removed = False
            
            # 检查页面是否仍然美观
            beauty_checks = [
                ('渐变背景', 'linear-gradient'),
                ('现代化设计', 'border-radius'),
                ('动画效果', '@keyframes'),
                ('响应式设计', '@media'),
            ]
            
            print("   页面美化保持检查:")
            for check_name, check_pattern in beauty_checks:
                if check_pattern in content:
                    print(f"     ✅ {check_name}: 保持正常")
                else:
                    print(f"     ❌ {check_name}: 可能受影响")
                    all_removed = False
            
            return all_removed
        else:
            print(f"   ❌ 登录页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_main_page_navbar():
    """测试主页导航栏"""
    print("\n🏠 测试主页导航栏")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 登录
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ 登录成功")
            
            # 获取主页
            index_response = session.get(f"{base_url}/")
            
            if index_response.status_code == 200:
                index_content = index_response.text
                
                # 检查是否移除了黑色导航栏
                if 'navbar-dark bg-dark' not in index_content:
                    print("   ✅ 主页黑色导航栏已成功移除")
                else:
                    print("   ❌ 主页仍有黑色导航栏")
                    return False
                
                # 检查是否有内置的美化头部
                if 'dashboard-header' in index_content or '问题管理中心' in index_content:
                    print("   ✅ 主页有美化的内置头部")
                else:
                    print("   ❌ 主页缺少美化头部")
                    return False
                
                # 检查通知功能是否正常
                if 'notificationDropdown' in index_content:
                    print("   ✅ 通知功能已集成到页面头部")
                else:
                    print("   ❌ 通知功能缺失")
                    return False
                
                return True
            else:
                print(f"   ❌ 主页访问失败: {index_response.status_code}")
                return False
        else:
            print(f"   ❌ 登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 主页测试失败: {e}")
        return False

def test_admin_page_navbar():
    """测试管理员页面导航栏"""
    print("\n👑 测试管理员页面导航栏")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 管理员登录
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ 管理员登录成功")
            
            # 获取管理员页面
            admin_response = session.get(f"{base_url}/admin")
            
            if admin_response.status_code == 200:
                admin_content = admin_response.text
                
                # 检查是否移除了黑色导航栏
                if 'navbar-dark bg-dark' not in admin_content:
                    print("   ✅ 管理员页面黑色导航栏已成功移除")
                else:
                    print("   ❌ 管理员页面仍有黑色导航栏")
                    return False
                
                # 检查是否有内置的美化头部
                if 'admin-header' in admin_content:
                    print("   ✅ 管理员页面有美化的内置头部")
                else:
                    print("   ❌ 管理员页面缺少美化头部")
                    return False
                
                # 检查通知功能是否正常（管理员页面使用简化设计）
                if '通知管理' in admin_content:
                    print("   ✅ 管理员页面通知功能已集成")
                else:
                    print("   ❌ 管理员页面通知功能缺失")
                    return False
                
                return True
            else:
                print(f"   ❌ 管理员页面访问失败: {admin_response.status_code}")
                return False
        else:
            print(f"   ❌ 管理员登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 管理员页面测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 黑色导航栏移除测试")
    print("=" * 60)
    
    # 测试导航栏移除
    navbar_success = test_navbar_removal()
    
    # 测试主页导航栏
    main_success = test_main_page_navbar()
    
    # 测试管理员页面导航栏
    admin_success = test_admin_page_navbar()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   导航栏移除: {'✅ 通过' if navbar_success else '❌ 失败'}")
    print(f"   主页功能: {'✅ 通过' if main_success else '❌ 失败'}")
    print(f"   管理员页面: {'✅ 通过' if admin_success else '❌ 失败'}")
    
    if navbar_success and main_success and admin_success:
        print("\n🎉 所有测试通过！黑色导航栏已成功移除。")
        print("\n✅ 改进内容:")
        print("   1. 移除了页面顶部的黑色Bootstrap导航栏")
        print("   2. 保持了页面的美化效果和现代化设计")
        print("   3. 将通知功能集成到各页面的内置头部")
        print("   4. 登录、注册、主页、管理员页面都有独立的美化头部")
        print("   5. 页面布局更加简洁和统一")
        print("   6. 响应式设计和动画效果保持不变")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
