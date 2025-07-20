# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# 项目根目录
project_root = r'/Users/guohao/src/ReBugTracker'

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
    # 加密兼容性模块
    (os.path.join(project_root, 'cross_platform_build/crypto_compat.py'), '.'),
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
    hooksconfig={},
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
