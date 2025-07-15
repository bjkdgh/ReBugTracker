#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用内通知的实际发送功能
使用gh、zjn、wbx三个用户测试五个通知规则的应用内通知
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
                SELECT id, username, chinese_name, role
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
                        'role': result[3]
                    }
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")
        return {}

def test_inapp_config():
    """测试应用内通知配置"""
    print("📱 测试应用内通知配置")
    print("-" * 50)
    
    try:
        from notification.channels.inapp_notifier import InAppNotifier
        
        notifier = InAppNotifier()
        
        print(f"   启用状态: {notifier.is_enabled()}")  # 应该总是True
        
        # 检查数据库表是否存在
        from db_factory import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM notifications LIMIT 1")
            print(f"   数据库表: 正常")
            table_ok = True
        except Exception as e:
            print(f"   数据库表: 异常 - {e}")
            table_ok = False
        
        conn.close()
        
        return notifier.is_enabled() and table_ok
        
    except Exception as e:
        print(f"   ❌ 应用内通知配置测试失败: {e}")
        return False

def send_test_inapp(user_info, event_type, event_data):
    """发送测试应用内通知"""
    try:
        from notification.channels.inapp_notifier import InAppNotifier
        
        notifier = InAppNotifier()
        
        # 生成通知内容
        from notification.simple_notifier import SimpleNotifier
        simple_notifier = SimpleNotifier()
        
        user_display_info = {
            'name': user_info.get('chinese_name') or user_info['username']
        }
        
        content_data = simple_notifier._generate_content(event_type, event_data, user_display_info)
        
        # 发送应用内通知
        recipient = {
            'id': user_info['id'],
            'name': user_display_info['name']
        }
        
        success = notifier.send(
            title=content_data['title'],
            content=content_data['content'],
            recipient=recipient,
            priority=content_data['priority'],
            metadata=content_data.get('metadata', {})
        )
        
        if success:
            print(f"      ✅ 应用内通知创建成功 → {user_info['username']}")
        else:
            print(f"      ❌ 应用内通知创建失败 → {user_info['username']}")
        
        return success
        
    except Exception as e:
        print(f"      ❌ 应用内通知异常: {e}")
        return False

