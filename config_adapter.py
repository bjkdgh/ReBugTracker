#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置适配器
兼容原有的config.py，同时支持exe环境的配置管理
"""

import os
import sys

# 检测是否在exe环境中
if getattr(sys, 'frozen', False):
    # 在exe环境中，先加载exe配置
    try:
        from app_config_exe import setup_exe_environment
        setup_exe_environment()
    except ImportError:
        pass

# 数据库类型配置
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')

# PostgreSQL配置
POSTGRES_CONFIG = {
    'dbname': os.getenv('DATABASE_NAME', 'rebugtracker'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', 'your_password_here'),
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', '5432'))
}

# SQLite配置
SQLITE_CONFIG = {
    'database': os.getenv('SQLITE_DB_PATH', 'rebugtracker.db')
}

# 统一数据库配置接口
DATABASE_CONFIG = {
    'postgres': POSTGRES_CONFIG,
    'sqlite': SQLITE_CONFIG
}

# 文件上传配置
ALLOWED_EXTENSIONS_STR = os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif')
ALLOWED_EXTENSIONS = set(ext.strip() for ext in ALLOWED_EXTENSIONS_STR.split(','))

MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB

# Flask应用配置
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-this')
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# 服务器配置
SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.getenv('SERVER_PORT', '5000'))

# 目录配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
LOG_FOLDER = os.getenv('LOG_FOLDER', 'logs')
DATA_EXPORT_FOLDER = os.getenv('DATA_EXPORT_FOLDER', 'data_exports')

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 会话配置
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))

# 功能开关
ENABLE_REGISTRATION = os.getenv('ENABLE_REGISTRATION', 'true').lower() == 'true'

# 默认管理员配置
DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin')

# 邮件配置
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME', 'ReBugTracker')
MAIL_FROM_EMAIL = os.getenv('MAIL_FROM_EMAIL', '')

# Gotify配置
GOTIFY_SERVER_URL = os.getenv('GOTIFY_SERVER_URL', '')
GOTIFY_APP_TOKEN = os.getenv('GOTIFY_APP_TOKEN', '')

def get_config_summary():
    """获取配置摘要（用于调试）"""
    return {
        'DB_TYPE': DB_TYPE,
        'FLASK_ENV': FLASK_ENV,
        'SERVER_HOST': SERVER_HOST,
        'SERVER_PORT': SERVER_PORT,
        'UPLOAD_FOLDER': UPLOAD_FOLDER,
        'LOG_FOLDER': LOG_FOLDER,
        'ENABLE_REGISTRATION': ENABLE_REGISTRATION,
        'SECRET_KEY_SET': bool(SECRET_KEY and SECRET_KEY != 'default-secret-key-change-this'),
    }

def validate_config():
    """验证配置"""
    errors = []
    warnings = []
    
    # 检查必要配置
    if SECRET_KEY == 'default-secret-key-change-this':
        warnings.append("使用默认SECRET_KEY，建议修改")
    
    if DB_TYPE == 'postgres':
        if not POSTGRES_CONFIG['password'] or POSTGRES_CONFIG['password'] == 'your_password_here':
            errors.append("PostgreSQL密码未设置")
        if not POSTGRES_CONFIG['host']:
            errors.append("PostgreSQL主机地址未设置")
    
    if DB_TYPE == 'sqlite':
        if not SQLITE_CONFIG['database']:
            errors.append("SQLite数据库路径未设置")
    
    # 检查目录权限
    for folder_name, folder_path in [
        ('UPLOAD_FOLDER', UPLOAD_FOLDER),
        ('LOG_FOLDER', LOG_FOLDER),
        ('DATA_EXPORT_FOLDER', DATA_EXPORT_FOLDER)
    ]:
        if not os.path.isabs(folder_path):
            # 相对路径，检查当前目录
            full_path = os.path.abspath(folder_path)
        else:
            full_path = folder_path
        
        parent_dir = os.path.dirname(full_path)
        if not os.access(parent_dir, os.W_OK):
            warnings.append(f"{folder_name} 目录可能无写入权限: {full_path}")
    
    return errors, warnings

# 兼容性：保持与原config.py的接口一致
# 这样原有代码无需修改即可使用
if __name__ == '__main__':
    # 配置验证和调试信息
    print("🔧 ReBugTracker 配置信息:")
    print("=" * 40)
    
    config_summary = get_config_summary()
    for key, value in config_summary.items():
        print(f"{key}: {value}")
    
    print("\n🔍 配置验证:")
    errors, warnings = validate_config()
    
    if errors:
        print("❌ 错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("⚠️ 警告:")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("✅ 配置验证通过")
