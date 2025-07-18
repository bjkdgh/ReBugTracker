#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker EXE专用配置文件
处理打包后的路径和配置问题
"""

import os
import sys
import configparser
import secrets
from pathlib import Path

def get_app_dir():
    """获取应用目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe环境
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    """获取资源文件路径（兼容开发和打包环境）"""
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

def setup_exe_environment():
    """设置exe环境"""
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
        'SERVER_PORT': '5000',
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
            print(f"📁 创建目录: {directory}")

    return app_dir

def load_config():
    """加载配置文件"""
    app_dir = get_app_dir()
    config_file = os.path.join(app_dir, 'app_config.ini')
    
    config = configparser.ConfigParser()
    
    # 默认配置
    default_config = {
        'database': {
            'type': 'sqlite',
            'sqlite_path': 'rebugtracker.db'
        },
        'server': {
            'host': '127.0.0.1',
            'port': '5000',
            'debug': 'false'
        },
        'security': {
            'secret_key': 'rebugtracker-exe-default-key-change-this'
        },
        'uploads': {
            'max_file_size': '16777216',
            'allowed_extensions': 'png,jpg,jpeg,gif'
        }
    }
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_file):
        for section, options in default_config.items():
            config.add_section(section)
            for key, value in options.items():
                config.set(section, key, value)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
        except Exception as e:
            print(f"创建配置文件失败: {e}")
    else:
        # 读取现有配置
        try:
            config.read(config_file, encoding='utf-8')
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            # 使用默认配置
            for section, options in default_config.items():
                config.add_section(section)
                for key, value in options.items():
                    config.set(section, key, value)
    
    return config

def apply_config_to_env(config):
    """将配置应用到环境变量"""
    try:
        # 数据库配置
        if config.has_section('database'):
            if config.has_option('database', 'type'):
                os.environ['DB_TYPE'] = config.get('database', 'type')
            if config.has_option('database', 'sqlite_path'):
                app_dir = get_app_dir()
                db_path = os.path.join(app_dir, config.get('database', 'sqlite_path'))
                os.environ['SQLITE_DB_PATH'] = db_path
        
        # 服务器配置
        if config.has_section('server'):
            if config.has_option('server', 'host'):
                os.environ['SERVER_HOST'] = config.get('server', 'host')
            if config.has_option('server', 'port'):
                os.environ['SERVER_PORT'] = config.get('server', 'port')
        
        # 安全配置
        if config.has_section('security'):
            if config.has_option('security', 'secret_key'):
                os.environ['SECRET_KEY'] = config.get('security', 'secret_key')
        
        # 上传配置
        if config.has_section('uploads'):
            if config.has_option('uploads', 'max_file_size'):
                os.environ['MAX_CONTENT_LENGTH'] = config.get('uploads', 'max_file_size')
            if config.has_option('uploads', 'allowed_extensions'):
                os.environ['ALLOWED_EXTENSIONS'] = config.get('uploads', 'allowed_extensions')
    
    except Exception as e:
        print(f"应用配置失败: {e}")

def get_server_config():
    """获取服务器配置"""
    host = os.environ.get('SERVER_HOST', '127.0.0.1')
    port = int(os.environ.get('SERVER_PORT', '5000'))
    return host, port

# 在导入时自动设置环境
if __name__ != '__main__':
    setup_exe_environment()
    config = load_config()
    apply_config_to_env(config)
