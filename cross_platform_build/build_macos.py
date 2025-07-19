#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker macOS 打包脚本
支持在 macOS 系统上打包 ReBugTracker 为可执行文件
现在调用 macos 目录下的专用构建脚本
"""

import os
import sys
import subprocess
import platform
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

def check_system():
    """检查系统环境"""
    print_step(1, "检查系统环境")

    if platform.system() != 'Darwin':
        print_error("此脚本只能在 macOS 系统上运行")
        return False

    print_success(f"系统: {platform.system()} {platform.release()}")

    # 检查 Python 版本
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
        print_error("未安装 PyInstaller，请运行: pip install pyinstaller")
        return False

    return True

def run_macos_build():
    """运行 macOS 专用构建脚本"""
    print_step(2, "调用 macOS 专用构建脚本")

    script_dir = Path(__file__).parent
    macos_build_script = script_dir / 'macos' / 'build_macos_fixed.py'

    if not macos_build_script.exists():
        print_error(f"macOS 构建脚本不存在: {macos_build_script}")
        return False

    print(f"🔧 执行命令: python {macos_build_script}")
    print()

    try:
        # 运行 macOS 专用构建脚本
        result = subprocess.run([
            sys.executable, str(macos_build_script)
        ], check=True, capture_output=False, text=True)

        print_success("macOS 构建脚本执行完成")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"macOS 构建脚本执行失败: {e}")
        return False
    except Exception as e:
        print_error(f"执行 macOS 构建脚本时出错: {e}")
        return False




def show_usage():
    """显示使用说明"""
    print()
    print("=" * 60)
    print("🚀 使用说明")
    print("=" * 60)
    print()
    print("macOS 使用方法:")
    print("1. 进入 dist_mac 目录")
    print("2. 运行 ./start_rebugtracker.sh 启动")
    print("3. 或直接运行 ./ReBugTracker")
    print()
    print("高级功能:")
    print("- 后台运行: nohup ./ReBugTracker > app.log 2>&1 &")
    print("- 配置修改: 编辑 .env 文件")
    print("- 管理员修复: python macos/fix_admin_macos.py")
    print()
    print("=" * 60)
    print("🎉 macOS 构建完成!")
    print("=" * 60)
    print("感谢使用 ReBugTracker!")

def main():
    """主函数"""
    print("🍎 ReBugTracker macOS 打包工具")
    print("=" * 60)

    # 检查系统环境
    if not check_system():
        sys.exit(1)

    # 运行 macOS 专用构建脚本
    if not run_macos_build():
        sys.exit(1)

    # 显示使用说明
    show_usage()

if __name__ == '__main__':
    main()
