#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Gotify测试
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gotify_simple():
    """简单Gotify测试"""
    print("🧪 简单Gotify测试")
    print("=" * 50)
    
    # 使用环境变量或默认配置
    server_url = os.getenv('GOTIFY_SERVER_URL', 'http://localhost:8080')
    app_token = os.getenv('GOTIFY_APP_TOKEN', '')
    
    print(f"服务器地址: {server_url}")
    print(f"Token: {'已设置' if app_token else '未设置'}")
    
    if not app_token:
        print("❌ 没有设置GOTIFY_APP_TOKEN环境变量")
        print("请设置环境变量或在管理员页面配置Gotify")
        return False
    
    try:
        url = f"{server_url.rstrip('/')}/message"
        
        data = {
            "title": "🧪 ReBugTracker简单测试",
            "message": f"""您好！

这是一条简单的Gotify测试消息。

📱 测试信息：
- 发送时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 目标用户: t1
- 服务器: {server_url}

如果您收到这条消息，说明Gotify基本功能正常！""",
            "priority": 5
        }
        
        headers = {
            "X-Gotify-Key": app_token,
            "Content-Type": "application/json"
        }
        
        print("发送测试消息...")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ 消息发送成功！")
            print("📱 请检查您的Gotify客户端")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def test_gotify_with_system_config():
    """使用系统配置测试Gotify"""
    print("\n🔧 使用系统配置测试Gotify...")
    print("=" * 50)
    
    try:
        from notification.channels.gotify_notifier import GotifyNotifier
        
        print("1. 创建Gotify通知器...")
        gotify_notifier = GotifyNotifier()
        
        print("2. 检查通知器状态...")
        is_enabled = gotify_notifier.is_enabled()
        print(f"   状态: {'✅ 启用' if is_enabled else '❌ 禁用'}")
        
        if not is_enabled:
            print("   ⚠️ Gotify通知器未启用")
            print("   请在管理员页面配置Gotify设置")
            return False
        
        print("3. 准备测试消息...")
        recipient_info = {
            'id': '27',
            'name': 't1',
            'email': '237038603@qq.com'
        }
        
        print("4. 发送测试消息...")
        success = gotify_notifier.send(
            title="🧪 ReBugTracker系统配置测试",
            content=f"""您好 t1！

这是通过系统配置发送的Gotify测试消息。

📋 用户信息：
- 用户名: t1
- 用户ID: 27
- 邮箱: 237038603@qq.com

如果您收到这条消息，说明Gotify通知系统配置正确！

---
ReBugTracker 系统
测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            recipient=recipient_info,
            priority=2,
            metadata={
                'event_type': 'test',
                'user_id': '27',
                'test_type': 'system_config_test'
            }
        )
        
        if success:
            print("   ✅ 系统配置发送成功！")
            return True
        else:
            print("   ❌ 系统配置发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始Gotify通知测试")
    print("📱 目标用户: t1")
    print()
    
    # 测试1: 简单测试
    success1 = test_gotify_simple()
    
    # 测试2: 系统配置测试
    success2 = test_gotify_with_system_config()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   简单测试: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   系统配置测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 至少有一种方式发送成功！")
        print("📱 请检查您的Gotify客户端应用")
    else:
        print("\n❌ 所有测试都失败了")
        print("💡 请检查:")
        print("   1. Gotify服务器是否运行")
        print("   2. 服务器地址是否正确")
        print("   3. App Token是否有效")
        print("   4. 网络连接是否正常")

if __name__ == "__main__":
    main()
