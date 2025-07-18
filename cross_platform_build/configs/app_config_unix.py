#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker Unix系统（macOS/Linux）环境配置模块
处理可执行文件的环境变量和路径配置
"""

import os
import sys
import secrets
from pathlib import Path

def get_app_dir():
    """获取应用程序目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 临时目录
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(sys.executable)
    else:
        # 如果是源码运行
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.abspath(app_dir)

def load_env_file(app_dir):
    """加载.env文件"""
    env_file = os.path.join(app_dir, '.env')

    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
            print(f"📄 已加载环境变量文件: {env_file}")
            return True
        except Exception as e:
            print(f"⚠️ 加载.env文件失败: {e}")
            return False
    else:
        print("📄 未找到.env文件，将使用默认配置")
        return False

def create_default_env_file(app_dir):
    """创建默认的.env文件"""
    env_file = os.path.join(app_dir, '.env')

    # 生成随机密钥
    secret_key = secrets.token_urlsafe(32)

    env_content = f"""# ReBugTracker 环境变量配置
# 此文件由程序自动生成，可以手动修改

# 数据库配置
DB_TYPE=sqlite
SQLITE_DB_PATH=rebugtracker.db

# Flask 配置
SECRET_KEY={secret_key}
FLASK_ENV=production
FLASK_DEBUG=false

# 服务器配置
SERVER_HOST=127.0.0.1
SERVER_PORT=5000

# 文件上传配置
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif
UPLOAD_FOLDER=uploads

# 日志配置
LOG_LEVEL=INFO
LOG_FOLDER=logs

# 其他配置
DATA_EXPORT_FOLDER=data_exports
SESSION_TIMEOUT=3600
ENABLE_REGISTRATION=true
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin
"""

    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"📄 已创建默认.env文件: {env_file}")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False

def ensure_directories(app_dir):
    """确保必要的目录存在"""
    directories = [
        'uploads',
        'logs', 
        'data_exports'
    ]
    
    for directory in directories:
        dir_path = os.path.join(app_dir, directory)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"📁 已创建目录: {directory}")
            except Exception as e:
                print(f"⚠️ 创建目录 {directory} 失败: {e}")

def setup_unix_environment():
    """设置Unix环境"""
    app_dir = get_app_dir()
    
    # 设置工作目录
    os.chdir(app_dir)
    print(f"📂 工作目录: {app_dir}")

    # 确保必要目录存在
    ensure_directories(app_dir)

    # 尝试加载.env文件，如果不存在则创建
    if not load_env_file(app_dir):
        create_default_env_file(app_dir)
        load_env_file(app_dir)

    # 设置基本环境变量（如果.env中没有的话）
    env_defaults = {
        'FLASK_ENV': 'production',
        'DB_TYPE': 'sqlite',
        'SQLITE_DB_PATH': os.path.join(app_dir, 'rebugtracker.db'),
        'UPLOAD_FOLDER': os.path.join(app_dir, 'uploads'),
        'LOG_FOLDER': os.path.join(app_dir, 'logs'),
        'DATA_EXPORT_FOLDER': os.path.join(app_dir, 'data_exports'),
        'SERVER_HOST': '127.0.0.1',
        'SERVER_PORT': '5000',
        'SECRET_KEY': secrets.token_urlsafe(32),
    }

    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = str(default_value)

    print("✅ Unix环境配置完成")
    
    # 显示配置信息
    print(f"🗄️ 数据库类型: {os.environ.get('DB_TYPE', 'sqlite')}")
    print(f"🌐 服务器地址: {os.environ.get('SERVER_HOST', '127.0.0.1')}:{os.environ.get('SERVER_PORT', '5000')}")
    print(f"📁 上传目录: {os.environ.get('UPLOAD_FOLDER', 'uploads')}")
    print(f"📝 日志目录: {os.environ.get('LOG_FOLDER', 'logs')}")

def get_platform_info():
    """获取平台信息"""
    import platform
    
    return {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'app_dir': get_app_dir()
    }

def create_desktop_entry(app_dir):
    """创建Linux桌面快捷方式（仅Linux）"""
    import platform
    
    if platform.system() != 'Linux':
        return False
    
    try:
        desktop_dir = os.path.expanduser('~/.local/share/applications')
        os.makedirs(desktop_dir, exist_ok=True)
        
        desktop_file = os.path.join(desktop_dir, 'rebugtracker.desktop')
        
        desktop_content = f"""[Desktop Entry]
Name=ReBugTracker
Comment=Bug Tracking System
Exec={app_dir}/start_rebugtracker.sh
Icon={app_dir}/static/RBT.ico
Terminal=false
Type=Application
Categories=Development;
StartupNotify=true
"""
        
        with open(desktop_file, 'w', encoding='utf-8') as f:
            f.write(desktop_content)
        
        # 设置执行权限
        os.chmod(desktop_file, 0o755)
        
        print(f"🖥️ 已创建桌面快捷方式: {desktop_file}")
        return True
        
    except Exception as e:
        print(f"⚠️ 创建桌面快捷方式失败: {e}")
        return False

def check_dependencies():
    """检查系统依赖"""
    import platform
    
    print("🔍 检查系统依赖...")
    
    # 检查Python模块
    required_modules = [
        'flask',
        'sqlite3',
        'os',
        'sys'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少必要模块: {', '.join(missing_modules)}")
        return False
    
    print("✅ 系统依赖检查通过")
    return True

# 主要导出函数
__all__ = [
    'setup_unix_environment',
    'get_app_dir',
    'get_platform_info',
    'create_desktop_entry',
    'check_dependencies'
]
