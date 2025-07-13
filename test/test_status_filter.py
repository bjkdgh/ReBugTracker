#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试状态筛选修正
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_status_filter_correction():
    """测试状态筛选修正"""
    print("🔧 测试状态筛选修正")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试登录页面
        print("1. 测试登录页面...")
        response = requests.get(f"{base_url}/login")
        
        if response.status_code == 200:
            content = response.text
            
            # 检查登录页面是否正常
            if '系统登录' in content and '欢迎回来' in content:
                print("   ✅ 登录页面加载正常")
            else:
                print("   ❌ 登录页面加载异常")
                return False
        else:
            print(f"   ❌ 登录页面访问失败: {response.status_code}")
            return False
        
        # 2. 登录并测试主页
        print("\n2. 测试主页状态筛选...")
        session = requests.Session()
        
        # 登录
        login_data = {
            'username': 'gh',
            'password': 'gh'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ 登录成功")
            
            # 获取主页
            index_response = session.get(f"{base_url}/")
            
            if index_response.status_code == 200:
                index_content = index_response.text
                
                # 检查状态筛选选项
                status_checks = [
                    ('待处理', 'status-待处理'),
                    ('已分配', 'status-已分配'),
                    ('处理中', 'status-处理中'),
                    ('已解决', 'status-已解决'),
                    ('已完成', 'status-已完成'),  # 修正后的状态
                ]
                
                print("   状态筛选选项检查:")
                all_correct = True
                
                for status_name, status_class in status_checks:
                    if status_class in index_content:
                        print(f"     ✅ {status_name}: 存在")
                    else:
                        print(f"     ❌ {status_name}: 缺失")
                        all_correct = False
                
                # 检查是否还有旧的"已关闭"状态
                if 'status-已关闭' in index_content:
                    print("     ❌ 发现旧的'已关闭'状态，应该已被替换为'已完成'")
                    all_correct = False
                else:
                    print("     ✅ 已成功移除旧的'已关闭'状态")
                
                # 检查JavaScript中的状态处理
                if "status === '已完成'" in index_content:
                    print("     ✅ JavaScript中已更新为'已完成'状态")
                else:
                    print("     ❌ JavaScript中未正确更新状态")
                    all_correct = False
                
                if "status === '已关闭'" in index_content:
                    print("     ❌ JavaScript中仍有旧的'已关闭'状态")
                    all_correct = False
                else:
                    print("     ✅ JavaScript中已移除旧的'已关闭'状态")
                
                return all_correct
            else:
                print(f"   ❌ 主页访问失败: {index_response.status_code}")
                return False
        else:
            print(f"   ❌ 登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_page_status():
    """测试管理员页面状态"""
    print("\n🔧 测试管理员页面状态")
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
                
                # 检查管理员页面是否包含正确的状态处理
                if "status === '已完成'" in admin_content:
                    print("   ✅ 管理员页面JavaScript中已更新为'已完成'状态")
                    return True
                else:
                    print("   ❌ 管理员页面JavaScript中未正确更新状态")
                    return False
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
    print("🚀 ReBugTracker 状态筛选修正测试")
    print("=" * 60)
    
    # 测试状态筛选修正
    filter_success = test_status_filter_correction()
    
    # 测试管理员页面状态
    admin_success = test_admin_page_status()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   状态筛选修正: {'✅ 通过' if filter_success else '❌ 失败'}")
    print(f"   管理员页面状态: {'✅ 通过' if admin_success else '❌ 失败'}")
    
    if filter_success and admin_success:
        print("\n🎉 所有测试通过！状态筛选已成功修正。")
        print("\n✅ 修正内容:")
        print("   1. 将筛选选项中的'已关闭'改为'已完成'")
        print("   2. 更新CSS样式类名 status-已关闭 → status-已完成")
        print("   3. 修正JavaScript统计逻辑中的状态判断")
        print("   4. 同步更新管理员页面的状态处理")
        print("   5. 保持界面美化效果不变")
    else:
        print("\n💥 部分测试失败！请检查相关修正。")
        sys.exit(1)
