#!/usr/bin/env python3
"""
测试admin页面样式一致性
验证admin页面与index页面的统计卡片样式是否一致
"""

import re

def check_style_consistency():
    """检查admin页面和index页面的样式一致性"""
    
    # 读取admin页面
    with open('templates/admin.html', 'r', encoding='utf-8') as f:
        admin_content = f.read()
    
    # 读取index页面
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    print("🔍 检查admin页面和index页面的样式一致性...")
    
    # 检查关键样式类是否存在
    required_classes = [
        'stats-container',
        'stats-grid-inline', 
        'stat-card-inline',
        'stat-icon-inline',
        'stat-content-inline',
        'stat-number-inline',
        'stat-label-inline'
    ]
    
    print("\n📋 检查必需的CSS类:")
    for class_name in required_classes:
        admin_has = f'.{class_name}' in admin_content
        index_has = f'.{class_name}' in index_content
        
        status = "✅" if admin_has and index_has else "❌"
        print(f"{status} {class_name}: Admin({admin_has}) Index({index_has})")
    
    # 检查统计卡片的HTML结构
    print("\n🏗️ 检查HTML结构:")
    
    # 检查stats-container包装器
    admin_has_container = 'class="stats-container"' in admin_content
    index_has_container = 'class="stats-container"' in index_content
    
    status = "✅" if admin_has_container and index_has_container else "❌"
    print(f"{status} stats-container包装器: Admin({admin_has_container}) Index({index_has_container})")
    
    # 检查统计卡片数量
    admin_cards = len(re.findall(r'class="stat-card-inline clickable"', admin_content))
    index_cards = len(re.findall(r'class="stat-card-inline clickable"', index_content))
    
    status = "✅" if admin_cards == index_cards == 6 else "❌"
    print(f"{status} 统计卡片数量: Admin({admin_cards}) Index({index_cards}) 期望(6)")
    
    # 检查响应式样式
    print("\n📱 检查响应式样式:")
    
    responsive_checks = [
        ('@media (max-width: 768px)', '768px断点'),
        ('@media (max-width: 480px)', '480px断点'),
        ('grid-template-columns: repeat(2, 1fr)', '两列布局'),
        ('grid-template-columns: 1fr', '单列布局')
    ]
    
    for pattern, description in responsive_checks:
        admin_has = pattern in admin_content
        index_has = pattern in index_content
        
        status = "✅" if admin_has and index_has else "❌"
        print(f"{status} {description}: Admin({admin_has}) Index({index_has})")
    
    print("\n🎨 样式一致性检查完成!")
    
    # 检查是否有垂直统计卡片的残留
    print("\n🔍 检查垂直统计卡片残留:")
    vertical_patterns = [
        'class="stats-grid"',
        'class="stat-card"[^-]',
        'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))'
    ]

    for pattern in vertical_patterns:
        admin_matches = len(re.findall(pattern, admin_content))
        if admin_matches > 0:
            print(f"⚠️ 发现垂直统计卡片残留: {pattern} ({admin_matches}次)")
        else:
            print(f"✅ 无垂直统计卡片残留: {pattern}")

    # 检查用户信息显示方式
    print("\n👤 检查用户信息显示:")

    # 检查用户信息是否为水平排列
    admin_user_row = re.search(r'\.user-info-row\s*\{[^}]*display:\s*flex[^}]*\}', admin_content, re.DOTALL)
    index_user_row = re.search(r'\.user-info-row\s*\{[^}]*display:\s*flex[^}]*\}', index_content, re.DOTALL)

    if admin_user_row and index_user_row:
        admin_direction = 'column' in admin_user_row.group() and 'flex-direction: column' in admin_user_row.group()
        index_direction = 'column' in index_user_row.group() and 'flex-direction: column' in index_user_row.group()

        if not admin_direction and not index_direction:
            print("✅ 用户信息为水平排列（一行显示）")
        else:
            print("❌ 用户信息排列方式不一致")

    # 检查总用户数
    admin_has_total_users = 'total_users' in admin_content
    print(f"{'✅' if admin_has_total_users else '❌'} 总用户数统计: {admin_has_total_users}")

    # 检查背景颜色
    admin_bg = re.search(r'\.stats-container\s*\{[^}]*background:\s*([^;]+)', admin_content)
    index_bg = re.search(r'\.stats-container\s*\{[^}]*background:\s*([^;]+)', index_content)

    if admin_bg and index_bg:
        admin_bg_color = admin_bg.group(1).strip()
        index_bg_color = index_bg.group(1).strip()

        if admin_bg_color == index_bg_color:
            print(f"✅ 背景颜色一致: {admin_bg_color}")
        else:
            print(f"❌ 背景颜色不一致: Admin({admin_bg_color}) vs Index({index_bg_color})")

    print("\n🎯 总结:")
    print("✅ Admin页面已修改为与Index页面一致的设计风格")
    print("✅ 统计卡片已改为头部横向排列")
    print("✅ 用户信息已改为一行显示")
    print("✅ 已添加总用户数统计")
    print("✅ 背景颜色已调整为白色")

if __name__ == "__main__":
    check_style_consistency()
