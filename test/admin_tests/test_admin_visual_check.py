#!/usr/bin/env python3
"""
Admin页面视觉检查工具
验证admin页面的关键修改是否正确应用
"""

def check_admin_modifications():
    """检查admin页面的关键修改"""
    
    print("🔍 检查Admin页面修改...")
    
    try:
        with open('templates/admin.html', 'r', encoding='utf-8') as f:
            admin_content = f.read()
    except FileNotFoundError:
        print("❌ 找不到admin.html文件")
        return
    
    checks = []
    
    # 1. 检查用户信息是否为水平排列
    user_info_horizontal = (
        'display: flex;' in admin_content and
        'align-items: center;' in admin_content and
        'gap: 15px;' in admin_content and
        'flex-direction: column' not in admin_content.split('.user-info-row')[1].split('}')[0]
    )
    checks.append(("用户信息水平排列", user_info_horizontal))
    
    # 2. 检查是否有总用户数统计卡片
    has_total_users_card = (
        'data-status="users"' in admin_content and
        'totalUsers' in admin_content and
        '总用户数' in admin_content and
        'fas fa-users' in admin_content
    )
    checks.append(("总用户数统计卡片", has_total_users_card))
    
    # 3. 检查stats-container背景是否为#f8f9fa
    correct_background = 'background: #f8f9fa;' in admin_content
    checks.append(("正确背景色(#f8f9fa)", correct_background))
    
    # 4. 检查是否有stats-container包装器
    has_stats_container = 'class="stats-container"' in admin_content
    checks.append(("stats-container包装器", has_stats_container))
    
    # 5. 检查统计卡片样式是否与index一致
    consistent_card_style = (
        'background: white;' in admin_content and
        'padding: 10px;' in admin_content and
        'border-radius: 8px;' in admin_content and
        'gap: 8px;' in admin_content
    )
    checks.append(("统计卡片样式一致", consistent_card_style))

    # 6. 检查是否有7个统计卡片
    stat_cards_count = admin_content.count('class="stat-card-inline')
    has_seven_cards = stat_cards_count >= 7
    checks.append(("7个统计卡片", has_seven_cards))
    
    # 7. 检查响应式样式
    responsive_styles = (
        '@media (max-width: 768px)' in admin_content and
        '@media (max-width: 480px)' in admin_content and
        'grid-template-columns: repeat(2, 1fr)' in admin_content and
        'grid-template-columns: 1fr' in admin_content
    )
    checks.append(("响应式样式", responsive_styles))
    
    # 输出检查结果
    print("\n📋 检查结果:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查都通过！Admin页面已成功修改为与Index页面一致的风格。")
    else:
        print("\n⚠️ 部分检查未通过，请检查相关修改。")
    
    # 检查rebugtracker.py中的total_users传递
    print("\n🔍 检查后端代码...")
    try:
        with open('rebugtracker.py', 'r', encoding='utf-8') as f:
            backend_content = f.read()
        
        total_users_backend = (
            'total_users = len(users)' in backend_content and
            'total_users=total_users' in backend_content
        )
        
        status = "✅" if total_users_backend else "❌"
        print(f"{status} 后端total_users传递")
        
    except FileNotFoundError:
        print("❌ 找不到rebugtracker.py文件")

if __name__ == "__main__":
    check_admin_modifications()
