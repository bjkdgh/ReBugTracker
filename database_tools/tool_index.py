#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker 数据库工具索引
提供交互式工具选择界面
"""

import sys
import os
import subprocess

def show_tool_menu():
    """显示工具菜单"""
    print("🚀 ReBugTracker 数据库工具集")
    print("=" * 50)
    print()
    
    tools = {
        "1": {
            "name": "综合数据库状态检查",
            "file": "comprehensive_db_check.py",
            "description": "全面检查数据库健康状态（推荐）"
        },
        "2": {
            "name": "用户表数据对比",
            "file": "compare_users_table.py",
            "description": "比较PostgreSQL和SQLite的用户数据"
        },
        "3": {
            "name": "通用通知系统表创建",
            "file": "create_notification_tables.py",
            "description": "为当前数据库创建通知系统表（支持PostgreSQL和SQLite）"
        },
        "4": {
            "name": "SQLite配置检查",
            "file": "sqlite_config_checker.py",
            "description": "检查SQLite配置和优化建议"
        },
        "5": {
            "name": "SQLite优化工具",
            "file": "sqlite_optimizer.py",
            "description": "优化SQLite数据库性能"
        }
    }
    
    print("📋 可用工具列表:")
    print()
    
    for key, tool in tools.items():
        print(f"  {key}. {tool['name']}")
        print(f"     {tool['description']}")
        print()
    
    print("0. 退出")
    print()
    
    return tools

def run_tool(tool_file):
    """运行指定的工具"""
    try:
        print(f"🔧 正在运行: {tool_file}")
        print("=" * 50)
        
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tool_path = os.path.join(root_dir, "database_tools", tool_file)
        
        if not os.path.exists(tool_path):
            print(f"❌ 工具文件不存在: {tool_path}")
            return False
        
        # 运行工具
        result = subprocess.run([sys.executable, tool_path], 
                              cwd=root_dir,
                              capture_output=False)
        
        print()
        print("=" * 50)
        if result.returncode == 0:
            print("✅ 工具执行完成")
        else:
            print(f"❌ 工具执行失败，退出码: {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 运行工具时出错: {e}")
        return False

def main():
    """主函数"""
    while True:
        try:
            tools = show_tool_menu()
            
            choice = input("请选择要运行的工具 (输入数字): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            
            if choice in tools:
                tool = tools[choice]
                print(f"\n🎯 您选择了: {tool['name']}")
                
                confirm = input("确认运行此工具吗？(y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    print()
                    success = run_tool(tool['file'])
                    
                    if success:
                        print("\n✨ 工具运行成功！")
                    else:
                        print("\n💥 工具运行失败！")
                    
                    input("\n按回车键继续...")
                else:
                    print("❌ 已取消")
            else:
                print("❌ 无效选择，请输入正确的数字")
            
            print("\n" + "=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
