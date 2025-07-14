#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实配置测试Gotify通知发送给t1用户
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_gotify_config():
    """获取Gotify配置"""
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取Gotify配置
        query, params = adapt_sql('SELECT config_key, config_value FROM system_config WHERE config_key LIKE %s', ('notification_gotify_%',))
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        config_dict = {}
        for config in configs:
            key = config[0].replace('notification_gotify_', '')
            value = config[1]
            config_dict[key] = value
        
        # 获取t1用户的个人Token
        query, params = adapt_sql('SELECT gotify_app_token FROM users WHERE username = %s', ('t1',))
        cursor.execute(query, params)
        user_result = cursor.fetchone()
        user_token = user_result[0] if user_result and user_result[0] else None
        
        # 获取t1用户的通知偏好
        query, params = adapt_sql('SELECT gotify_enabled FROM user_notification_preferences WHERE user_id = %s', ('27',))
        cursor.execute(query, params)
        pref_result = cursor.fetchone()
        user_enabled = pref_result[0] if pref_result else True
        
        conn.close()
        
        return {
            'server_url': config_dict.get('server_url', 'http://localhost:8080'),
            'app_token': config_dict.get('app_token', ''),
            'enabled': config_dict.get('enabled', 'false') == 'true',
            'default_priority': int(config_dict.get('default_priority', '10')),
            'user_token': user_token,
            'user_enabled': user_enabled
        }
        
    except Exception as e:
        print(f"获取配置失败: {e}")
        return None

def test_gotify_direct():
    """直接测试Gotify发送"""
    print("🧪 直接测试Gotify发送...")
    print("=" * 50)
    
    config = get_gotify_config()
    if not config:
        return False
    
    print(f"服务器地址: {config['server_url']}")
    print(f"全局Token: {'已设置' if config['app_token'] else '未设置'}")
    print(f"用户Token: {'已设置' if config['user_token'] else '未设置'}")
    print(f"系统启用: {config['enabled']}")
    print(f"用户启用: {config['user_enabled']}")
    
    if not config['enabled']:
        print("❌ Gotify系统未启用")
        return False
    
    if not config['user_enabled']:
        print("❌ 用户Gotify通知未启用")
        return False
    
    # 选择使用的Token
    token = config['user_token'] or config['app_token']
    if not token:
        print("❌ 没有可用的Token")
        return False
    
    token_type = "用户专属" if config['user_token'] else "全局"
    print(f"使用Token: {token_type}")
    
    try:
        url = f"{config['server_url'].rstrip('/')}/message"
        
        # 准备消息
        title = "🧪 ReBugTracker Gotify测试"
        content = """您好 t1！

这是一条来自ReBugTracker的Gotify测试消息。

📱 测试信息：
- 用户: t1 (ID: 27)
- 邮箱: 237038603@qq.com
- 服务器: {server_url}
- Token类型: {token_type}

如果您收到这条消息，说明Gotify通知功能正常工作！

---
ReBugTracker 系统
测试时间: {current_time}""".format(
            server_url=config['server_url'],
            token_type=token_type,
            current_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # 如果使用全局Token，添加用户标识
        if not config['user_token']:
            title = "[t1] " + title
            content = "@t1\n" + content
        
        data = {
            "title": title,
            "message": content,
            "priority": config['default_priority'],
            "extras": {
                "client::display": {
                    "contentType": "text/markdown"
                },
                "rebugtracker": {
                    "event_type": "test",
                    "user_id": "27",
                    "test_type": "direct_gotify_test",
                    "token_type": token_type
                }
            }
        }
        
        headers = {
            "X-Gotify-Key": token,
            "Content-Type": "application/json"
        }
        
        print("发送测试消息...")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Gotify消息发送成功！")
            print("📱 请检查您的Gotify客户端")
            result = response.json()
            print(f"消息ID: {result.get('id', 'N/A')}")
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

def test_gotify_via_notifier():
    """通过通知器测试Gotify发送"""
    print("\n🔄 通过通知器测试Gotify发送...")
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
            return False
        
        print("3. 准备收件人信息...")
        recipient_info = {
            'id': '27',
            'name': 't1',
            'email': '237038603@qq.com'
        }
        
        print("4. 发送测试消息...")
        success = gotify_notifier.send(
            title="🧪 ReBugTracker通知器测试",
            content="""您好 t1！

这是通过ReBugTracker通知器发送的Gotify测试消息。

📋 测试内容：
- 通知器功能正常
- 消息路由正确
- 用户配置有效
- 服务器连接正常

如果您收到这条消息，说明通知系统工作正常！

---
ReBugTracker 通知系统
测试时间: {current_time}""".format(
                current_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ),
            recipient=recipient_info,
            priority=2,
            metadata={
                'event_type': 'test',
                'test_type': 'notifier_test',
                'user_id': '27'
            }
        )
        
        if success:
            print("   ✅ 通知器发送成功！")
            return True
        else:
            print("   ❌ 通知器发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试Gotify通知发送给t1用户")
    print("📱 目标用户: t1 (ID: 27)")
    print()
    
    # 显示配置信息
    config = get_gotify_config()
    if config:
        print("📋 当前配置:")
        print(f"   服务器: {config['server_url']}")
        print(f"   系统启用: {config['enabled']}")
        print(f"   用户启用: {config['user_enabled']}")
        print()
    
    # 测试直接发送
    success1 = test_gotify_direct()
    
    # 测试通过通知器发送
    success2 = test_gotify_via_notifier()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   直接Gotify发送: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   通知器发送: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 至少有一种方式发送成功！")
        print("📱 请检查您的Gotify客户端应用")
        print("🔔 注意查看通知是否到达")
        print(f"🌐 服务器地址: {config['server_url'] if config else 'N/A'}")
    else:
        print("\n❌ 所有测试都失败了，请检查Gotify配置")

if __name__ == "__main__":
    main()
