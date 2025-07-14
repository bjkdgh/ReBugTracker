#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试清理统计信息功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

def login_and_get_session():
    """登录并获取session"""
    session = requests.Session()

    # 模拟登录（使用admin用户）
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }

    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)

    if login_response.status_code == 200:
        print("✅ 登录成功")
        return session
    else:
        print(f"❌ 登录失败，状态码: {login_response.status_code}")
        return None

def test_cleanup_stats():
    """测试清理统计信息API"""
    print("🧪 测试清理统计信息功能...")

    # 获取登录session
    session = login_and_get_session()
    if not session:
        print("❌ 无法获取登录session")
        return

    # 测试API端点
    url = "http://127.0.0.1:5000/admin/notifications/cleanup/stats"

    try:
        # 发送请求
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            print(f"📊 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查新增的字段
            if data.get('success') and 'data' in data:
                stats = data['data']
                
                # 检查是否包含新的统计字段
                required_fields = [
                    'total_notifications', 'user_count', 'retention_days', 
                    'max_per_user', 'expired_count', 'excess_count'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in stats:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ 缺少字段: {missing_fields}")
                else:
                    print("✅ 所有必需字段都存在")
                    print(f"📈 过期记录数: {stats.get('expired_count', 0)}")
                    print(f"📈 过量记录数: {stats.get('excess_count', 0)}")
            else:
                print("❌ API返回格式错误")
                
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_notification_config():
    """测试通知配置API"""
    print("\n🧪 测试通知配置功能...")

    # 获取登录session
    session = login_and_get_session()
    if not session:
        print("❌ 无法获取登录session")
        return

    # 测试获取配置
    url = "http://127.0.0.1:5000/admin/notifications/config"

    try:
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取配置成功")
            
            if data.get('success') and 'data' in data:
                config = data['data']
                server_config = config.get('server', {})
                
                print(f"🔧 服务器配置: {json.dumps(server_config, indent=2, ensure_ascii=False)}")
                
                # 检查是否包含自动清理开关
                if 'auto_cleanup_enabled' in server_config:
                    print(f"✅ 自动清理开关存在: {server_config['auto_cleanup_enabled']}")
                else:
                    print("❌ 缺少自动清理开关配置")
            else:
                print("❌ 配置格式错误")
        else:
            print(f"❌ 获取配置失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试新增的清理统计功能...")
    test_cleanup_stats()
    test_notification_config()
    print("\n✨ 测试完成！")
