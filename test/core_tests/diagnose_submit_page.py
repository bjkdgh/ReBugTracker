#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker - Submit页面诊断脚本

诊断submit页面的问题
"""

import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_submit_page():
    """诊断submit页面问题"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 ReBugTracker - Submit页面诊断")
    print("=" * 50)
    
    # 创建会话
    session = requests.Session()
    
    try:
        # 1. 登录为实施组用户
        print("1. 登录为实施组用户...")
        login_data = {
            'username': 'gh',
            'password': 'gh123'
        }
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code != 200:
            print("❌ 登录失败")
            return False
        print("✅ 登录成功")
        
        # 2. 访问submit页面
        print("\n2. 访问submit页面...")
        response = session.get(f"{base_url}/submit")
        
        if response.status_code == 200:
            print("✅ submit页面访问成功")
            content = response.text
            
            # 保存页面内容到文件以便检查
            with open('test/submit_page_content.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("📄 页面内容已保存到 test/submit_page_content.html")
            
            # 检查关键元素
            print("\n3. 检查页面关键元素...")
            
            checks = [
                ("页面标题", "提交新问题需求" in content),
                ("现代化头部", "submit-header" in content),
                ("表单卡片", "form-card" in content),
                ("Bootstrap CSS", "bootstrap" in content),
                ("Font Awesome", "font-awesome" in content or "fas fa-" in content),
                ("用户信息", "郭浩" in content or "gh" in content),
                ("负责人选项", "李世杰" in content and "张佳楠" in content),
                ("现代化样式", "linear-gradient" in content),
                ("JavaScript", "DOMContentLoaded" in content),
                ("表单验证", "validation-message" in content)
            ]
            
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name}")
            
            # 检查页面大小
            print(f"\n📊 页面大小: {len(content)} 字符")
            
            # 检查是否有错误信息
            if "error" in content.lower() or "exception" in content.lower():
                print("⚠️  页面可能包含错误信息")
            else:
                print("✅ 页面没有明显的错误信息")
            
            # 检查CSS样式
            if ".submit-container" in content:
                print("✅ 发现submit页面专用样式")
            else:
                print("❌ 缺少submit页面专用样式")
            
            # 检查表单元素
            form_elements = [
                "project",
                "manager", 
                "title",
                "description",
                "image"
            ]
            
            print("\n4. 检查表单元素...")
            for element in form_elements:
                if f'name="{element}"' in content:
                    print(f"   ✅ {element} 字段存在")
                else:
                    print(f"   ❌ {element} 字段缺失")
            
            return True
            
        else:
            print(f"❌ submit页面访问失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 诊断过程中出现错误: {e}")
        return False

def main():
    """主函数"""
    print("ReBugTracker - Submit页面诊断工具")
    print("检查submit页面是否正确加载和渲染")
    print()
    
    success = diagnose_submit_page()
    
    if success:
        print("\n🎯 诊断完成！")
        print("请检查保存的页面内容文件以获取更多详细信息")
    else:
        print("\n❌ 诊断失败")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
