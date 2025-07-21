#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker 离线包创建脚本
用于创建可在离线环境部署的完整安装包
"""

import os
import sys
import subprocess
import shutil
import platform
import urllib.request
from pathlib import Path
import tarfile
import zipfile

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
        return False

def create_offline_directory():
    """创建离线包目录"""
    offline_dir = Path("rebugtracker-offline")
    if offline_dir.exists():
        print(f"删除现有目录: {offline_dir}")
        shutil.rmtree(offline_dir)
    
    offline_dir.mkdir()
    print(f"✅ 创建离线包目录: {offline_dir}")
    return offline_dir

def copy_project_files(offline_dir):
    """复制项目文件"""
    print("正在复制项目文件...")
    
    # 要复制的文件和目录
    items_to_copy = [
        "rebugtracker.py",
        "config.py", 
        "db_factory.py",
        "sql_adapter.py",
        "config_adapter.py",
        "notification/",
        "templates/",
        "static/",
        "pyproject.toml",
        "requirements.txt",
        "UV_GUIDE.md",
        "README.md",
        ".env.template"
    ]
    
    # 可选文件（存在则复制）
    optional_items = [
        "rebugtracker.db",
        "uploads/",
        "logs/",
        "data_exports/",
        ".env"
    ]
    
    for item in items_to_copy:
        src = Path(item)
        if src.exists():
            dst = offline_dir / item
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print(f"✅ 已复制: {item}")
        else:
            print(f"❌ 文件不存在: {item}")
    
    for item in optional_items:
        src = Path(item)
        if src.exists():
            dst = offline_dir / item
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print(f"✅ 已复制（可选）: {item}")

def export_requirements(offline_dir):
    """导出依赖列表"""
    print("正在导出依赖列表...")
    
    # 尝试使用 uv 导出
    try:
        result = run_command("uv export --no-dev", capture_output=True)
        if result:
            with open(offline_dir / "requirements.txt", "w") as f:
                f.write(result)
            print("✅ 使用 uv 导出依赖成功")
            return True
    except:
        pass
    
    # 回退到复制现有的 requirements.txt
    if Path("requirements.txt").exists():
        shutil.copy2("requirements.txt", offline_dir / "requirements.txt")
        print("✅ 复制现有 requirements.txt")
        return True
    
    print("❌ 无法导出依赖列表")
    return False

def download_packages(offline_dir):
    """下载Python包"""
    print("正在下载Python包...")
    
    wheels_dir = offline_dir / "wheels"
    wheels_dir.mkdir()
    
    requirements_file = offline_dir / "requirements.txt"
    
    # 尝试使用 uv 下载
    try:
        cmd = f"uv pip download -r {requirements_file} -d {wheels_dir}"
        if run_command(cmd):
            print("✅ 使用 uv 下载包成功")
            return True
    except:
        pass
    
    # 回退到使用 pip 下载
    try:
        cmd = f"pip download -r {requirements_file} -d {wheels_dir}"
        if run_command(cmd):
            print("✅ 使用 pip 下载包成功")
            return True
    except:
        pass
    
    print("❌ 下载包失败")
    return False

def download_uv_binary(offline_dir):
    """下载 uv 二进制文件"""
    print("正在下载 uv 二进制文件...")
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 确定下载URL
    if system == "windows":
        if "64" in machine or "amd64" in machine:
            url = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
            filename = "uv-windows.zip"
        else:
            url = "https://github.com/astral-sh/uv/releases/latest/download/uv-i686-pc-windows-msvc.zip"
            filename = "uv-windows-32.zip"
    elif system == "darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            url = "https://github.com/astral-sh/uv/releases/latest/download/uv-aarch64-apple-darwin.tar.gz"
            filename = "uv-macos-arm.tar.gz"
        else:
            url = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-apple-darwin.tar.gz"
            filename = "uv-macos.tar.gz"
    else:  # Linux
        if "arm" in machine or "aarch64" in machine:
            url = "https://github.com/astral-sh/uv/releases/latest/download/uv-aarch64-unknown-linux-gnu.tar.gz"
            filename = "uv-linux-arm.tar.gz"
        else:
            url = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz"
            filename = "uv-linux.tar.gz"
    
    try:
        print(f"下载 {url}")
        urllib.request.urlretrieve(url, offline_dir / filename)
        print(f"✅ 下载 uv 二进制文件成功: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 下载 uv 二进制文件失败: {e}")
        return None

def create_install_scripts(offline_dir, uv_filename):
    """创建安装脚本"""
    print("正在创建安装脚本...")
    
    # Linux/macOS 安装脚本
    linux_script = '''#!/bin/bash
# ReBugTracker 离线安装脚本 (Linux/macOS)

set -e

echo "🚀 开始安装 ReBugTracker 离线环境..."

# 检测系统类型
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    UV_FILE="uv-linux.tar.gz"
    if [[ $(uname -m) == "aarch64" ]] || [[ $(uname -m) == "arm64" ]]; then
        UV_FILE="uv-linux-arm.tar.gz"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    UV_FILE="uv-macos.tar.gz"
    if [[ $(uname -m) == "arm64" ]]; then
        UV_FILE="uv-macos-arm.tar.gz"
    fi
else
    echo "❌ 不支持的系统类型: $OSTYPE"
    exit 1
fi

# 解压并安装 uv
if [ -f "$UV_FILE" ]; then
    echo "📦 解压 uv..."
    tar -xzf "$UV_FILE"
    
    # 尝试安装到系统路径
    if sudo cp uv /usr/local/bin/ 2>/dev/null; then
        echo "✅ uv 已安装到 /usr/local/bin/"
    else
        echo "⚠️ 无法安装到系统路径，将使用本地 uv"
        export PATH="$PWD:$PATH"
    fi
else
    echo "❌ 未找到 uv 二进制文件: $UV_FILE"
    exit 1
fi

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
./uv venv || uv venv

# 安装依赖
echo "📦 安装依赖包..."
./uv pip install --no-index --find-links wheels/ -r requirements.txt || uv pip install --no-index --find-links wheels/ -r requirements.txt

echo "✅ 离线安装完成！"
echo ""
echo "🚀 启动应用:"
echo "   ./uv run python rebugtracker.py"
echo "   或者: uv run python rebugtracker.py"
echo ""
echo "🌐 访问地址: http://localhost:5000"
echo "👤 默认账号: admin / admin"
'''
    
    # Windows 安装脚本
    windows_script = '''@echo off
REM ReBugTracker 离线安装脚本 (Windows)

echo 🚀 开始安装 ReBugTracker 离线环境...

REM 解压 uv
if exist "uv-windows.zip" (
    echo 📦 解压 uv...
    powershell -Command "Expand-Archive -Path 'uv-windows.zip' -DestinationPath '.' -Force"
    echo ✅ uv 解压完成
) else if exist "uv-windows-32.zip" (
    echo 📦 解压 uv (32位)...
    powershell -Command "Expand-Archive -Path 'uv-windows-32.zip' -DestinationPath '.' -Force"
    echo ✅ uv 解压完成
) else (
    echo ❌ 未找到 uv 二进制文件
    pause
    exit /b 1
)

REM 创建虚拟环境
echo 🔧 创建虚拟环境...
uv.exe venv
if errorlevel 1 (
    echo ❌ 创建虚拟环境失败
    pause
    exit /b 1
)

REM 安装依赖
echo 📦 安装依赖包...
uv.exe pip install --no-index --find-links wheels/ -r requirements.txt
if errorlevel 1 (
    echo ❌ 安装依赖失败
    pause
    exit /b 1
)

echo ✅ 离线安装完成！
echo.
echo 🚀 启动应用:
echo    uv.exe run python rebugtracker.py
echo.
echo 🌐 访问地址: http://localhost:5000
echo 👤 默认账号: admin / admin
echo.
pause
'''
    
    # 写入脚本文件
    with open(offline_dir / "install_offline.sh", "w", encoding="utf-8") as f:
        f.write(linux_script)
    os.chmod(offline_dir / "install_offline.sh", 0o755)
    
    with open(offline_dir / "install_offline.bat", "w", encoding="utf-8") as f:
        f.write(windows_script)
    
    print("✅ 创建安装脚本成功")

def create_readme(offline_dir):
    """创建离线包说明文档"""
    readme_content = '''# ReBugTracker 离线安装包

这是 ReBugTracker 的离线安装包，可以在没有网络连接的环境中部署。

## 📦 包含内容

- ReBugTracker 应用程序源码
- 所有 Python 依赖包 (wheels/ 目录)
- uv 包管理器二进制文件
- 自动安装脚本

## 🚀 安装步骤

### Linux/macOS
```bash
# 1. 解压安装包
tar -xzf rebugtracker-offline.tar.gz
cd rebugtracker-offline

# 2. 运行安装脚本
./install_offline.sh

# 3. 启动应用
uv run python rebugtracker.py
```

### Windows
```cmd
# 1. 解压安装包
# 使用 WinRAR 或 7-Zip 解压 rebugtracker-offline.zip

# 2. 进入目录
cd rebugtracker-offline

# 3. 运行安装脚本
install_offline.bat

# 4. 启动应用
uv.exe run python rebugtracker.py
```

## 🌐 访问应用

- 访问地址: http://localhost:5000
- 默认管理员账号: admin
- 默认管理员密码: admin

## 📋 系统要求

- Python 3.8 或更高版本
- Windows 10+, macOS 10.14+, 或 Linux (glibc 2.17+)
- 至少 100MB 可用磁盘空间

## 🔧 故障排除

1. **Python 未安装**: 请先安装 Python 3.8+
2. **权限问题**: 在 Linux/macOS 上可能需要 sudo 权限
3. **端口占用**: 如果 5000 端口被占用，请修改 .env 文件中的 SERVER_PORT

## 📚 更多信息

详细使用说明请参考 UV_GUIDE.md 文件。
'''
    
    with open(offline_dir / "README_OFFLINE.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 创建离线包说明文档")

def create_archive(offline_dir):
    """创建压缩包"""
    print("正在创建压缩包...")
    
    # 创建 tar.gz 包 (适用于 Linux/macOS)
    with tarfile.open("rebugtracker-offline.tar.gz", "w:gz") as tar:
        tar.add(offline_dir, arcname="rebugtracker-offline")
    print("✅ 创建 rebugtracker-offline.tar.gz")
    
    # 创建 zip 包 (适用于 Windows)
    with zipfile.ZipFile("rebugtracker-offline.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(offline_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = Path("rebugtracker-offline") / file_path.relative_to(offline_dir)
                zipf.write(file_path, arcname)
    print("✅ 创建 rebugtracker-offline.zip")

def main():
    """主函数"""
    print("🚀 ReBugTracker 离线包创建工具")
    print("=" * 60)
    
    # 检查当前目录
    if not Path("rebugtracker.py").exists():
        print("❌ 请在 ReBugTracker 项目根目录中运行此脚本")
        sys.exit(1)
    
    try:
        # 1. 创建离线目录
        offline_dir = create_offline_directory()
        
        # 2. 复制项目文件
        copy_project_files(offline_dir)
        
        # 3. 导出依赖列表
        if not export_requirements(offline_dir):
            print("❌ 导出依赖失败")
            sys.exit(1)
        
        # 4. 下载Python包
        if not download_packages(offline_dir):
            print("❌ 下载包失败")
            sys.exit(1)
        
        # 5. 下载 uv 二进制文件
        uv_filename = download_uv_binary(offline_dir)
        if not uv_filename:
            print("❌ 下载 uv 失败")
            sys.exit(1)
        
        # 6. 创建安装脚本
        create_install_scripts(offline_dir, uv_filename)
        
        # 7. 创建说明文档
        create_readme(offline_dir)
        
        # 8. 创建压缩包
        create_archive(offline_dir)
        
        print("\n" + "=" * 60)
        print("🎉 离线包创建完成!")
        print("=" * 60)
        print(f"📦 离线包文件:")
        print(f"   - rebugtracker-offline.tar.gz (Linux/macOS)")
        print(f"   - rebugtracker-offline.zip (Windows)")
        print(f"📁 离线包目录: {offline_dir}")
        print("\n📋 部署说明:")
        print("1. 将压缩包传输到离线环境")
        print("2. 解压并运行对应的安装脚本")
        print("3. 使用 uv run python rebugtracker.py 启动应用")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 创建离线包失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
