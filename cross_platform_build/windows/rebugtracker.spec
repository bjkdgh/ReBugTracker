# -*- mode: python ; coding: utf-8 -*-
"""
ReBugTracker PyInstaller 配置文件
用于将Flask应用打包成Windows可执行文件
"""

import os
import sys
from pathlib import Path

# 获取项目根目录 (从 cross_platform_build/windows 回到根目录)
spec_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(os.path.dirname(spec_dir))

# 数据文件和目录
datas = [
    # 模板文件
    (os.path.join(project_root, 'templates'), 'templates'),
    # 静态文件
    (os.path.join(project_root, 'static'), 'static'),
    # 配置文件
    (os.path.join(project_root, 'config.py'), '.'),
    (os.path.join(spec_dir, 'app_config_exe.py'), '.'),
    (os.path.join(project_root, 'config_adapter.py'), '.'),

    # 环境变量模板
    (os.path.join(project_root, '.env.template'), '.'),
    # 数据库工厂和适配器
    (os.path.join(project_root, 'db_factory.py'), '.'),
    (os.path.join(project_root, 'sql_adapter.py'), '.'),
    # 通知系统
    (os.path.join(project_root, 'notification'), 'notification'),
    # 数据库文件（如果存在）
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
    'pillow',
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
    'notification.channels.email_channel',
    'notification.channels.gotify_channel',
    'notification.channels.inapp_channel',

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


    # 加密和安全
    'secrets',
    'hmac',

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
    [os.path.join(spec_dir, 'rebugtracker_exe.py')],  # 主入口文件
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
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
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'static', 'RBT.ico') if os.path.exists(os.path.join(project_root, 'static', 'RBT.ico')) else None,
    version_file=None,
)

# 收集所有文件到一个目录（可选）
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='ReBugTracker'
# )
