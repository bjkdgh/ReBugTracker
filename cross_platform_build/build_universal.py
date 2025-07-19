#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker 通用跨平台打包脚本
自动检测操作系统并调用相应的打包脚本
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {message}")
    print('='*60)

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")

def print_warning(message):
    """打印警告信息"""
    print(f"⚠️ {message}")

def detect_system():
    """检测操作系统"""
    print_step(1, "检测操作系统")
    
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    
    print(f"系统: {system}")
    print(f"版本: {release}")
    print(f"架构: {machine}")
    
    if system == 'Windows':
        print_success("检测到 Windows 系统")
        return 'windows'
    elif system == 'Darwin':
        print_success("检测到 macOS 系统")
        return 'macos'
    elif system == 'Linux':
        print_success("检测到 Linux 系统")
        return 'linux'
    else:
        print_error(f"不支持的操作系统: {system}")
        return None

def check_python_version():
    """检查Python版本"""
    print_step(2, "检查Python环境")
    
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print_error("需要 Python 3.8 或更高版本")
        return False
    
    print_success(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print_success(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print_error("未安装 PyInstaller")
        print("请运行以下命令安装:")
        print("  pip install pyinstaller")
        return False
    
    return True

def run_platform_build(system_type):
    """运行平台特定的打包脚本"""
    print_step(3, f"运行 {system_type.upper()} 打包脚本")
    
    script_dir = Path(__file__).parent
    
    if system_type == 'windows':
        # Windows 使用 windows 目录下的打包脚本
        script_path = script_dir / 'windows' / 'build_windows.py'
        if not script_path.exists():
            print_error(f"Windows 打包脚本不存在: {script_path}")
            print("尝试使用传统构建脚本...")
            script_path = script_dir / 'windows' / 'build_exe.py'
            if not script_path.exists():
                print_error(f"传统 Windows 打包脚本也不存在: {script_path}")
                return False
    elif system_type == 'macos':
        script_path = script_dir / 'build_macos.py'
    elif system_type == 'linux':
        script_path = script_dir / 'build_linux.py'
    else:
        print_error(f"不支持的系统类型: {system_type}")
        return False
    
    if not script_path.exists():
        print_error(f"打包脚本不存在: {script_path}")
        return False
    
    print(f"执行脚本: {script_path}")
    
    try:
        # 运行打包脚本
        result = subprocess.run([
            sys.executable, str(script_path)
        ], check=True)
        
        print_success("打包脚本执行完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"打包脚本执行失败，退出码: {e.returncode}")
        return False
    except Exception as e:
        print_error(f"执行打包脚本时发生错误: {e}")
        return False

def show_platform_info():
    """显示平台特定信息"""
    system_type = platform.system()
    
    print()
    print("=" * 60)
    print("📋 平台特定信息")
    print("=" * 60)
    
    if system_type == 'Windows':
        print("🪟 Windows 平台:")
        print("- 输出文件: ReBugTracker.exe")
        print("- 启动脚本: start_rebugtracker.bat")
        print("- 配置文件: .env")
        print("- 支持: Windows 服务、VBS 后台启动")
        
    elif system_type == 'Darwin':
        print("🍎 macOS 平台:")
        print("- 输出文件: ReBugTracker")
        print("- 启动脚本: start_rebugtracker.sh")
        print("- 配置文件: .env")
        print("- 支持: 应用程序包、启动项")
        
    elif system_type == 'Linux':
        print("🐧 Linux 平台:")
        print("- 输出文件: ReBugTracker")
        print("- 启动脚本: start_rebugtracker.sh")
        print("- 安装脚本: install.sh")
        print("- 配置文件: .env")
        print("- 支持: 系统服务、桌面快捷方式")

def show_usage_instructions(system_type):
    """显示使用说明"""
    print()
    print("=" * 60)
    print("🚀 使用说明")
    print("=" * 60)
    
    if system_type == 'windows':
        print("Windows 使用方法:")
        print("1. 进入 dist 目录")
        print("2. 双击 start_rebugtracker.bat")
        print("3. 或直接运行 ReBugTracker.exe")
        print()
        print("高级功能:")
        print("- Windows 服务: 运行 install_service.bat")
        print("- VBS 后台启动: 运行 start_rebugtracker.vbs")
        
    elif system_type == 'macos':
        print("macOS 使用方法:")
        print("1. 进入 dist/ReBugTracker 目录")
        print("2. 运行 ./start_rebugtracker.sh")
        print("3. 或直接运行 ./ReBugTracker")
        print()
        print("权限设置:")
        print("chmod +x ReBugTracker")
        print("chmod +x start_rebugtracker.sh")
        
    elif system_type == 'linux':
        print("Linux 使用方法:")
        print("1. 进入 dist/ReBugTracker 目录")
        print("2. 运行 ./start_rebugtracker.sh")
        print("3. 或运行 sudo ./install.sh 安装到系统")
        print()
        print("权限设置:")
        print("chmod +x ReBugTracker")
        print("chmod +x start_rebugtracker.sh")
        print("chmod +x install.sh")

def main():
    """主函数"""
    print("ReBugTracker 通用跨平台打包工具")
    print("=" * 60)
    print("🌍 自动检测操作系统并执行相应的打包脚本")
    
    # 检测操作系统
    system_type = detect_system()
    if not system_type:
        sys.exit(1)
    
    # 检查Python环境
    if not check_python_version():
        sys.exit(1)
    
    # 显示平台信息
    show_platform_info()
    
    # 确认继续
    print()
    try:
        response = input("是否继续打包? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("已取消打包")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n已取消打包")
        sys.exit(0)
    
    # 运行平台特定的打包脚本
    if not run_platform_build(system_type):
        sys.exit(1)
    
    # 显示使用说明
    show_usage_instructions(system_type)
    
    print()
    print("=" * 60)
    print("🎉 跨平台打包完成!")
    print("=" * 60)
    print("感谢使用 ReBugTracker!")

if __name__ == '__main__':
    main()
