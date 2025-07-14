#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gotify通知的实际发送功能
使用gh、zjn、wbx三个用户测试五个通知规则的Gotify推送
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_test_users():
    """获取测试用户信息"""
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        users = {}
        for username in ['gh', 'zjn', 'wbx']:
            query, params = adapt_sql("""
                SELECT id, username, chinese_name, role, gotify_app_token, gotify_user_id
                FROM users WHERE username = %s
            """, (username,))
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                if hasattr(result, 'keys'):
                    users[username] = dict(result)
                else:
                    users[username] = {
                        'id': result[0],
                        'username': result[1], 
                        'chinese_name': result[2],
                        'role': result[3],
                        'gotify_app_token': result[4],
                        'gotify_user_id': result[5]
                    }
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")
        return {}

def test_gotify_config():
    """测试Gotify配置"""
    print("🔔 测试Gotify通知配置")
    print("-" * 50)
    
    try:
        from notification.channels.gotify_notifier import GotifyNotifier
        
        notifier = GotifyNotifier()
        
        print(f"   启用状态: {notifier.is_enabled()}")

        config = notifier.config
        print(f"   服务器URL: {config.get('server_url', 'N/A')}")
        print(f"   全局Token: {'已设置' if config.get('app_token') else '未设置'}")
        print(f"   默认优先级: {config.get('default_priority', 'N/A')}")

        # 简单验证配置完整性
        config_valid = all([
            config.get('server_url'),
            config.get('app_token')
        ])
        print(f"   配置完整性: {'✅ 完整' if config_valid else '❌ 不完整'}")

        return notifier.is_enabled() and config_valid
        
    except Exception as e:
        print(f"   ❌ Gotify配置测试失败: {e}")
        return False

def send_test_gotify(user_info, event_type, event_data):
    """发送测试Gotify通知"""
    try:
        from notification.channels.gotify_notifier import GotifyNotifier
        
        notifier = GotifyNotifier()
        
        if not notifier.is_enabled():
            print(f"      ⚠️ Gotify通知未启用，跳过发送")
            return False
        
        # 生成通知内容
        from notification.simple_notifier import SimpleNotifier
        simple_notifier = SimpleNotifier()
        
        user_display_info = {
            'name': user_info.get('chinese_name') or user_info['username']
        }
        
        content_data = simple_notifier._generate_content(event_type, event_data, user_display_info)
        
        # 发送Gotify通知
        recipient = {
            'id': user_info['id'],
            'name': user_display_info['name'],
            'gotify_app_token': user_info.get('gotify_app_token'),
            'gotify_user_id': user_info.get('gotify_user_id')
        }
        
        success = notifier.send(
            title=content_data['title'],
            content=content_data['content'],
            recipient=recipient,
            priority=content_data['priority'],  # 会被转换为10
            metadata=content_data.get('metadata', {})
        )
        
        token_type = "用户专属" if user_info.get('gotify_app_token') else "全局"
        
        if success:
            print(f"      ✅ Gotify推送成功 → {user_info['username']} ({token_type}Token)")
        else:
            print(f"      ❌ Gotify推送失败 → {user_info['username']} ({token_type}Token)")
        
        return success
        
    except Exception as e:
        print(f"      ❌ Gotify推送异常: {e}")
        return False

def test_rule_1_gotify():
    """测试规则1的Gotify通知：问题创建"""
    print("\n🆕 测试规则1 Gotify通知：问题创建")
    print("   gh(实施组) 创建问题 → Gotify推送 zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 2001,
        'title': '【Gotify测试】数据库连接超时',
        'description': '生产数据库连接频繁超时，影响业务正常运行',
        'creator_name': users['gh'].get('chinese_name', 'gh'),
        'created_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'creator_id': users['gh']['id'],
        'assigned_manager_id': users['zjn']['id']
    }
    
    print(f"   📤 创建者: {users['gh']['username']} ({users['gh'].get('chinese_name', 'N/A')})")
    print(f"   📥 通知对象: {users['zjn']['username']} ({users['zjn'].get('chinese_name', 'N/A')})")
    print(f"   🔔 优先级: 10 (最高)")
    
    return send_test_gotify(users['zjn'], 'bug_created', event_data)