def check_notification_in_db(user_id, title_keyword):
    """检查数据库中的通知记录"""
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query, params = adapt_sql("""
            SELECT id, title, content, created_at, read_status
            FROM notifications
            WHERE user_id = %s AND title LIKE %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id, f'%{title_keyword}%'))
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            if hasattr(result, 'keys'):
                return {
                    'id': result['id'],
                    'title': result['title'],
                    'content': result['content'],
                    'created_at': result['created_at'],
                    'read_status': result['read_status']
                }
            else:
                return {
                    'id': result[0],
                    'title': result[1],
                    'content': result[2],
                    'created_at': result[3],
                    'read_status': result[4]
                }
        
        return None
        
    except Exception as e:
        print(f"      ⚠️ 检查数据库记录失败: {e}")
        return None

def test_rule_1_inapp():
    """测试规则1的应用内通知：问题创建"""
    print("\n🆕 测试规则1应用内通知：问题创建")
    print("   gh(实施组) 创建问题 → 应用内通知 zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 3001,
        'title': '【应用内测试】服务器内存不足',
        'description': '生产服务器内存使用率超过90%，需要紧急处理',
        'creator_name': users['gh'].get('chinese_name', 'gh'),
        'created_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'creator_id': users['gh']['id'],
        'assigned_manager_id': users['zjn']['id']
    }
    
    print(f"   📤 创建者: {users['gh']['username']} ({users['gh'].get('chinese_name', 'N/A')})")
    print(f"   📥 通知对象: {users['zjn']['username']} ({users['zjn'].get('chinese_name', 'N/A')})")
    
    success = send_test_inapp(users['zjn'], 'bug_created', event_data)
    
    if success:
        # 验证数据库记录
        notification = check_notification_in_db(users['zjn']['id'], '有新的提交问题')
        if notification:
            print(f"      ✅ 数据库记录验证成功: {notification['title']}")
        else:
            print(f"      ⚠️ 数据库记录验证失败")
    
    return success

def test_rule_2_inapp():
    """测试规则2的应用内通知：问题分配"""
    print("\n🔔 测试规则2应用内通知：问题分配")
    print("   zjn(负责人) 分配问题 → 应用内通知 wbx(组内成员)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 3001,
        'title': '【应用内测试】服务器内存不足',
        'description': '生产服务器内存使用率超过90%，需要紧急处理',
        'assigner_name': users['zjn'].get('chinese_name', 'zjn'),
        'assigned_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'assignee_id': users['wbx']['id']
    }
    
    print(f"   📤 分配者: {users['zjn']['username']} ({users['zjn'].get('chinese_name', 'N/A')})")
    print(f"   📥 通知对象: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    
    success = send_test_inapp(users['wbx'], 'bug_assigned', event_data)
    
    if success:
        # 验证数据库记录
        notification = check_notification_in_db(users['wbx']['id'], '问题分配给您')
        if notification:
            print(f"      ✅ 数据库记录验证成功: {notification['title']}")
        else:
            print(f"      ⚠️ 数据库记录验证失败")
    
    return success

def test_rule_3_inapp():
    """测试规则3的应用内通知：状态变更"""
    print("\n🔄 测试规则3应用内通知：状态变更")
    print("   wbx(组内成员) 更新状态 → 应用内通知 gh(创建者) 和 wbx(分配者)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 3001,
        'title': '【应用内测试】服务器内存不足',
        'old_status': '已分配',
        'new_status': '处理中',
        'operator_name': users['wbx'].get('chinese_name', 'wbx'),
        'updated_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 操作者: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    success1 = send_test_inapp(users['gh'], 'bug_status_changed', event_data)
    results.append(success1)
    
    if success1:
        notification = check_notification_in_db(users['gh']['id'], '问题状态更新')
        if notification:
            print(f"      ✅ 创建者通知数据库记录验证成功")
    
    # 通知分配者（自己）
    print(f"   📥 通知分配者: {users['wbx']['username']}")
    success2 = send_test_inapp(users['wbx'], 'bug_status_changed', event_data)
    results.append(success2)
    
    if success2:
        notification = check_notification_in_db(users['wbx']['id'], '问题状态更新')
        if notification:
            print(f"      ✅ 分配者通知数据库记录验证成功")
    
    return all(results)

def test_rule_4_inapp():
    """测试规则4的应用内通知：问题解决"""
    print("\n✅ 测试规则4应用内通知：问题解决")
    print("   wbx(组内成员) 解决问题 → 应用内通知 gh(创建者) 和 zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 3001,
        'title': '【应用内测试】服务器内存不足',
        'solution': '已清理临时文件并增加内存，问题已解决',
        'resolver_name': users['wbx'].get('chinese_name', 'wbx'),
        'resolved_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 解决者: {users['wbx']['username']} ({users['wbx'].get('chinese_name', 'N/A')})")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    success1 = send_test_inapp(users['gh'], 'bug_resolved', event_data)
    results.append(success1)
    
    if success1:
        notification = check_notification_in_db(users['gh']['id'], '问题已解决')
        if notification:
            print(f"      ✅ 创建者通知数据库记录验证成功")
    
    # 通知负责人
    print(f"   📥 通知负责人: {users['zjn']['username']}")
    success2 = send_test_inapp(users['zjn'], 'bug_resolved', event_data)
    results.append(success2)
    
    if success2:
        notification = check_notification_in_db(users['zjn']['id'], '问题已解决')
        if notification:
            print(f"      ✅ 负责人通知数据库记录验证成功")
    
    return all(results)

def test_rule_5_inapp():
    """测试规则5的应用内通知：问题关闭"""
    print("\n🎯 测试规则5应用内通知：问题关闭")
    print("   gh(实施组) 确认闭环 → 应用内通知 gh(创建者)、wbx(分配者)、zjn(负责人)")
    print("-" * 50)
    
    users = get_test_users()
    if not users:
        return False
    
    event_data = {
        'bug_id': 3001,
        'title': '【应用内测试】服务器内存不足',
        'close_reason': '实施组确认闭环',
        'closer_name': users['gh'].get('chinese_name', 'gh'),
        'closed_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"   📤 闭环者: {users['gh']['username']} ({users['gh'].get('chinese_name', 'N/A')})")
    
    results = []
    
    # 通知创建者
    print(f"   📥 通知创建者: {users['gh']['username']}")
    success1 = send_test_inapp(users['gh'], 'bug_closed', event_data)
    results.append(success1)
    
    # 通知分配者
    print(f"   📥 通知分配者: {users['wbx']['username']}")
    success2 = send_test_inapp(users['wbx'], 'bug_closed', event_data)
    results.append(success2)
    
    # 通知负责人
    print(f"   📥 通知负责人: {users['zjn']['username']}")
    success3 = send_test_inapp(users['zjn'], 'bug_closed', event_data)
    results.append(success3)
    
    # 验证数据库记录
    if all(results):
        print(f"      ✅ 所有应用内通知创建成功")
        for username, user_info in [('gh', users['gh']), ('wbx', users['wbx']), ('zjn', users['zjn'])]:
            notification = check_notification_in_db(user_info['id'], '问题已关闭')
            if notification:
                print(f"      ✅ {username}的数据库记录验证成功")
    
    return all(results)

def get_notification_statistics():
    """获取通知统计信息"""
    print("\n📊 应用内通知统计信息")
    print("-" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 总通知数
        query, params = adapt_sql("SELECT COUNT(*) FROM notifications", ())
        cursor.execute(query, params)
        total_count = cursor.fetchone()[0]
        
        # 未读通知数
        query, params = adapt_sql("SELECT COUNT(*) FROM notifications WHERE read_status = false", ())
        cursor.execute(query, params)
        unread_count = cursor.fetchone()[0]
        
        # 今日通知数
        query, params = adapt_sql("""
            SELECT COUNT(*) FROM notifications 
            WHERE DATE(created_at) = CURRENT_DATE
        """, ())
        cursor.execute(query, params)
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"   总通知数: {total_count}")
        print(f"   未读通知数: {unread_count}")
        print(f"   今日通知数: {today_count}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 获取统计信息失败: {e}")
        return False

def main():
    """主函数"""
    print("📱 ReBugTracker 应用内通知实际发送测试")
    print("=" * 80)
    print("测试用户：gh(实施组) → zjn(负责人) → wbx(组内成员)")
    print("测试内容：五个通知规则的应用内通知实际创建")
    print("=" * 80)
    
    # 显示用户信息
    users = get_test_users()
    if users:
        print("\n👥 测试用户信息:")
        for username, info in users.items():
            print(f"   {username}: ID={info['id']}, 姓名={info.get('chinese_name', 'N/A')}")
    
    # 测试应用内通知配置
    config_ok = test_inapp_config()
    if not config_ok:
        print("\n❌ 应用内通知配置异常，无法进行测试")
        return False
    
    # 获取测试前的统计信息
    get_notification_statistics()
    
    # 执行五个规则测试
    print("\n" + "=" * 80)
    print("开始应用内通知测试...")
    
    test_functions = [
        ("规则1: 问题创建通知", test_rule_1_inapp),
        ("规则2: 问题分配通知", test_rule_2_inapp),
        ("规则3: 状态变更通知", test_rule_3_inapp),
        ("规则4: 问题解决通知", test_rule_4_inapp),
        ("规则5: 问题关闭通知", test_rule_5_inapp)
    ]
    
    results = []
    for name, test_func in test_functions:
        print(f"\n⏳ 执行 {name}...")
        result = test_func()
        results.append((name, result))
        time.sleep(0.5)  # 短暂延迟
    
    # 获取测试后的统计信息
    print("\n" + "=" * 50)
    print("测试后统计:")
    get_notification_statistics()
    
    # 总结结果
    print("\n" + "=" * 80)
    print("📊 应用内通知测试结果总结:")
    
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失败"
        print(f"   {name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n总体结果: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("🎉 所有应用内通知测试通过！")
        print("💡 您可以登录系统查看通知中心的新通知")
    else:
        print("⚠️ 部分应用内通知测试失败，请检查数据库配置")
    
    return success_count == total_count

if __name__ == "__main__":
    main()
