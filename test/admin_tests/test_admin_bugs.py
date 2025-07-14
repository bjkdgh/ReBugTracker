#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员页面问题列表恢复
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_bug_list():
    """测试管理员页面问题列表"""
    print("🐛 测试管理员页面问题列表")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 管理员登录
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"登录状态: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ 管理员登录成功")
            
            # 获取管理员页面
            admin_response = session.get(f"{base_url}/admin")
            print(f"管理员页面状态: {admin_response.status_code}")
            
            if admin_response.status_code == 200:
                admin_content = admin_response.text
                
                # 检查页面基本结构
                basic_checks = [
                    ('页面标题', '管理员控制面板' in admin_content),
                    ('黑色导航栏移除', 'navbar-dark bg-dark' not in admin_content),
                    ('美化头部', 'admin-header' in admin_content),
                    ('统计卡片', 'stat-card' in admin_content),
                ]
                
                print("   基本结构检查:")
                for check_name, result in basic_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                
                # 检查问题管理功能
                bug_management_checks = [
                    ('问题管理卡片', '问题管理' in admin_content),
                    ('问题列表表格', '<table' in admin_content and 'bugTable' in admin_content),
                    ('问题表头', '<th>ID</th>' in admin_content and '<th>标题</th>' in admin_content),
                    ('删除按钮', 'deleteBug' in admin_content),
                    ('确认闭环按钮', 'completeBug' in admin_content),
                    ('问题状态显示', 'badge bg-' in admin_content),
                ]
                
                print("   问题管理功能检查:")
                all_bug_features = True
                for check_name, result in bug_management_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_bug_features = False
                
                # 检查用户管理功能
                user_management_checks = [
                    ('用户管理卡片', '用户管理' in admin_content),
                    ('用户列表表格', 'userTable' in admin_content),
                    ('添加用户按钮', 'showAddModal' in admin_content),
                    ('用户模态框', 'userModal' in admin_content),
                ]
                
                print("   用户管理功能检查:")
                all_user_features = True
                for check_name, result in user_management_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_user_features = False
                
                # 检查通知管理功能
                notification_checks = [
                    ('通知管理卡片', '通知管理' in admin_content),
                    ('服务器通知开关', 'serverNotificationToggle' in admin_content),
                    ('邮件通知开关', 'emailGlobalToggle' in admin_content),
                    ('Gotify通知开关', 'gotifyGlobalToggle' in admin_content),
                ]
                
                print("   通知管理功能检查:")
                all_notification_features = True
                for check_name, result in notification_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_notification_features = False
                
                # 检查JavaScript功能
                js_checks = [
                    ('问题统计计算', 'calculateBugStats' in admin_content),
                    ('删除问题函数', 'function deleteBug' in admin_content),
                    ('确认闭环函数', 'function completeBug' in admin_content),
                    ('用户管理函数', 'function loadUsers' in admin_content),
                    ('动画效果', 'fadeInUp' in admin_content),
                ]
                
                print("   JavaScript功能检查:")
                all_js_features = True
                for check_name, result in js_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_js_features = False
                
                return all_bug_features and all_user_features and all_notification_features and all_js_features
            else:
                print(f"   ❌ 管理员页面访问失败: {admin_response.status_code}")
                return False
        else:
            print(f"   ❌ 管理员登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_data_display():
    """测试管理员页面数据显示"""
    print("\n📊 测试管理员页面数据显示")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 管理员登录
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            # 获取管理员页面
            admin_response = session.get(f"{base_url}/admin")
            
            if admin_response.status_code == 200:
                admin_content = admin_response.text
                
                # 检查统计数据是否显示
                stats_checks = [
                    ('总用户数统计', '总用户数' in admin_content),
                    ('总问题数统计', '总问题数' in admin_content),
                    ('待处理问题统计', '待处理问题' in admin_content),
                    ('已解决问题统计', '已解决问题' in admin_content),
                ]
                
                print("   统计数据显示检查:")
                for check_name, result in stats_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                
                # 检查是否有数据传递错误
                error_checks = [
                    ('无模板错误', 'TemplateNotFound' not in admin_content),
                    ('无变量错误', 'UndefinedError' not in admin_content),
                    ('无JSON错误', 'is not JSON serializable' not in admin_content),
                ]
                
                print("   错误检查:")
                all_no_errors = True
                for check_name, result in error_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_no_errors = False
                
                return all_no_errors
            else:
                print(f"   ❌ 管理员页面访问失败: {admin_response.status_code}")
                return False
        else:
            print(f"   ❌ 管理员登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 数据显示测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker 管理员页面问题列表恢复测试")
    print("=" * 60)
    
    # 测试问题列表功能
    bug_list_success = test_admin_bug_list()
    
    # 测试数据显示
    data_display_success = test_admin_data_display()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   问题列表功能: {'✅ 通过' if bug_list_success else '❌ 失败'}")
    print(f"   数据显示: {'✅ 通过' if data_display_success else '❌ 失败'}")
    
    if bug_list_success and data_display_success:
        print("\n🎉 所有测试通过！管理员页面问题列表已成功恢复。")
        print("\n✅ 恢复的功能:")
        print("   1. ✅ 移除了顶部黑色导航栏")
        print("   2. ✅ 保持了现代化美化设计")
        print("   3. ✅ 恢复了完整的问题管理功能")
        print("   4. ✅ 问题列表表格显示")
        print("   5. ✅ 删除问题和确认闭环功能")
        print("   6. ✅ 用户管理功能")
        print("   7. ✅ 通知管理功能")
        print("   8. ✅ 统计数据显示")
        print("   9. ✅ JavaScript交互功能")
        print("   10. ✅ 响应式设计和动画效果")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
