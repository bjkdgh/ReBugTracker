#!/usr/bin/env python3
"""
ReBugTracker 部署脚本选择器
帮助用户选择合适的部署脚本
"""

import os
import sys
import platform
import subprocess

def print_banner():
    """打印欢迎横幅"""
    print("🚀 ReBugTracker 部署脚本选择器")
    print("=" * 50)
    print()

def print_info(msg):
    print(f"ℹ️  {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def detect_system():
    """检测操作系统"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system in ["linux", "darwin"]:
        return "unix"
    else:
        return "unknown"

def check_script_exists(script_path):
    """检查脚本是否存在"""
    return os.path.exists(script_path)

def show_script_comparison():
    """显示脚本功能对比"""
    print("📋 可用的部署脚本:")
    print()
    
    scripts = {
        "deploy.sh": {
            "name": "Linux/macOS 一键部署脚本",
            "features": [
                "✅ Docker + 本地部署选择",
                "✅ PostgreSQL + SQLite 数据库选择",
                "✅ 全程交互式引导",
                "✅ 自动依赖安装",
                "✅ 虚拟环境隔离",
                "✅ 详细错误处理"
            ],
            "suitable": "推荐所有Linux/macOS用户使用"
        },
        "deploy.bat": {
            "name": "Windows 一键部署脚本",
            "features": [
                "✅ Docker + 本地部署选择",
                "✅ PostgreSQL + SQLite 数据库选择",
                "✅ 全程交互式引导",
                "✅ 自动环境检查",
                "✅ 虚拟环境隔离",
                "✅ 详细错误处理"
            ],
            "suitable": "推荐所有Windows用户使用"
        }
    }
    
    for script, info in scripts.items():
        if check_script_exists(script):
            print(f"🔧 {info['name']}")
            print(f"   文件: {script}")
            for feature in info['features']:
                print(f"   {feature}")
            print(f"   💡 {info['suitable']}")
            print()
        else:
            print(f"❌ {info['name']} (文件不存在: {script})")
            print()

def recommend_script():
    """推荐合适的脚本"""
    system = detect_system()
    
    print("🎯 推荐的部署脚本:")
    print()
    
    if system == "windows":
        if check_script_exists("deploy.bat"):
            print("👉 推荐使用: deploy.bat")
            print("   这是专为Windows设计的一键部署脚本")
            print("   支持Docker和本地部署，支持多种数据库")
            return "deploy.bat"
        else:
            print_error("Windows部署脚本不存在")
            return None

    elif system == "unix":
        if check_script_exists("deploy.sh"):
            print("👉 推荐使用: deploy.sh")
            print("   这是Linux/macOS的一键部署脚本")
            print("   支持Docker和本地部署，支持多种数据库")
            return "deploy.sh"
        else:
            print_error("没有找到适合的Linux/macOS部署脚本")
            return None
    else:
        print_error(f"不支持的操作系统: {platform.system()}")
        return None

def run_script(script_path):
    """运行选择的脚本"""
    system = detect_system()
    
    try:
        if system == "windows":
            # Windows批处理文件
            subprocess.run([script_path], shell=True, check=True)
        else:
            # Unix shell脚本
            # 确保脚本有执行权限
            os.chmod(script_path, 0o755)
            subprocess.run([f"./{script_path}"], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"脚本执行失败: {e}")
        return False
    except Exception as e:
        print_error(f"执行出错: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print_banner()
    
    # 检查是否在项目根目录
    if not os.path.exists("rebugtracker.py"):
        print_error("请在ReBugTracker项目根目录运行此脚本")
        sys.exit(1)
    
    # 显示脚本对比
    show_script_comparison()
    
    # 推荐脚本
    recommended_script = recommend_script()
    
    if not recommended_script:
        print()
        print_error("没有找到合适的部署脚本")
        print("请确保部署脚本文件存在于项目目录中")
        sys.exit(1)
    
    print()
    print("🤔 您想要:")
    print("1. 运行推荐的部署脚本")
    print("2. 手动选择部署脚本")
    print("3. 查看部署指南")
    print("4. 退出")
    print()
    
    while True:
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == "1":
            print()
            print_info(f"正在运行推荐脚本: {recommended_script}")
            print()
            if run_script(recommended_script):
                print_success("部署脚本执行完成")
            break
            
        elif choice == "2":
            print()
            print("可用的脚本:")
            available_scripts = []
            for i, script in enumerate(["deploy.sh", "deploy.bat"], 1):
                if check_script_exists(script):
                    print(f"{i}. {script}")
                    available_scripts.append(script)
            
            if not available_scripts:
                print_error("没有找到可用的部署脚本")
                break
            
            try:
                script_choice = int(input("请选择脚本编号: ")) - 1
                if 0 <= script_choice < len(available_scripts):
                    selected_script = available_scripts[script_choice]
                    print()
                    print_info(f"正在运行: {selected_script}")
                    print()
                    if run_script(selected_script):
                        print_success("部署脚本执行完成")
                    break
                else:
                    print_warning("无效的选择")
            except ValueError:
                print_warning("请输入有效的数字")
                
        elif choice == "3":
            print()
            print("📚 部署指南文档:")
            guides = [
                "README_DEPLOYMENT.md - 部署脚本使用指南",
                "DEPLOYMENT_GUIDE_ENHANCED.md - 详细部署指南"
            ]
            
            for guide in guides:
                if os.path.exists(guide.split(" - ")[0]):
                    print(f"✅ {guide}")
                else:
                    print(f"❌ {guide} (文件不存在)")
            
            print()
            print("💡 建议先阅读 README_DEPLOYMENT.md 了解基本使用方法")
            print()
            
        elif choice == "4":
            print()
            print_info("感谢使用ReBugTracker！")
            break
            
        else:
            print_warning("无效选择，请输入 1-4")

if __name__ == "__main__":
    main()
