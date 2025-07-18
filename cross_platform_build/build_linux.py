#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker Linux 打包脚本
支持在 Linux 系统上打包 ReBugTracker 为可执行文件
"""

import os
import sys
import shutil
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
    
    if platform.system() != 'Linux':
        print_error("此脚本只能在 Linux 系统上运行")
        return False
    
    print_success(f"系统: {platform.system()} {platform.release()}")
    print_success(f"架构: {platform.machine()}")
    
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

def check_project_files():
    """检查项目文件"""
    print_step(2, "检查项目文件")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    required_files = [
        'rebugtracker.py',
        'requirements.txt',
        'templates',
        'static',
        'config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print_error(f"缺少必要文件: {', '.join(missing_files)}")
        return False
    
    print_success("所有必要文件都存在")
    return True

def clean_build_dirs():
    """清理构建目录"""
    print_step(3, "清理构建目录")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print_success(f"已清理: {dir_name}")
            except Exception as e:
                print_warning(f"清理 {dir_name} 失败: {e}")
        else:
            print(f"📁 {dir_name} 不存在，跳过")

def create_spec_file():
    """创建 PyInstaller 配置文件"""
    print_step(4, "创建 PyInstaller 配置文件")
    
    project_root = os.getcwd()
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 项目根目录
project_root = r'{project_root}'

# 数据文件和目录
datas = [
    # 模板文件
    (os.path.join(project_root, 'templates'), 'templates'),
    # 静态文件
    (os.path.join(project_root, 'static'), 'static'),
    # 配置文件
    (os.path.join(project_root, 'config.py'), '.'),
    (os.path.join(project_root, 'cross_platform_build/configs/app_config_unix.py'), '.'),
    (os.path.join(project_root, 'config_adapter.py'), '.'),
    # 环境变量模板
    (os.path.join(project_root, '.env.template'), '.'),
    # 数据库工厂和适配器
    (os.path.join(project_root, 'db_factory.py'), '.'),
    (os.path.join(project_root, 'sql_adapter.py'), '.'),
    # 通知系统
    (os.path.join(project_root, 'notification'), 'notification'),
]

# 检查并添加数据库文件
db_file = os.path.join(project_root, 'rebugtracker.db')
if os.path.exists(db_file):
    datas.append((db_file, '.'))

# 隐藏导入
hiddenimports = [
    'psycopg2',
    'sqlite3',
    'flask',
    'werkzeug',
    'jinja2',
    'click',
    'itsdangerous',
    'markupsafe',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna'
]

block_cipher = None

a = Analysis(
    [os.path.join(project_root, 'rebugtracker.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ReBugTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ReBugTracker',
)
'''
    
    spec_file = 'cross_platform_build/configs/rebugtracker_linux.spec'
    os.makedirs(os.path.dirname(spec_file), exist_ok=True)
    
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print_success(f"已创建配置文件: {spec_file}")
    return spec_file

def build_executable(spec_file):
    """构建可执行文件"""
    print_step(5, "构建可执行文件")
    
    print("正在构建，这可能需要几分钟...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            spec_file
        ], check=True, capture_output=True, text=True)
        
        print_success("可执行文件构建完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error("构建失败")
        print(f"错误输出: {e.stderr}")
        return False

def copy_additional_files():
    """复制额外文件到dist目录"""
    print_step(6, "复制额外文件")
    
    dist_dir = 'dist/ReBugTracker'
    if not os.path.exists(dist_dir):
        print_error("dist目录不存在")
        return False
    
    # 要复制的文件和目录
    items_to_copy = [
        ('rebugtracker.db', '数据库文件'),
        ('uploads', '上传文件目录'),
        ('logs', '日志目录'),
        ('data_exports', '数据导出目录'),
        ('README.md', '说明文档'),
        ('.env.template', '环境变量模板'),
    ]
    
    for item, description in items_to_copy:
        if os.path.exists(item):
            dest = os.path.join(dist_dir, item)
            try:
                if os.path.isdir(item):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
                print_success(f"已复制 {description}: {item}")
            except Exception as e:
                print_warning(f"复制 {item} 失败: {e}")
        else:
            print(f"📁 {item} 不存在，跳过")
    
    return True

def create_startup_script():
    """创建启动脚本"""
    print_step(7, "创建启动脚本")
    
    startup_script = '''#!/bin/bash
# ReBugTracker Linux 启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 切换到应用目录
cd "$SCRIPT_DIR"

# 启动应用
echo "正在启动 ReBugTracker..."
./ReBugTracker &

# 等待应用启动
sleep 3

# 尝试打开浏览器
echo "正在打开浏览器..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v gnome-open > /dev/null; then
    gnome-open http://localhost:5000
elif command -v firefox > /dev/null; then
    firefox http://localhost:5000 &
elif command -v chromium-browser > /dev/null; then
    chromium-browser http://localhost:5000 &
else
    echo "无法自动打开浏览器，请手动访问: http://localhost:5000"
fi

echo "ReBugTracker 已启动"
echo "访问地址: http://localhost:5000"
echo "默认管理员: admin / admin"
'''
    
    script_path = 'dist/ReBugTracker/start_rebugtracker.sh'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    # 设置执行权限
    os.chmod(script_path, 0o755)
    
    print_success(f"已创建启动脚本: {script_path}")

    # 创建安装脚本
    create_install_script()

    # 创建配置说明文档
    create_config_docs()

    return True

def create_install_script():
    """创建安装脚本"""
    install_script = '''#!/bin/bash
# ReBugTracker Linux 安装脚本

echo "ReBugTracker Linux 安装程序"
echo "=========================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="/opt/rebugtracker"

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

echo "正在安装 ReBugTracker 到 $INSTALL_DIR..."

# 创建安装目录
mkdir -p "$INSTALL_DIR"

# 复制文件
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

# 设置权限
chmod +x "$INSTALL_DIR/ReBugTracker"
chmod +x "$INSTALL_DIR/start_rebugtracker.sh"

# 创建桌面快捷方式
DESKTOP_FILE="/usr/share/applications/rebugtracker.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=ReBugTracker
Comment=Bug Tracking System
Exec=$INSTALL_DIR/start_rebugtracker.sh
Icon=$INSTALL_DIR/static/RBT.ico
Terminal=false
Type=Application
Categories=Development;
EOF

# 创建命令行快捷方式
SYMLINK="/usr/local/bin/rebugtracker"
ln -sf "$INSTALL_DIR/start_rebugtracker.sh" "$SYMLINK"

echo "安装完成！"
echo "启动方法："
echo "1. 从应用菜单启动 ReBugTracker"
echo "2. 命令行运行: rebugtracker"
echo "3. 直接运行: $INSTALL_DIR/start_rebugtracker.sh"
'''

    script_path = 'dist/ReBugTracker/install.sh'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(install_script)

    # 设置执行权限
    os.chmod(script_path, 0o755)

    print_success(f"已创建安装脚本: {script_path}")

def create_config_docs():
    """创建配置说明文档"""
    config_doc = '''# ReBugTracker Linux 配置说明

## 📋 文件说明

- `ReBugTracker` - 主程序可执行文件
- `start_rebugtracker.sh` - 启动脚本
- `install.sh` - 系统安装脚本
- `.env` - 环境配置文件（首次运行自动生成）
- `.env.template` - 配置模板文件
- `rebugtracker.db` - SQLite数据库文件
- `uploads/` - 文件上传目录
- `logs/` - 日志文件目录
- `data_exports/` - 数据导出目录

## 🚀 启动方法

### 方法1: 使用启动脚本（推荐）
```bash
./start_rebugtracker.sh
```

### 方法2: 直接运行
```bash
./ReBugTracker
```

### 方法3: 系统安装后
```bash
# 安装到系统
sudo ./install.sh

# 启动
rebugtracker
```

## ⚙️ 配置修改

1. **编辑配置文件**: 用文本编辑器打开 `.env` 文件
2. **常用配置项**:
   - `SERVER_PORT=8080` - 修改端口
   - `DB_TYPE=postgres` - 切换到PostgreSQL
   - `UPLOAD_FOLDER=/path/to/uploads` - 修改上传目录

## 🔧 故障排除

1. **权限问题**: 确保文件有执行权限
   ```bash
   chmod +x ReBugTracker
   chmod +x start_rebugtracker.sh
   ```

2. **端口占用**: 修改 `.env` 文件中的 `SERVER_PORT`

3. **数据库问题**: 删除 `rebugtracker.db` 重新初始化

4. **浏览器问题**: 手动访问 http://localhost:5000

## 📦 系统要求

- Linux 发行版（Ubuntu、CentOS、Debian等）
- glibc 2.17 或更高版本
- 可选：PostgreSQL（如需使用PostgreSQL数据库）

## 📞 技术支持

如遇问题，请查看 `logs/` 目录中的日志文件。
'''

    doc_path = 'dist/ReBugTracker/配置说明.md'
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(config_doc)

    print_success(f"已创建配置说明: {doc_path}")

def show_results():
    """显示打包结果"""
    print()
    print("=" * 60)
    print("🎉 Linux 打包完成!")
    print("=" * 60)

    dist_dir = 'dist/ReBugTracker'
    if os.path.exists(dist_dir):
        print(f"📂 输出目录: {os.path.abspath(dist_dir)}")

        # 列出主要文件
        exe_file = os.path.join(dist_dir, 'ReBugTracker')
        if os.path.exists(exe_file):
            size = os.path.getsize(exe_file) / (1024 * 1024)  # MB
            print(f"📦 可执行文件: ReBugTracker ({size:.1f} MB)")

        print()
        print("🚀 使用方法:")
        print("1. 进入 dist/ReBugTracker 目录")
        print("2. 运行 ./start_rebugtracker.sh 启动")
        print("3. 或运行 sudo ./install.sh 安装到系统")
        print()
        print("💡 提示: 首次运行会自动初始化数据库")
    else:
        print_error("dist目录不存在，打包可能失败")

def main():
    """主函数"""
    print("ReBugTracker Linux 打包工具")
    print("=" * 60)

    # 检查系统环境
    if not check_system():
        sys.exit(1)

    # 检查项目文件
    if not check_project_files():
        sys.exit(1)

    # 清理构建目录
    clean_build_dirs()

    # 创建配置文件
    spec_file = create_spec_file()

    # 构建可执行文件
    if not build_executable(spec_file):
        sys.exit(1)

    # 复制额外文件
    if not copy_additional_files():
        sys.exit(1)

    # 创建启动脚本
    if not create_startup_script():
        sys.exit(1)

    # 显示结果
    show_results()

if __name__ == '__main__':
    main()
