#!/usr/bin/env python3
"""
测试Admin页面JavaScript修复
检查是否修复了JavaScript错误
"""

def test_js_fix():
    """测试JavaScript修复"""
    
    print("🔧 测试Admin页面JavaScript修复...")
    
    try:
        with open('templates/admin.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ 找不到admin.html文件")
        return
    
    checks = []
    
    # 1. 检查是否删除了有问题的calculateBugStats函数
    has_calculate_bug_stats = 'function calculateBugStats()' in content
    checks.append(("删除calculateBugStats函数", not has_calculate_bug_stats))
    
    # 2. 检查是否删除了对不存在元素的引用
    has_pending_bugs_count = 'pendingBugsCount' in content
    has_resolved_bugs_count = 'resolvedBugsCount' in content
    checks.append(("删除不存在的元素引用", not has_pending_bugs_count and not has_resolved_bugs_count))
    
    # 3. 检查updateStats函数是否使用正确的变量名
    has_bugs_data = 'const bugsData = {{ bugs|tojson|safe }};' in content
    checks.append(("使用正确的变量名bugsData", has_bugs_data))
    
    # 4. 检查是否只有一个DOMContentLoaded监听器
    dom_content_loaded_count = content.count("document.addEventListener('DOMContentLoaded'")
    has_single_dom_listener = dom_content_loaded_count == 1
    checks.append(("单一DOMContentLoaded监听器", has_single_dom_listener))
    
    # 5. 检查是否在DOMContentLoaded中调用updateStats
    has_update_stats_call = 'updateStats();' in content
    checks.append(("调用updateStats函数", has_update_stats_call))
    
    # 6. 检查是否移除了对calculateBugStats的调用
    has_calculate_call = 'calculateBugStats();' in content
    checks.append(("移除calculateBugStats调用", not has_calculate_call))
    
    # 输出结果
    print("\n📋 检查结果:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有JavaScript错误都已修复！")
        print("现在admin页面应该不会再出现以下错误：")
        print("- Cannot set properties of null (setting 'textContent')")
        print("- Cannot redeclare block-scoped variable 'bugs'")
        print("- 重复的DOMContentLoaded监听器")
    else:
        print("\n⚠️ 部分修复未完成，请检查。")

if __name__ == "__main__":
    test_js_fix()
