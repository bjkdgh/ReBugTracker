#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker UV 管理脚本
用于初始化和管理 uv 项目环境
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True, capture_output=False):
    """运行命令并处理结果"""
    print(f"执行命令: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if capture_output and e.stdout:
            print(f"输出: {e.stdout}")
        if capture_output and e.stderr:
            print(f"错误: {e.stderr}")
        return False

def check_uv_installed():
    """检查 uv 是否已安装"""
    try:
        version = run_command("uv --version", capture_output=True)
        print(f"✅ uv 已安装: {version}")
        return True
    except:
        print("❌ uv 未安装")
        return False

def install_uv():
    """安装 uv"""
    print("正在安装 uv...")
    
    if sys.platform == "win32":
        # Windows 安装
        cmd = 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
    else:
        # Unix/Linux/macOS 安装
        cmd = 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    
    if run_command(cmd):
        print("✅ uv 安装成功")
        return True
    else:
        print("❌ uv 安装失败")
        return False

def init_uv_project():
    """初始化 uv 项目"""
    print("正在初始化 uv 项目...")
    
    # 检查是否已经是 uv 项目
    if Path("uv.lock").exists():
        print("✅ 项目已经是 uv 项目")
        return True
    
    # 初始化项目
    if run_command("uv init --no-readme"):
        print("✅ uv 项目初始化成功")
        return True
    else:
        print("❌ uv 项目初始化失败")
        return False

def sync_dependencies():
    """同步依赖"""
    print("正在同步依赖...")
    
    if run_command("uv sync"):
        print("✅ 依赖同步成功")
        return True
    else:
        print("❌ 依赖同步失败")
        return False

def add_dev_dependencies():
    """添加开发依赖"""
    print("正在添加开发依赖...")
    
    dev_deps = [
        "pytest>=7.0.0",
        "pytest-flask>=1.2.0", 
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
    ]
    
    for dep in dev_deps:
        if run_command(f"uv add --dev {dep}"):
            print(f"✅ 已添加开发依赖: {dep}")
        else:
            print(f"❌ 添加开发依赖失败: {dep}")

def migrate_from_requirements():
    """从 requirements.txt 迁移依赖"""
    print("正在从 requirements.txt 迁移依赖...")
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt 不存在")
        return False
    
    # 读取 requirements.txt
    with open("requirements.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 添加每个依赖
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            if run_command(f"uv add {line}"):
                print(f"✅ 已添加依赖: {line}")
            else:
                print(f"❌ 添加依赖失败: {line}")
    
    return True

def create_scripts():
    """创建常用脚本"""
    print("正在创建常用脚本...")
    
    scripts = {
        "run.py": '''#!/usr/bin/env python3
"""运行 ReBugTracker"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "rebugtracker.py"] + sys.argv[1:])
''',
        "test.py": '''#!/usr/bin/env python3
"""运行测试"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run(["uv", "run", "pytest"] + sys.argv[1:])
''',
        "format.py": '''#!/usr/bin/env python3
"""格式化代码"""
import subprocess

if __name__ == "__main__":
    print("正在格式化代码...")
    subprocess.run(["uv", "run", "black", "."])
    subprocess.run(["uv", "run", "flake8", "."])
'''
    }
    
    for script_name, content in scripts.items():
        with open(script_name, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 在 Unix 系统上设置执行权限
        if sys.platform != "win32":
            os.chmod(script_name, 0o755)
        
        print(f"✅ 已创建脚本: {script_name}")

def show_usage():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎉 ReBugTracker UV 环境设置完成!")
    print("="*60)
    print()
    print("常用命令:")
    print("  uv run python rebugtracker.py    # 运行应用")
    print("  uv run pytest                    # 运行测试")
    print("  uv run black .                   # 格式化代码")
    print("  uv run flake8 .                  # 代码检查")
    print("  uv add <package>                 # 添加依赖")
    print("  uv remove <package>              # 移除依赖")
    print("  uv sync                          # 同步依赖")
    print("  uv lock                          # 更新锁定文件")
    print()
    print("快捷脚本:")
    print("  python run.py                    # 运行应用")
    print("  python test.py                   # 运行测试")
    print("  python format.py                 # 格式化代码")
    print()
    print("环境信息:")
    print(f"  项目目录: {Path.cwd()}")
    print(f"  Python 版本: {sys.version}")
    print()

def main():
    """主函数"""
    print("🚀 ReBugTracker UV 环境设置")
    print("="*60)
    
    # 检查并安装 uv
    if not check_uv_installed():
        if not install_uv():
            print("❌ 无法安装 uv，请手动安装")
            sys.exit(1)
    
    # 初始化项目
    if not init_uv_project():
        print("❌ 项目初始化失败")
        sys.exit(1)
    
    # 迁移依赖
    if not migrate_from_requirements():
        print("❌ 依赖迁移失败")
        sys.exit(1)
    
    # 添加开发依赖
    add_dev_dependencies()
    
    # 同步依赖
    if not sync_dependencies():
        print("❌ 依赖同步失败")
        sys.exit(1)
    
    # 创建脚本
    create_scripts()
    
    # 显示使用说明
    show_usage()

if __name__ == "__main__":
    main()
