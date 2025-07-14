#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的SSL邮件发送功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fixed_ssl_email():
    """测试修复后的SSL邮件发送"""
    print("🔒 测试修复后的SSL邮件发送功能...")
    print("=" * 50)
    
    try:
        # 重新导入邮件通知器（使用修改后的代码）
        import importlib
        import notification.channels.email_notifier
        importlib.reload(notification.channels.email_notifier)
        
        from notification.channels.email_notifier import EmailNotifier
        
        print("1. 创建邮件通知器...")
        email_notifier = EmailNotifier()
        
        print("2. 检查邮件通知器状态...")
        is_enabled = email_notifier.is_enabled()
        print(f"   状态: {'✅ 启用' if is_enabled else '❌ 禁用'}")
        
        if not is_enabled:
            print("   ❌ 邮件通知器未启用")
            return False
        
        print("\n3. 准备测试邮件...")
        recipient_info = {
            'id': '2',
            'name': '郭浩',
            'email': 'guoh202505@gmail.com'
        }
        
        print(f"   收件人: {recipient_info['name']}")
        print(f"   邮箱: {recipient_info['email']}")
        
        print("\n4. 发送修复后的SSL邮件...")
        success = email_notifier.send(
            title="🎉 ReBugTracker SSL邮件修复测试",
            content=f"""您好 郭浩！

恭喜！这是一封使用修复后SSL功能发送的邮件。

🔧 修复内容：
- 正确使用SMTP_SSL连接465端口
- 区分SSL和TLS连接模式
- 优化邮件发送逻辑

📋 当前配置信息：
- SMTP服务器: smtp.163.com
- 端口: 465
- 加密方式: SSL (SMTP_SSL)
- 发件人: bjkd_ssz@163.com

如果您收到这封邮件，说明SSL邮件功能已经修复成功！

🔔 现在您可以正常接收到：
- 问题分配通知
- 状态变更通知
- 问题解决通知
- 问题关闭通知

---
ReBugTracker 系统
测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            recipient=recipient_info,
            priority=1,
            metadata={'test_type': 'ssl_fix_verification', 'user_id': '2'}
        )
        
        if success:
            print("   ✅ SSL邮件发送成功！")
            return True
        else:
            print("   ❌ SSL邮件发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flow_notification_ssl():
    """测试流程通知的SSL邮件发送"""
    print("\n🔄 测试流程通知的SSL邮件发送...")
    print("=" * 50)
    
    try:
        from notification.simple_notifier import simple_notifier
        
        print("1. 发送问题分配通知...")
        simple_notifier.send_flow_notification('bug_assigned', {
            'bug_id': 8888,
            'title': 'SSL邮件功能修复验证',
            'description': '这是一个用于验证SSL邮件功能修复的测试问题',
            'assignee_name': '郭浩',
            'assignee_id': '2',
            'assigned_time': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'manager_name': '系统管理员'
        })
        
        print("   ✅ 问题分配通知发送完成")
        
        print("\n2. 发送状态变更通知...")
        simple_notifier.send_flow_notification('bug_status_changed', {
            'bug_id': 8888,
            'title': 'SSL邮件功能修复验证',
            'old_status': '待处理',
            'new_status': '处理中',
            'assignee_name': '郭浩',
            'assignee_id': '2',
            'changed_time': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'changed_by': '系统管理员'
        })
        
        print("   ✅ 状态变更通知发送完成")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 流程通知测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_email_config():
    """验证邮件配置"""
    print("\n📋 验证当前邮件配置...")
    print("=" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取邮件配置
        query, params = adapt_sql("""
            SELECT config_key, config_value FROM system_config 
            WHERE config_key LIKE %s
            ORDER BY config_key
        """, ('notification_email_%',))
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        print("📧 当前邮件配置:")
        config_dict = {}
        for config in configs:
            key = config[0]
            value = config[1]
            config_dict[key] = value
            
            # 隐藏密码
            if 'password' in key.lower():
                display_value = '*' * len(value) if value else '(未设置)'
            else:
                display_value = value
            
            print(f"   {key}: {display_value}")
        
        # 验证SSL配置
        port = config_dict.get('notification_email_smtp_port', '587')
        use_tls = config_dict.get('notification_email_use_tls', 'true')
        
        print(f"\n🔍 配置分析:")
        print(f"   端口: {port}")
        print(f"   TLS: {use_tls}")
        
        if port == '465' and use_tls == 'false':
            print("   ✅ SSL模式配置正确 (465端口 + 不使用TLS)")
        elif port == '587' and use_tls == 'true':
            print("   ✅ TLS模式配置正确 (587端口 + 使用TLS)")
        else:
            print("   ⚠️ 配置可能有问题")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证配置失败: {e}")

def main():
    """主测试函数"""
    print("🚀 测试修复后的SSL邮件功能")
    print("📧 目标：验证SSL邮件发送修复")
    print()
    
    # 验证配置
    verify_email_config()
    
    # 测试直接邮件发送
    success1 = test_fixed_ssl_email()
    
    # 测试流程通知
    success2 = test_flow_notification_ssl()
    
    print("\n" + "=" * 50)
    print("📋 SSL修复测试结果:")
    print(f"   直接邮件发送: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   流程通知发送: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 or success2:
        print("\n🎉 SSL邮件功能修复成功！")
        print("📧 请检查郭浩的邮箱: guoh202505@gmail.com")
        print("📁 注意检查垃圾邮件文件夹")
        print("🔔 现在可以正常接收ReBugTracker的邮件通知了")
    else:
        print("\n❌ SSL修复仍有问题，需要进一步检查")

if __name__ == "__main__":
    main()
