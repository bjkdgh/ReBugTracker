#!/usr/bin/env python3
"""
检查admin和index页面的背景色一致性
"""

import re

def check_backgrounds():
    """检查背景色设置"""
    
    print("🎨 检查背景色一致性...")
    
    # 读取文件
    try:
        with open('templates/admin.html', 'r', encoding='utf-8') as f:
            admin_content = f.read()
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
    except FileNotFoundError as e:
        print(f"❌ 文件未找到: {e}")
        return
    
    # 检查stats-container背景
    admin_container_bg = re.search(r'\.stats-container\s*\{[^}]*background:\s*([^;]+)', admin_content)
    index_container_bg = re.search(r'\.stats-container\s*\{[^}]*background:\s*([^;]+)', index_content)
    
    print("\n📦 容器背景色 (stats-container):")
    if admin_container_bg and index_container_bg:
        admin_bg = admin_container_bg.group(1).strip()
        index_bg = index_container_bg.group(1).strip()
        
        if admin_bg == index_bg:
            print(f"✅ 一致: {admin_bg}")
        else:
            print(f"❌ 不一致: Admin({admin_bg}) vs Index({index_bg})")
    else:
        print("❌ 未找到容器背景设置")
    
    # 检查stat-card-inline背景
    admin_card_bg = re.search(r'\.stat-card-inline\s*\{[^}]*background:\s*([^;]+)', admin_content)
    index_card_bg = re.search(r'\.stat-card-inline\s*\{[^}]*background:\s*([^;]+)', index_content)
    
    print("\n🎴 卡片背景色 (stat-card-inline):")
    if admin_card_bg and index_card_bg:
        admin_card = admin_card_bg.group(1).strip()
        index_card = index_card_bg.group(1).strip()
        
        if admin_card == index_card:
            print(f"✅ 一致: {admin_card}")
        else:
            print(f"❌ 不一致: Admin({admin_card}) vs Index({index_card})")
    else:
        print("❌ 未找到卡片背景设置")
    
    print("\n💡 说明:")
    print("- stats-container: 统计卡片区域的容器背景 (浅灰色)")
    print("- stat-card-inline: 每个统计卡片的背景 (白色)")
    print("- 您看到的白色是卡片背景，这是正确的设计")
    print("- 容器的浅灰色背景在卡片之间的间隙中可见")

if __name__ == "__main__":
    check_backgrounds()
