#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试问题关闭通知功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_notification_flow_rules():
    """测试通知流转规则"""
    print("🔔 测试通知流转规则")
    print("=" * 50)
    
    try:
        from notification.flow_rules import FlowNotificationRules
        
        # 测试问题关闭通知目标
        print("1. 测试问题关闭通知目标...")

        event_data = {
            'bug_id': 1,
            'title': '测试问题',
            'creator_id': '2',  # 实施组用户 gh
            'assignee_id': '4',  # 组内成员 wbx (网络分析团队)
            'close_reason': '实施组确认闭环',
            'closer_name': '测试用户'
        }
        
        targets = FlowNotificationRules.get_notification_targets('bug_closed', event_data)
        
        print(f"   通知目标用户数: {len(targets)}")
        print(f"   目标用户ID: {list(targets)}")
        
        # 验证通过组内成员找到的负责人
        from notification.flow_rules import FlowNotificationRules
        assignee_manager = FlowNotificationRules._get_manager_by_assignee(event_data['assignee_id'])
        print(f"   组内成员 {event_data['assignee_id']} 的负责人: {assignee_manager}")

        # 检查是否包含创建者、分配者和负责人
        creator_included = event_data['creator_id'] in targets
        assignee_included = event_data['assignee_id'] in targets
        manager_included = assignee_manager and assignee_manager in targets

        print(f"   是否包含创建者: {'✅' if creator_included else '❌'}")
        print(f"   是否包含分配者: {'✅' if assignee_included else '❌'}")
        print(f"   是否包含相关负责人: {'✅' if manager_included else '❌'}")

        return len(targets) > 0 and creator_included and assignee_included and manager_included
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_template():
    """测试通知模板"""
    print("\n2. 测试通知模板...")

    try:
        from notification.simple_notifier import SimpleNotifier

        notifier = SimpleNotifier()

        # 测试问题关闭通知模板
        event_data = {
            'title': '测试问题标题',
            'close_reason': '实施组确认闭环',
            'closer_name': '张三',
            'closed_time': '2025-07-14 22:45:00'
        }

        # 模拟用户信息
        user_info = {'name': '测试用户'}

        # 使用内部方法测试模板
        result = notifier._generate_content('bug_closed', event_data, user_info)
        title = result['title']
        content = result['content']

        print(f"   通知标题: {title}")
        print(f"   通知内容: {content}")

        # 验证模板是否正确填充
        template_filled = all([
            event_data['title'] in content,
            event_data['close_reason'] in content,
            event_data['closer_name'] in content
        ])

        print(f"   模板填充正确: {'✅' if template_filled else '❌'}")

        return template_filled

    except Exception as e:
        print(f"❌ 模板测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_manager():
    """测试通知管理器"""
    print("\n3. 测试通知管理器...")

    try:
        from notification.notification_manager import NotificationManager

        # 检查通知是否启用
        enabled = NotificationManager.is_notification_enabled()
        print(f"   服务器通知启用: {'✅' if enabled else '❌'}")

        return enabled

    except Exception as e:
        print(f"❌ 通知管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🧪 ReBugTracker 问题关闭通知功能测试")
    print("=" * 60)
    
    results = []
    
    # 测试通知流转规则
    results.append(test_notification_flow_rules())
    
    # 测试通知模板
    results.append(test_notification_template())
    
    # 测试通知管理器
    results.append(test_notification_manager())
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    test_names = [
        "通知流转规则",
        "通知模板",
        "通知管理器"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {i+1}. {name}: {status}")
    
    all_passed = all(results)
    print(f"\n总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    
    if all_passed:
        print("\n💡 问题关闭通知功能已正确实现！")
        print("   当问题状态变为'已完成'时，将通知:")
        print("   - 问题创建者（实施组）")
        print("   - 问题分配者（组内成员）")
        print("   - 相关负责人（该组内成员所在团队的负责人）")
    else:
        print("\n⚠️ 问题关闭通知功能存在问题，需要进一步检查。")
    
    return all_passed

if __name__ == "__main__":
    main()
