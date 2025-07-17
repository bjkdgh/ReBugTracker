#!/usr/bin/env python3
"""
ReBugTracker 统一数据库工具集 - 交互式工具选择器
整合了所有数据库管理、迁移、检查和优化工具
"""

import os
import sys
import subprocess
from datetime import datetime

def print_header():
    """打印工具集标题"""
    print("🚀 ReBugTracker 统一数据库工具集")
    print("=" * 60)
    print(f"🕒 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def print_menu():
    """打印主菜单"""
    print("\n📋 工具分类菜单:")
    print("1. 🔄 数据库同步工具")
    print("2. 🔍 数据库检查工具") 
    print("3. 🛠️ 数据库维护工具")
    print("4. 📊 快速状态检查")
    print("5. 📖 查看工具说明")
    print("0. 退出")

def show_sync_tools():
    """显示同步工具菜单"""
    print("\n🔄 数据库同步工具:")
    print("=" * 40)
    print("1. smart_sync_postgres_to_sqlite.py - 智能同步(推荐) ⭐")
    print("   - 自动检查表结构")
    print("   - 一键完成表结构+数据同步")
    print("   - 自动备份和验证")
    print("   💡 建议：解决登录问题、日常同步")
    print()
    print("2. sync_sqlite_to_postgres_data.py - 反向同步")
    print("   - 从SQLite同步到PostgreSQL")
    print("   💡 建议：开发环境数据同步到服务器")
    print()
    print("0. 返回主菜单")

    choice = input("\n请选择工具 (0-2): ").strip()

    tools = {
        "1": "sync_tools/smart_sync_postgres_to_sqlite.py",
        "2": "sync_tools/sync_sqlite_to_postgres_data.py"
    }
    
    if choice in tools:
        run_tool(tools[choice])
    elif choice == "0":
        return
    else:
        print("❌ 无效选择")

def show_check_tools():
    """显示检查工具菜单"""
    print("\n🔍 数据库检查工具:")
    print("=" * 40)
    print("1. sync_status_checker.py - 全面状态检查(推荐) ⭐")
    print("   - 连接测试 + 表结构对比 + 数据统计")
    print("   💡 建议：日常检查、同步前诊断")
    print()
    print("2. table_structure_checker.py - 表结构对比")
    print("   - 详细的字段级对比分析")
    print("   💡 建议：表结构问题深度诊断")
    print()
    print("3. postgres_structure_inspector.py - PostgreSQL详细检查 🆕")
    print("   - PostgreSQL表结构、外键、索引详细分析")
    print("   💡 建议：PostgreSQL结构深度分析")
    print()
    print("4. sqlite_structure_inspector.py - SQLite详细检查 🆕")
    print("   - SQLite表结构、外键、索引详细分析")
    print("   💡 建议：SQLite结构深度分析")
    print()
    print("5. database_structure_validator.py - 结构验证工具 🆕")
    print("   - 验证数据库结构是否符合规范")
    print("   💡 建议：结构规范性检查")
    print()
    print("6. test_db_connection_new.py - 连接测试")
    print("   - 验证数据库连接")
    print("   💡 建议：连接问题排查")
    print()
    print("0. 返回主菜单")

    choice = input("\n请选择工具 (0-6): ").strip()

    tools = {
        "1": "check_tools/sync_status_checker.py",
        "2": "check_tools/table_structure_checker.py",
        "3": "check_tools/postgres_structure_inspector.py",
        "4": "check_tools/sqlite_structure_inspector.py",
        "5": "check_tools/database_structure_validator.py",
        "6": "check_tools/test_db_connection_new.py"
    }
    
    if choice in tools:
        run_tool(tools[choice])
    elif choice == "0":
        return
    else:
        print("❌ 无效选择")

def show_maintenance_tools():
    """显示维护工具菜单"""
    print("\n🛠️ 数据库维护工具:")
    print("=" * 40)
    print("1. fix_orphan_records.py - 修复孤儿记录")
    print("   - 清理无效的外键引用")
    print("   💡 建议：数据不一致时使用")
    print()
    print("2. sqlite_optimizer.py - SQLite优化")
    print("   - 优化SQLite数据库性能")
    print("   💡 建议：定期维护，提升性能")
    print()
    print("0. 返回主菜单")

    choice = input("\n请选择工具 (0-2): ").strip()

    tools = {
        "1": "maintenance_tools/fix_orphan_records.py",
        "2": "maintenance_tools/sqlite_optimizer.py"
    }
    
    if choice in tools:
        run_tool(tools[choice])
    elif choice == "0":
        return
    else:
        print("❌ 无效选择")

def quick_status_check():
    """快速状态检查"""
    print("\n📊 执行快速状态检查...")
    print("=" * 40)
    
    # 运行同步状态检查
    print("🔍 检查数据库同步状态...")
    run_tool("check_tools/sync_status_checker.py", wait_for_input=False)
    
    print("\n" + "=" * 40)
    input("按回车键返回主菜单...")

def show_documentation():
    """显示工具说明"""
    print("\n📖 工具说明文档:")
    print("=" * 40)
    
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        print("📄 README.md 文档位置:", readme_path)
        print("\n💡 推荐工作流程:")
        print("1. 日常检查: sync_status_checker.py → comprehensive_db_check.py")
        print("2. 数据迁移: sync_status_checker.py → full_sync_postgres_to_sqlite.py → verify_migration.py")
        print("3. 问题排查: comprehensive_db_check.py → check_db_constraints.py → compare_databases.py")
        
        print("\n⭐ 推荐工具:")
        print("- sync_status_checker.py (必备)")
        print("- comprehensive_db_check.py (必备)")
        print("- full_sync_postgres_to_sqlite.py (推荐)")
        print("- test_db_connection_new.py (推荐)")
    else:
        print("❌ 未找到README.md文档")
    
    print("\n" + "=" * 40)
    input("按回车键返回主菜单...")

def run_tool(tool_path, wait_for_input=True):
    """运行指定工具"""
    print(f"\n🚀 启动工具: {tool_path}")
    print("=" * 50)
    
    # 检查虚拟环境
    venv_python = os.path.join(".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        cmd = [venv_python, tool_path]
        print("✅ 使用虚拟环境运行")
    else:
        cmd = ["python", tool_path]
        print("⚠️ 使用系统Python运行")
    
    try:
        # 切换到项目根目录
        original_dir = os.getcwd()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)

        # 构建完整工具路径
        full_tool_path = os.path.join("database_tools", tool_path)
        cmd = [venv_python if os.path.exists(venv_python) else "python", full_tool_path]

        # 运行工具
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        # 恢复原目录
        os.chdir(original_dir)
        
        print(f"\n✅ 工具执行完成 (返回码: {result.returncode})")
        
    except Exception as e:
        print(f"❌ 工具执行失败: {e}")
    
    if wait_for_input:
        print("\n" + "=" * 50)
        input("按回车键返回菜单...")

def main():
    """主函数"""
    while True:
        print_header()
        print_menu()
        
        choice = input("\n请选择操作 (0-5): ").strip()
        
        if choice == "1":
            show_sync_tools()
        elif choice == "2":
            show_check_tools()
        elif choice == "3":
            show_maintenance_tools()
        elif choice == "4":
            quick_status_check()
        elif choice == "5":
            show_documentation()
        elif choice == "0":
            print("\n👋 感谢使用 ReBugTracker 数据库工具集！")
            break
        else:
            print("❌ 无效选择，请重新输入")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
