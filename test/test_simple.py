#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试主页内容
"""

import requests

def test_main_page():
    """测试主页内容"""
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 登录（使用实施组用户）
        login_data = {
            'username': 'gh',
            'password': 'gh'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"登录状态: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # 获取主页
            index_response = session.get(f"{base_url}/")
            print(f"主页状态: {index_response.status_code}")
            
            if index_response.status_code == 200:
                content = index_response.text
                
                # 检查关键内容
                checks = [
                    ('问题管理中心', '问题管理中心' in content),
                    ('dashboard-header', 'dashboard-header' in content),
                    ('navbar-dark bg-dark', 'navbar-dark bg-dark' in content),
                    ('admin', 'admin' in content),
                ]
                
                for check_name, result in checks:
                    print(f"{check_name}: {'✅' if result else '❌'}")
                
                # 输出部分内容用于调试
                print("\n主页内容片段:")
                lines = content.split('\n')
                for i, line in enumerate(lines[:50]):
                    if '问题管理中心' in line or 'dashboard-header' in line:
                        print(f"第{i+1}行: {line.strip()}")
                        
            elif index_response.status_code == 302:
                print(f"主页重定向到: {index_response.headers.get('Location')}")
                
                # 跟随重定向
                redirect_response = session.get(f"{base_url}{index_response.headers.get('Location')}")
                print(f"重定向页面状态: {redirect_response.status_code}")
                
                if redirect_response.status_code == 200:
                    content = redirect_response.text
                    print(f"重定向页面包含'问题管理中心': {'问题管理中心' in content}")
                    print(f"重定向页面包含'dashboard-header': {'dashboard-header' in content}")
                    
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_main_page()
