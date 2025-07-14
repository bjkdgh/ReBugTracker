#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试邮件通知的实际发送功能
使用gh、zjn、wbx三个用户测试五个通知规则的邮件发送
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
                SELECT id, username, chinese_name, role, email
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
                        'email': result[4]
                    }
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")
        return {}

def test_email_config():
    """测试邮件配置"""
    print("📧 测试邮件通知配置")
    print("-" * 50)
    
    try:
        from notification.channels.email_notifier import EmailNotifier
        
        notifier = EmailNotifier()
        
        print(f"   启用状态: {notifier.is_enabled()}")

        config = notifier.config
        print(f"   SMTP服务器: {config.get('smtp_server', 'N/A')}")
        print(f"   SMTP端口: {config.get('smtp_port', 'N/A')}")
        print(f"   发送邮箱: {config.get('from_email', 'N/A')}")
        print(f"   使用TLS: {config.get('use_tls', 'N/A')}")

        # 简单验证配置完整性
        config_valid = all([
            config.get('smtp_server'),
            config.get('smtp_port'),
            config.get('from_email'),
            config.get('password')
        ])
        print(f"   配置完整性: {'✅ 完整' if config_valid else '❌ 不完整'}")

        return notifier.is_enabled() and config_valid
        
    except Exception as e:
        print(f"   ❌ 邮件配置测试失败: {e}")
        return False

def send_test_email(user_info, event_type, event_data):
    """发送测试邮件"""
    try:
        from notification.channels.email_notifier import EmailNotifier
        
        notifier = EmailNotifier()
        
        if not notifier.is_enabled():
            print(f"      ⚠️ 邮件通知未启用，跳过发送")
            return False
        
        if not user_info.get('email'):
            print(f"      ⚠️ 用户{user_info['username']}没有邮箱地址")
            return False
        
        # 生成通知内容
        from notification.simple_notifier import SimpleNotifier
        simple_notifier = SimpleNotifier()
        
        user_display_info = {
            'name': user_info.get('chinese_name') or user_info['username']
        }
        
        content_data = simple_notifier._generate_content(event_type, event_data, user_display_info)
        
        # 发送邮件
        recipient = {
            'id': user_info['id'],
            'name': user_display_info['name'],
            'email': user_info['email']
        }
        
        success = notifier.send(
            title=content_data['title'],
            content=content_data['content'],
            recipient=recipient,
            priority=content_data['priority'],
            metadata=content_data.get('metadata', {})
        )
        
        if success:
            print(f"      ✅ 邮件发送成功 → {user_info['email']}")
        else:
            print(f"      ❌ 邮件发送失败 → {user_info['email']}")
        
        return success
        
    except Exception as e:
        print(f"      ❌ 邮件发送异常: {e}")
        return False

def test_rule_1_email():
    """测试规则1的邮件通知：问题创建"""
    print("\n🆕 测试规则1邮件通知：问题创建")
    print("   gh(实施组) 创建问题 → 邮件通知 zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 1001,
        'title': '【邮件测试】网络连接异常问题',
        'description': '生产环境网络连接出现间歇性中断，需要紧急处理',
        'creator_name': users['gh'].get('chinese_name', 'gh'),
        'created_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'creator_id': users['gh']['id'],
        'assigned_manager_id': users['zjn']['id']
    }
    
    print(f"   📤 创建者: {users['gh']['username']} ({users['gh'].get('chinese_name', 'N/A')})")
    print(f"   📥 通知对象: {users['zjn']['username']} ({users['zjn'].get('chinese_name', 'N/A')})")
    
    return send_test_email(users['zjn'], 'bug_created', event_data)

