"""
ReBugTracker macOS 专用配置文件
处理 macOS 打包后的路径和配置问题
"""

import os
import sys
import configparser
import secrets
from pathlib import Path

def get_app_dir():
    """获取应用目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return base_path

def get_resource_path(relative_path):
    """获取资源文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe环境
        base_path = sys._MEIPASS
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

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
    """创建默认的.env文件 - macOS版本"""
    env_file = os.path.join(app_dir, '.env')

    # 生成随机密钥
    secret_key = secrets.token_urlsafe(32)

    env_content = f"""# ReBugTracker macOS 环境变量配置
# 此文件由程序自动生成，可以手动修改

# 数据库配置
DB_TYPE=sqlite
SQLITE_DB_PATH=rebugtracker.db

# Flask 配置
SECRET_KEY={secret_key}
FLASK_ENV=production
FLASK_DEBUG=false

# 服务器配置 - macOS 默认端口
SERVER_HOST=127.0.0.1
SERVER_PORT=10001

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

def setup_macos_environment():
    """设置 macOS 环境"""
    app_dir = get_app_dir()

    # 设置工作目录
    os.chdir(app_dir)

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
        'SERVER_PORT': '10001',  # macOS 默认端口
        'SECRET_KEY': secrets.token_urlsafe(32),
    }

    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = str(default_value)

    # 创建必要目录
    directories = [
        os.environ.get('UPLOAD_FOLDER', 'uploads'),
        os.environ.get('LOG_FOLDER', 'logs'),
        os.environ.get('DATA_EXPORT_FOLDER', 'data_exports')
    ]

    for directory in directories:
        if not os.path.isabs(directory):
            directory = os.path.join(app_dir, directory)
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_server_config():
    """获取服务器配置"""
    host = os.environ.get('SERVER_HOST', '127.0.0.1')
    port = int(os.environ.get('SERVER_PORT', '10001'))  # macOS 默认端口
    return host, port

# 在导入时自动设置环境
if __name__ != '__main__':
    setup_macos_environment()
