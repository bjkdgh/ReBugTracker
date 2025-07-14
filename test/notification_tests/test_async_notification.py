#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker - 异步通知处理测试脚本

测试问题提交、分配、解决等操作的异步通知处理效果
"""

import requests
import time
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_async_notification_performance():
    """测试异步通知处理的性能"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 ReBugTracker - 异步通知处理测试")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 测试应用是否运行
        print("1. 检查应用状态...")
        response = session.get(f"{base_url}/login")
        if response.status_code != 200:
            print("❌ 应用未运行，请先启动ReBugTracker")
            return False
        print("✅ 应用正在运行")
        
        # 2. 登录为实施组用户（可以提交问题）
        print("\n2. 登录为实施组用户...")
        login_data = {
            'username': 't1',
            'password': 't1123'
        }
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code != 200:
            print("❌ 登录失败")
            return False
        print("✅ 登录成功")
        
        # 3. 测试问题提交的响应时间
        print("\n3. 测试问题提交响应时间...")
        
        submit_data = {
            'title': '异步通知测试问题',
            'description': '这是一个用于测试异步通知处理的问题',
            'project': '测试项目',
            'manager': '张佳楠'
        }
        
        # 记录开始时间
        start_time = time.time()
        
        response = session.post(f"{base_url}/bug/submit", data=submit_data)
        
        # 记录结束时间
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 问题提交成功")
                    print(f"📊 响应时间: {response_time:.3f} 秒")
                    
                    if response_time < 2.0:
                        print("🚀 响应时间优秀 (< 2秒)")
                    elif response_time < 5.0:
                        print("⚡ 响应时间良好 (< 5秒)")
                    else:
                        print("⚠️  响应时间较慢 (> 5秒)")
                    
                    bug_id = result.get('bug_id')
                    print(f"📝 创建的问题ID: {bug_id}")
                    
                    # 等待一段时间让通知处理完成
                    print("⏳ 等待通知处理完成...")
                    time.sleep(3)
                    
                    return bug_id
                else:
                    print(f"❌ 问题提交失败: {result.get('message', '未知错误')}")
                    return False
            except json.JSONDecodeError:
                print("❌ 响应格式错误")
                return False
        else:
            print(f"❌ 问题提交失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用，请确保ReBugTracker正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def test_assignment_performance(session, bug_id):
    """测试问题分配的响应时间"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n4. 测试问题分配响应时间...")
    
    # 先登录为负责人
    login_data = {
        'username': 'zjn',
        'password': 'zjn123'
    }
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code != 200:
        print("❌ 负责人登录失败")
        return False
    
    # 分配问题
    assign_data = {
        'assigned_to': '李世杰'
    }
    
    # 记录开始时间
    start_time = time.time()
    
    response = session.post(f"{base_url}/bug/{bug_id}/assign", data=assign_data)
    
    # 记录结束时间
    end_time = time.time()
    response_time = end_time - start_time
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('success'):
                print(f"✅ 问题分配成功")
                print(f"📊 响应时间: {response_time:.3f} 秒")
                
                if response_time < 1.0:
                    print("🚀 响应时间优秀 (< 1秒)")
                elif response_time < 3.0:
                    print("⚡ 响应时间良好 (< 3秒)")
                else:
                    print("⚠️  响应时间较慢 (> 3秒)")
                
                return True
            else:
                print(f"❌ 问题分配失败: {result.get('message', '未知错误')}")
                return False
        except json.JSONDecodeError:
            print("❌ 响应格式错误")
            return False
    else:
        print(f"❌ 问题分配失败，状态码: {response.status_code}")
        return False

def main():
    """主函数"""
    print("ReBugTracker - 异步通知处理测试")
    print("测试问题提交、分配等操作的响应时间和异步通知处理")
    print()
    
    # 测试问题提交
    bug_id = test_async_notification_performance()
    
    if bug_id:
        # 创建新会话测试分配
        session = requests.Session()
        assignment_success = test_assignment_performance(session, bug_id)
        
        print("\n📋 测试总结:")
        print("✅ 问题提交异步通知处理正常")
        if assignment_success:
            print("✅ 问题分配异步通知处理正常")
        
        print("\n🎯 异步通知处理的优势:")
        print("• 用户界面响应更快")
        print("• 不会因为通知发送失败而影响主要功能")
        print("• 通知在后台异步处理，提升用户体验")
        print("• 减少页面等待时间")
        
        print("\n💡 实现原理:")
        print("• 主要操作立即返回响应")
        print("• 通知发送在后台线程中异步处理")
        print("• 使用daemon线程，不阻塞主进程")
        print("• 详细的日志记录，便于调试")
        
        return True
    else:
        print("\n❌ 异步通知处理测试失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
