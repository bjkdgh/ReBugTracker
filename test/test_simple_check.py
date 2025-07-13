#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单检查页面内容
"""

import requests

def test_page_content():
    """测试页面内容"""
    base_url = "http://localhost:5000"
    
    try:
        # 直接访问主页
        response = requests.get(f"{base_url}/")
        print(f"主页状态: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        
        # 检查是否是登录页面
        if '登录' in response.text and 'username' in response.text:
            print("✅ 访问到登录页面")
            
            # 检查登录页面的关键元素
            login_checks = [
                ('登录表单', '<form' in response.text),
                ('用户名输入', 'name="username"' in response.text),
                ('密码输入', 'name="password"' in response.text),
                ('登录按钮', '登录' in response.text),
            ]
            
            for check_name, result in login_checks:
                print(f"  {'✅' if result else '❌'} {check_name}")
                
        elif '问题管理中心' in response.text:
            print("✅ 访问到主页")
            
            # 检查主页的关键元素
            index_checks = [
                ('问题管理中心', '问题管理中心' in response.text),
                ('用户信息', '郭浩' in response.text or 'chinese_name' in response.text),
                ('通知按钮', 'notificationDropdown' in response.text),
                ('统计卡片', 'stat-card-inline' in response.text),
            ]
            
            for check_name, result in index_checks:
                print(f"  {'✅' if result else '❌'} {check_name}")
        else:
            print("❓ 未知页面类型")
            print(f"页面内容前500字符: {response.text[:500]}")
                    
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_page_content()
