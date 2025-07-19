# -*- mode: python ; coding: utf-8 -*-
"""
ReBugTracker macOS PyInstaller 配置文件
专门用于 macOS 平台的打包配置
"""

import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(SPEC))))
macos_build_dir = os.path.dirname(os.path.abspath(SPEC))

# 数据文件和目录
datas = [
    # 模板文件
    (os.path.join(project_root, 'templates'), 'templates'),
    # 静态文件
    (os.path.join(project_root, 'static'), 'static'),
    # 配置文件
    (os.path.join(project_root, 'config.py'), '.'),
    (os.path.join(project_root, 'config_adapter.py'), '.'),
    
    # macOS 专用配置文件
    (os.path.join(macos_build_dir, 'app_config_macos.py'), '.'),
    (os.path.join(macos_build_dir, 'crypto_compat_macos.py'), '.'),

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

# 隐藏导入（PyInstaller可能无法自动检测的模块）
hiddenimports = [
    # Flask核心
    'flask',
    'werkzeug',
    'werkzeug.security',
    'werkzeug.utils',
    'jinja2',
    'jinja2.ext',
    'markupsafe',
    'itsdangerous',
    'click',
    'blinker',

    # 数据库驱动
    'psycopg2',
    'psycopg2.extras',
    'psycopg2.pool',
    'sqlite3',

    # WSGI服务器
    'waitress',
    'waitress.server',

    # HTTP请求
    'requests',
    'requests.adapters',
    'requests.auth',
    'urllib3',

    # 文档处理
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',

    # 图像处理
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageFilter',

    # 通知系统
    'notification',
    'notification.notification_manager',
    'notification.cleanup_manager',
    'notification.simple_notifier',
    'notification.flow_rules',
    'notification.channels',

    # 邮件
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'email.mime.base',
    'smtplib',

    # 系统模块
    'threading',
    'schedule',
    'datetime',
    'json',
    'uuid',
    'hashlib',
    '_hashlib',  # 重要：macOS 底层hashlib模块
    'base64',
    'urllib.parse',
    'functools',
    'traceback',
    'pathlib',
    'webbrowser',
    'socket',
    'time',
    'os',
    'sys',
    'configparser',
    'logging',
    'logging.handlers',

    # 加密和安全 - macOS 专用
    'secrets',
    'hmac',
    '_sha1',
    '_sha256',
    '_sha512',
    '_md5',
    'binascii',

    # macOS 专用模块
    'crypto_compat_macos',
    'app_config_macos',

    # 数据处理
    'csv',
    'io',
    'tempfile',
    'shutil',
]

# 排除的模块（减少打包大小）
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'unittest',
    'doctest',
]

# 分析配置
a = Analysis(
    [os.path.join(macos_build_dir, 'rebugtracker_macos.py')],  # macOS 专用启动脚本
    pathex=[project_root, macos_build_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[macos_build_dir],  # 使用 macOS 专用 hook 路径
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 处理重复文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ReBugTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩（如果可用）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # macOS 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'static', 'RBT.ico') if os.path.exists(os.path.join(project_root, 'static', 'RBT.ico')) else None,
)

# 收集所有文件到 dist_mac 目录
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dist_mac'  # 输出到 dist_mac 目录
)
