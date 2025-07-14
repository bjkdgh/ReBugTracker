#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试index页面内容
"""

import requests

def test_index_content():
    """测试index页面内容"""
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 先访问登录页面
        login_page = session.get(f"{base_url}/login")
        print(f"登录页面状态: {login_page.status_code}")
        
        # 登录
        login_data = {
            'username': 'gh',
            'password': 'gh'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"登录响应状态: {login_response.status_code}")
        print(f"登录响应内容长度: {len(login_response.text)}")
        
        if login_response.status_code == 200:
            # 获取主页
            index_response = session.get(f"{base_url}/")
            print(f"主页状态: {index_response.status_code}")
            
            if index_response.status_code == 200:
                content = index_response.text
                
                # 检查关键内容
                checks = [
                    ('问题管理中心', '问题管理中心' in content),
                    ('通知按钮', 'notificationDropdown' in content),
                    ('提交新问题', '提交新问题' in content),
                    ('统计容器', 'stats-container' in content),
                    ('内联统计卡片', 'stat-card-inline' in content),
                    ('点击筛选', 'filterByStatus' in content),
                    ('总问题数', 'totalBugs' in content),
                    ('待处理', 'pendingBugs' in content),
                    ('已分配', 'assignedBugs' in content),
                    ('处理中', 'processingBugs' in content),
                    ('已解决', 'resolvedBugs' in content),
                    ('已完成', 'completedBugs' in content),
                ]
                
                print("\n主页内容检查:")
                for check_name, result in checks:
                    print(f"  {'✅' if result else '❌'} {check_name}")
                
                # 检查按钮顺序
                notification_pos = content.find('notificationDropdown')
                submit_pos = content.find('提交新问题')
                
                if notification_pos > 0 and submit_pos > 0:
                    if notification_pos < submit_pos:
                        print("  ✅ 通知按钮在提交新问题按钮前面")
                    else:
                        print("  ❌ 按钮顺序错误")
                        print(f"     通知位置: {notification_pos}, 提交位置: {submit_pos}")
                
                # 输出部分内容用于调试
                print(f"\n页面内容长度: {len(content)}")
                
            elif index_response.status_code == 302:
                print(f"主页重定向到: {index_response.headers.get('Location')}")
                
        else:
            print(f"登录失败，响应内容: {login_response.text[:500]}")
                    
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_index_content()
