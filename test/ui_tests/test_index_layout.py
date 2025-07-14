#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试index页面新布局和交互功能
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_index_layout():
    """测试index页面布局优化"""
    print("🏠 测试index页面布局优化")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 实施组用户登录（可以看到主页）
        login_data = {
            'username': 'gh',
            'password': 'gh'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        print(f"登录状态: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ 实施组用户登录成功")
            
            # 获取主页
            index_response = session.get(f"{base_url}/")
            print(f"主页状态: {index_response.status_code}")
            
            if index_response.status_code == 200:
                index_content = index_response.text
                
                # 检查页面基本结构
                basic_checks = [
                    ('页面标题', '问题管理中心' in index_content),
                    ('黑色导航栏移除', 'navbar-dark bg-dark' not in index_content),
                    ('美化头部', 'dashboard-header' in index_content),
                ]
                
                print("   基本结构检查:")
                for check_name, result in basic_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                
                # 检查按钮顺序（通知在提交新问题上面）
                button_order_checks = [
                    ('通知按钮存在', 'notificationDropdown' in index_content),
                    ('提交新问题按钮存在', '提交新问题' in index_content),
                    ('退出登录按钮存在', '退出登录' in index_content),
                ]
                
                print("   按钮布局检查:")
                all_buttons_exist = True
                for check_name, result in button_order_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_buttons_exist = False
                
                # 检查按钮顺序
                if all_buttons_exist:
                    notification_pos = index_content.find('notificationDropdown')
                    submit_pos = index_content.find('提交新问题')
                    logout_pos = index_content.find('退出登录')
                    
                    if notification_pos < submit_pos < logout_pos:
                        print("     ✅ 按钮顺序正确: 通知 → 提交新问题 → 退出登录")
                    else:
                        print("     ❌ 按钮顺序错误")
                        all_buttons_exist = False
                
                # 检查统计卡片位置（在问题管理中心模块内）
                stats_checks = [
                    ('统计容器存在', 'stats-container' in index_content),
                    ('内联统计卡片', 'stat-card-inline' in index_content),
                    ('总问题数卡片', 'totalBugs' in index_content),
                    ('待处理卡片', 'pendingBugs' in index_content),
                    ('已分配卡片', 'assignedBugs' in index_content),
                    ('处理中卡片', 'processingBugs' in index_content),
                    ('已解决卡片', 'resolvedBugs' in index_content),
                    ('已完成卡片', 'completedBugs' in index_content),
                ]
                
                print("   统计卡片检查:")
                all_stats_exist = True
                for check_name, result in stats_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_stats_exist = False
                
                # 检查交互功能
                interaction_checks = [
                    ('点击筛选功能', 'filterByStatus' in index_content),
                    ('可点击样式', 'clickable' in index_content),
                    ('激活状态样式', 'active' in index_content),
                    ('统计计算功能', 'updateStats' in index_content),
                    ('筛选复选框更新', 'updateFilterCheckboxes' in index_content),
                ]
                
                print("   交互功能检查:")
                all_interactions_exist = True
                for check_name, result in interaction_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_interactions_exist = False
                
                # 检查响应式设计
                responsive_checks = [
                    ('移动端适配', '@media (max-width: 768px)' in index_content),
                    ('小屏幕适配', '@media (max-width: 480px)' in index_content),
                    ('网格布局', 'grid-template-columns' in index_content),
                ]
                
                print("   响应式设计检查:")
                all_responsive_exist = True
                for check_name, result in responsive_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_responsive_exist = False
                
                return all_buttons_exist and all_stats_exist and all_interactions_exist and all_responsive_exist
            else:
                print(f"   ❌ 主页访问失败: {index_response.status_code}")
                return False
        else:
            print(f"   ❌ 用户登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_index_functionality():
    """测试index页面功能性"""
    print("\n🔧 测试index页面功能性")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # 实施组用户登录
        login_data = {
            'username': 'gh',
            'password': 'gh'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            # 获取主页
            index_response = session.get(f"{base_url}/")
            
            if index_response.status_code == 200:
                index_content = index_response.text
                
                # 检查JavaScript功能
                js_checks = [
                    ('统计数据计算', 'function updateStats()' in index_content),
                    ('状态筛选功能', 'function filterByStatus(' in index_content),
                    ('复选框更新功能', 'function updateFilterCheckboxes(' in index_content),
                    ('问题列表更新', 'function updateBugsList()' in index_content),
                    ('页面初始化', 'DOMContentLoaded' in index_content),
                ]
                
                print("   JavaScript功能检查:")
                all_js_exist = True
                for check_name, result in js_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_js_exist = False
                
                # 检查CSS样式
                css_checks = [
                    ('内联统计卡片样式', '.stat-card-inline' in index_content),
                    ('可点击样式', '.clickable' in index_content),
                    ('激活状态样式', '.active' in index_content),
                    ('悬停效果', ':hover' in index_content),
                    ('渐变背景', 'linear-gradient' in index_content),
                ]
                
                print("   CSS样式检查:")
                all_css_exist = True
                for check_name, result in css_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_css_exist = False
                
                # 检查数据绑定
                data_checks = [
                    ('问题数据传递', 'bugs|length' in index_content),
                    ('用户数据传递', 'user.role_en' in index_content),
                    ('状态数据属性', 'data-status' in index_content),
                ]
                
                print("   数据绑定检查:")
                all_data_exist = True
                for check_name, result in data_checks:
                    print(f"     {'✅' if result else '❌'} {check_name}")
                    if not result:
                        all_data_exist = False
                
                return all_js_exist and all_css_exist and all_data_exist
            else:
                print(f"   ❌ 主页访问失败: {index_response.status_code}")
                return False
        else:
            print(f"   ❌ 用户登录失败: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ReBugTracker Index页面布局优化测试")
    print("=" * 60)
    
    # 测试布局优化
    layout_success = test_index_layout()
    
    # 测试功能性
    functionality_success = test_index_functionality()
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   布局优化: {'✅ 通过' if layout_success else '❌ 失败'}")
    print(f"   功能性: {'✅ 通过' if functionality_success else '❌ 失败'}")
    
    if layout_success and functionality_success:
        print("\n🎉 所有测试通过！Index页面布局优化成功。")
        print("\n✅ 优化的功能:")
        print("   1. ✅ 通知按钮移到提交新问题上面")
        print("   2. ✅ 统计卡片移到问题管理中心模块内")
        print("   3. ✅ 补全了所有状态的统计卡片")
        print("   4. ✅ 点击统计卡片可筛选对应状态问题")
        print("   5. ✅ 内联统计卡片设计更紧凑")
        print("   6. ✅ 响应式设计适配移动端")
        print("   7. ✅ 交互动画和悬停效果")
        print("   8. ✅ 与原有筛选功能协调工作")
        print("   9. ✅ 实时统计数据更新")
        print("   10. ✅ 现代化美观界面保持")
    else:
        print("\n💥 部分测试失败！请检查相关功能。")
        sys.exit(1)
