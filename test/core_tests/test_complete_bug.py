#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试确认闭环功能
"""

import requests
import json

def test_complete_bug():
    """测试确认闭环功能"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 测试确认闭环功能")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 登录实施组用户
        print("\n1. 登录实施组用户...")
        login_data = {
            'username': 'gh',  # 实施组用户
            'password': '123456'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200 and 'login' not in response.url:
            print("   ✅ 登录成功")
        else:
            print("   ❌ 登录失败")
            return
        
        # 2. 获取用户创建的已解决问题
        print("\n2. 查找已解决的问题...")
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ 获取首页成功")
            
            # 检查页面中是否有确认闭环按钮
            if "确认闭环" in response.text:
                print("   ✅ 找到确认闭环按钮")
                
                # 尝试从页面中提取问题ID（简单的文本搜索）
                import re
                pattern = r'confirmComplete\([\'"](\d+)[\'"]\)'
                matches = re.findall(pattern, response.text)
                
                if matches:
                    bug_id = matches[0]
                    print(f"   ✅ 找到可闭环的问题ID: {bug_id}")
                    
                    # 3. 测试确认闭环功能
                    print(f"\n3. 测试确认闭环问题 {bug_id}...")
                    complete_response = session.post(
                        f"{base_url}/bug/complete/{bug_id}",
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if complete_response.status_code == 200:
                        result = complete_response.json()
                        if result.get('success'):
                            print("   ✅ 确认闭环成功！")
                            print(f"   📝 消息: {result.get('message')}")
                            
                            # 4. 验证问题状态是否已更新
                            print(f"\n4. 验证问题状态...")
                            detail_response = session.get(f"{base_url}/bug/{bug_id}")
                            if detail_response.status_code == 200:
                                if "已完成" in detail_response.text:
                                    print("   ✅ 问题状态已更新为'已完成'")
                                else:
                                    print("   ⚠️ 问题状态可能未正确更新")
                            else:
                                print("   ❌ 无法获取问题详情")
                        else:
                            print(f"   ❌ 确认闭环失败: {result.get('message')}")
                    else:
                        print(f"   ❌ 确认闭环请求失败: {complete_response.status_code}")
                        print(f"   📝 响应: {complete_response.text}")
                else:
                    print("   ⚠️ 页面中没有找到可闭环的问题")
            else:
                print("   ⚠️ 页面中没有确认闭环按钮，可能没有已解决的问题")
        else:
            print(f"   ❌ 获取首页失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_complete_bug()
