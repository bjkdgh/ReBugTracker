#!/usr/bin/env python3
"""
验证透明背景修改
检查统计卡片是否已改为透明背景
"""

def verify_transparent_background():
    """验证透明背景修改"""
    
    print("🎨 验证统计卡片透明背景修改...")
    
    files_to_check = ['templates/admin.html', 'templates/index.html']
    
    for file_path in files_to_check:
        print(f"\n📄 检查文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ 找不到文件: {file_path}")
            continue
        
        checks = []
        
        # 1. 检查是否使用透明背景
        has_transparent_bg = 'background: rgba(255, 255, 255, 0.15);' in content
        checks.append(("透明背景", has_transparent_bg))
        
        # 2. 检查是否有毛玻璃效果
        has_backdrop_filter = 'backdrop-filter: blur(10px);' in content
        checks.append(("毛玻璃效果", has_backdrop_filter))
        
        # 3. 检查是否有半透明边框
        has_transparent_border = 'border: 1px solid rgba(255, 255, 255, 0.2);' in content
        checks.append(("半透明边框", has_transparent_border))
        
        # 4. 检查文字颜色是否为白色
        has_white_text = 'color: white;' in content and 'text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);' in content
        checks.append(("白色文字+阴影", has_white_text))
        
        # 5. 检查标签文字是否为半透明白色
        has_semi_white_label = 'color: rgba(255, 255, 255, 0.9);' in content
        checks.append(("半透明白色标签", has_semi_white_label))
        
        # 6. 检查是否移除了原来的白色背景
        no_white_bg = 'background: white;' not in content
        checks.append(("移除白色背景", no_white_bg))
        
        # 输出结果
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print(f"  🎉 {file_path} 透明背景修改完成！")
        else:
            print(f"  ⚠️ {file_path} 部分修改未完成")
    
    print("\n🎯 透明背景效果说明:")
    print("- 统计卡片现在使用半透明白色背景 (15% 透明度)")
    print("- 添加了毛玻璃模糊效果 (backdrop-filter)")
    print("- 使用半透明白色边框")
    print("- 文字改为白色并添加阴影以提高可读性")
    print("- 这样可以更好地显示底层的蓝紫色渐变背景")

if __name__ == "__main__":
    verify_transparent_background()