def test_rule_2_email():
    """测试规则2的邮件通知：问题分配"""
    print("\n🔔 测试规则2邮件通知：问题分配")
    print("   zjn(负责人) 分配问题 → 邮件通知 wbx(组内成员)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 1001,
        'title': '【邮件测试】网络连接异常问题',
        'description': '生产环境网络连接出现间歇性中断，需要紧急处理',
        'assigner_name': users['zjn'].get('chinese_name', 'zjn'),
        'assigned_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'assignee_id': users['wbx']['id']
    }
    
    print(f"   📤 分配者: {users['zjn']['username']} ({users['zjn'].get('chinese_name', 'N/A')})")
    print(f"   📥 通知对象: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    
    return send_test_email(users['wbx'], 'bug_assigned', event_data)

def test_rule_3_email():
    """测试规则3的邮件通知：状态变更"""
    print("\n🔄 测试规则3邮件通知：状态变更")
    print("   wbx(组内成员) 更新状态 → 邮件通知 gh(创建者) 和 wbx(分配者)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 1001,
        'title': '【邮件测试】网络连接异常问题',
        'old_status': '已分配',
        'new_status': '处理中',
        'operator_name': users['wbx'].get('chinese_name', 'wbx'),
        'updated_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 操作者: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    results.append(send_test_email(users['gh'], 'bug_status_changed', event_data))
    
    # 通知分配者（自己）
    print(f"   📥 通知分配者: {users['wbx']['username']}")
    results.append(send_test_email(users['wbx'], 'bug_status_changed', event_data))
    
    return all(results)

def test_rule_4_email():
    """测试规则4的邮件通知：问题解决"""
    print("\n✅ 测试规则4邮件通知：问题解决")
    print("   wbx(组内成员) 解决问题 → 邮件通知 gh(创建者) 和 zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 1001,
        'title': '【邮件测试】网络连接异常问题',
        'solution': '已重启网络设备并更新配置，问题已解决',
        'resolver_name': users['wbx'].get('chinese_name', 'wbx'),
        'resolved_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 解决者: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    results.append(send_test_email(users['gh'], 'bug_resolved', event_data))
    
    # 通知负责人
    print(f"   📥 通知负责人: {users['zjn']['username']}")
    results.append(send_test_email(users['zjn'], 'bug_resolved', event_data))
    
    return all(results)

def test_rule_5_email():
    """测试规则5的邮件通知：问题关闭"""
    print("\n🎯 测试规则5邮件通知：问题关闭")
    print("   gh(实施组) 确认闭环 → 邮件通知 gh(创建者)、wbx(分配者)、zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 1001,
        'title': '【邮件测试】网络连接异常问题',
        'close_reason': '实施组确认闭环',
        'closer_name': users['gh'].get('chinese_name', 'gh'),
        'closed_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 闭环者: {users['gh']['username']} ({users['gh'].get('chinese_name', 'N/A')})")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    results.append(send_test_email(users['gh'], 'bug_closed', event_data))
    
    # 通知分配者
    print(f"   📥 通知分配者: {users['wbx']['username']}")
    results.append(send_test_email(users['wbx'], 'bug_closed', event_data))
    
    # 通知负责人
    print(f"   📥 通知负责人: {users['zjn']['username']}")
    results.append(send_test_email(users['zjn'], 'bug_closed', event_data))
    
    return all(results)

def main():
    """主函数"""
    print("📧 ReBugTracker 邮件通知实际发送测试")
    print("=" * 80)
    print("测试用户：gh(实施组) → zjn(负责人) → wbx(组内成员)")
    print("测试内容：五个通知规则的邮件实际发送")
    print("=" * 80)
    
    # 显示用户信息
    users = get_test_users()
    if users:
        print("\n👥 测试用户邮箱信息:")
        for username, info in users.items():
            email = info.get('email', '未设置')
            print(f"   {username}: {email}")
    
    # 测试邮件配置
    config_ok = test_email_config()
    if not config_ok:
        print("\n❌ 邮件配置异常，无法进行发送测试")
        return False
    
    # 执行五个规则测试
    print("\n" + "=" * 80)
    print("开始邮件发送测试...")
    
    test_functions = [
        ("规则1: 问题创建邮件", test_rule_1_email),
        ("规则2: 问题分配邮件", test_rule_2_email),
        ("规则3: 状态变更邮件", test_rule_3_email),
        ("规则4: 问题解决邮件", test_rule_4_email),
        ("规则5: 问题关闭邮件", test_rule_5_email)
    ]
    
    results = []
    for name, test_func in test_functions:
        print(f"\n⏳ 执行 {name}...")
        result = test_func()
        results.append((name, result))
        time.sleep(2)  # 避免邮件发送过快
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📊 邮件发送测试结果总结:")
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n总体结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有邮件通知测试通过！")
    else:
        print("⚠️ 部分邮件通知测试失败，请检查配置和网络")
    
    return success_count == total_count

if __name__ == "__main__":
    main()
