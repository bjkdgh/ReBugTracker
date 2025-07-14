#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试问题关闭（闭环）通知功能
验证当问题状态变为"已完成"时，是否正确通知负责人和组内成员
"""

import requests
import time
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_bug_closure_notification():
    """测试问题关闭通知功能"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔔 测试问题关闭通知功能")
    print("=" * 50)
    
    try:
        session = requests.Session()
        
        # 1. 实施组用户登录
        print("1. 实施组用户登录...")
        login_data = {
            'username': 'gh',  # 实施组用户
            'password': '123456'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ 实施组用户登录成功")
            
            # 2. 查找已解决的问题
            print("\n2. 查找已解决的问题...")
            index_response = session.get(f"{base_url}/")
            
            if index_response.status_code == 200:
                index_content = index_response.text
                
                # 查找已解决状态的问题
                import re
                resolved_bugs = re.findall(r'confirmComplete\((\d+)\)', index_content)
                
                if resolved_bugs:
                    bug_id = resolved_bugs[0]
                    print(f"   ✅ 找到已解决的问题 ID: {bug_id}")
                    
                    # 3. 执行问题关闭操作
                    print(f"\n3. 执行问题关闭操作...")
                    complete_response = session.post(f"{base_url}/bug/complete/{bug_id}")
                    
                    if complete_response.status_code == 200:
                        result = complete_response.json()
                        if result.get('success'):
                            print("   ✅ 问题关闭成功！")
                            print(f"   📝 消息: {result.get('message')}")
                            
                            # 4. 等待通知处理
                            print("\n4. 等待通知处理...")
                            time.sleep(3)
                            
                            # 5. 验证通知是否发送
                            print("\n5. 验证通知发送情况...")
                            print("   📧 检查应用内通知...")
                            
                            # 检查不同用户的通知
                            test_users = [
                                ('zjn', '123456', '负责人'),  # 负责人
                                ('wbx', '123456', '组内成员'),  # 组内成员
                                ('gh', '123456', '实施组')     # 实施组（创建者）
                            ]
                            
                            for username, password, role in test_users:
                                print(f"\n   检查 {role}({username}) 的通知:")
                                
                                # 登录用户
                                user_session = requests.Session()
                                user_login = user_session.post(f"{base_url}/login", data={
                                    'username': username,
                                    'password': password
                                })
                                
                                if user_login.status_code == 200:
                                    # 获取通知
                                    notifications_response = user_session.get(f"{base_url}/api/notifications")
                                    
                                    if notifications_response.status_code == 200:
                                        notifications = notifications_response.json()
                                        
                                        # 查找关闭通知
                                        closure_notifications = [
                                            n for n in notifications.get('data', [])
                                            if '问题已关闭' in n.get('title', '') or '已完成' in n.get('content', '')
                                        ]
                                        
                                        if closure_notifications:
                                            print(f"     ✅ 收到 {len(closure_notifications)} 条关闭通知")
                                            for notif in closure_notifications[:1]:  # 显示最新的一条
                                                print(f"     📋 标题: {notif.get('title')}")
                                                print(f"     📝 内容: {notif.get('content', '')[:100]}...")
                                        else:
                                            print(f"     ❌ 未收到关闭通知")
                                    else:
                                        print(f"     ❌ 获取通知失败: {notifications_response.status_code}")
                                else:
                                    print(f"     ❌ {role} 登录失败")
                            
                            # 6. 验证问题状态
                            print(f"\n6. 验证问题状态...")
                            detail_response = session.get(f"{base_url}/bug/{bug_id}")
                            if detail_response.status_code == 200:
                                if "已完成" in detail_response.text:
                                    print("   ✅ 问题状态已更新为'已完成'")
                                else:
                                    print("   ⚠️ 问题状态可能未正确更新")
                            
                            return True
                            
                        else:
                            print(f"   ❌ 问题关闭失败: {result.get('message')}")
                            return False
                    else:
                        print(f"   ❌ 问题关闭请求失败: {complete_response.status_code}")
                        print(f"   📝 响应: {complete_response.text}")
                        return False
                else:
                    print("   ⚠️ 没有找到已解决的问题，无法测试关闭通知")
                    print("   💡 提示: 请先创建并解决一个问题，然后再运行此测试")
                    return False
            else:
                print(f"   ❌ 获取首页失败: {index_response.status_code}")
                return False
        else:
            print(f"   ❌ 实施组用户登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🧪 ReBugTracker 问题关闭通知测试")
    print("=" * 60)
    
    success = test_bug_closure_notification()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 问题关闭通知测试完成")
    else:
        print("❌ 问题关闭通知测试失败")
    
    return success

if __name__ == "__main__":
    main()