def test_rule_2_gotify():
    """测试规则2的Gotify通知：问题分配"""
    print("\n🔔 测试规则2 Gotify通知：问题分配")
    print("   zjn(负责人) 分配问题 → Gotify推送 wbx(组内成员)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 2001,
        'title': '【Gotify测试】数据库连接超时',
        'description': '生产数据库连接频繁超时，影响业务正常运行',
        'assigner_name': users['zjn'].get('chinese_name', 'zjn'),
        'assigned_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'assignee_id': users['wbx']['id']
    }
    
    print(f"   📤 分配者: {users['zjn']['username']} ({users['zjn'].get('chinese_name', 'N/A')})")
    print(f"   📥 通知对象: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    print(f"   🔔 优先级: 10 (最高)")
    
    return send_test_gotify(users['wbx'], 'bug_assigned', event_data)

def test_rule_3_gotify():
    """测试规则3的Gotify通知：状态变更"""
    print("\n🔄 测试规则3 Gotify通知：状态变更")
    print("   wbx(组内成员) 更新状态 → Gotify推送 gh(创建者) 和 wbx(分配者)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 2001,
        'title': '【Gotify测试】数据库连接超时',
        'old_status': '已分配',
        'new_status': '处理中',
        'operator_name': users['wbx'].get('chinese_name', 'wbx'),
        'updated_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 操作者: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    print(f"   🔔 优先级: 10 (最高)")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    results.append(send_test_gotify(users['gh'], 'bug_status_changed', event_data))
    
    # 通知分配者（自己）
    print(f"   📥 通知分配者: {users['wbx']['username']}")
    results.append(send_test_gotify(users['wbx'], 'bug_status_changed', event_data))
    
    return all(results)

def test_rule_4_gotify():
    """测试规则4的Gotify通知：问题解决"""
    print("\n✅ 测试规则4 Gotify通知：问题解决")
    print("   wbx(组内成员) 解决问题 → Gotify推送 gh(创建者) 和 zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 2001,
        'title': '【Gotify测试】数据库连接超时',
        'solution': '已优化数据库连接池配置，增加超时重试机制',
        'resolver_name': users['wbx'].get('chinese_name', 'wbx'),
        'resolved_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 解决者: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    print(f"   🔔 优先级: 10 (最高)")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    results.append(send_test_gotify(users['gh'], 'bug_resolved', event_data))
    
    # 通知负责人
    print(f"   📥 通知负责人: {users['zjn']['username']}")
    results.append(send_test_gotify(users['zjn'], 'bug_resolved', event_data))
    
    return all(results)

def test_rule_5_gotify():
    """测试规则5的Gotify通知：问题关闭"""
    print("\n🎯 测试规则5 Gotify通知：问题关闭")
    print("   gh(实施组) 确认闭环 → Gotify推送 gh(创建者)、wbx(分配者)、zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 2001,
        'title': '【Gotify测试】数据库连接超时',
        'close_reason': '实施组确认闭环',
        'closer_name': users['gh'].get('chinese_name', 'gh'),
        'closed_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 闭环者: {users['gh']['username']} ({users['gh'].get('chinese_name', 'N/A')})")
    print(f"   🔔 优先级: 10 (最高)")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    results.append(send_test_gotify(users['gh'], 'bug_closed', event_data))
    
    # 通知分配者
    print(f"   📥 通知分配者: {users['wbx']['username']}")
    results.append(send_test_gotify(users['wbx'], 'bug_closed', event_data))
    
    # 通知负责人
    print(f"   📥 通知负责人: {users['zjn']['username']}")
    results.append(send_test_gotify(users['zjn'], 'bug_closed', event_data))
    
    return all(results)

def main():
    """主函数"""
    print("🔔 ReBugTracker Gotify通知实际发送测试")
    print("=" * 80)
    print("测试用户：gh(实施组) → zjn(负责人) → wbx(组内成员)")
    print("测试内容：五个通知规则的Gotify实际推送")
    print("=" * 80)
    
    # 显示用户信息
    users = get_test_users()
    if users:
        print("\n👥 测试用户Gotify配置:")
        for username, info in users.items():
            user_token = "已设置" if info.get('gotify_app_token') else "未设置"
            user_id = info.get('gotify_user_id', '未设置')
            print(f"   {username}: Token={user_token}, UserID={user_id}")
    
    # 测试Gotify配置
    config_ok = test_gotify_config()
    if not config_ok:
        print("\n❌ Gotify配置异常，无法进行推送测试")
        return False
    
    # 执行五个规则测试
    print("\n" + "=" * 80)
    print("开始Gotify推送测试...")
    print("💡 所有推送都使用优先级10（最高优先级）")
    
    test_functions = [
        ("规则1: 问题创建推送", test_rule_1_gotify),
        ("规则2: 问题分配推送", test_rule_2_gotify),
        ("规则3: 状态变更推送", test_rule_3_gotify),
        ("规则4: 问题解决推送", test_rule_4_gotify),
        ("规则5: 问题关闭推送", test_rule_5_gotify)
    ]
    
    results = []
    for name, test_func in test_functions:
        print(f"\n⏳ 执行 {name}...")
        result = test_func()
        results.append((name, result))
        time.sleep(1)  # 避免推送过快
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📊 Gotify推送测试结果总结:")
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n总体结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有Gotify通知测试通过！")
        print("📱 请检查您的Gotify客户端是否收到推送")
    else:
        print("⚠️ 部分Gotify通知测试失败，请检查配置和网络")
    
    return success_count == total_count

if __name__ == "__main__":
    main()
