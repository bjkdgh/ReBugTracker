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
    # 必要的Python模块
    (os.path.join(project_root, 'config.py'), '.'),
    (os.path.join(project_root, 'config_adapter.py'), '.'),
    (os.path.join(project_root, 'db_factory.py'), '.'),
    (os.path.join(project_root, 'sql_adapter.py'), '.'),
    # Windows特定配置
    (os.path.join(spec_dir, 'app_config_exe.py'), '.'),
    (os.path.join(spec_dir, 'rebugtracker_exe.py'), '.'),
    # 环境配置
    (os.path.join(project_root, '.env.template'), '.'),
    # 通知系统
    (os.path.join(project_root, 'notification'), 'notification'),
    # 必要目录结构
    (os.path.join(project_root, 'uploads'), 'uploads'),
    (os.path.join(project_root, 'logs'), 'logs'),
    (os.path.join(project_root, 'data_exports'), 'data_exports'),
    # 文档
    (os.path.join(project_root, 'README.md'), '.'),
    (os.path.join(project_root, 'DEPLOYMENT_GUIDE.md'), '.'),
    # 启动和服务脚本
    (os.path.join(spec_dir, 'start_rebugtracker.bat'), '.'),
]

# 数据库文件（如果存在）
db_file = os.path.join(project_root, 'rebugtracker.db')
if os.path.exists(db_file):
    datas.append((db_file, '.'))

# 检查并添加数据库文件
db_file = os.path.join(project_root, 'rebugtracker.db')
if os.path.exists(db_file):
    datas.append((db_file, '.'))

# 隐藏导入（PyInstaller可能无法自动检测的模块）
hiddenimports = [
    # Flask及其依赖
    'flask',
    'flask.app',
    'flask.cli',
    'flask.config',
    'flask.ctx',
    'flask.debughelpers',
    'flask.globals',
    'flask.helpers',
    'flask.json',
    'flask.logging',
    'flask.sessions',
    'flask.signals',
    'flask.templating',
    'flask.wrappers',
    # Flask Extensions
    'flask_login',
    'flask_sqlalchemy',
    'flask_migrate',
    # Werkzeug
    'werkzeug',
    'werkzeug.security',
    'werkzeug.utils',
    'werkzeug.datastructures',
    'werkzeug.debug',
    'werkzeug.exceptions',
    'werkzeug.formparser',
    'werkzeug.http',
    'werkzeug.local',
    'werkzeug.middleware',
    'werkzeug.middleware.proxy_fix',
    'werkzeug.routing',
    'werkzeug.serving',
    'werkzeug.test',
    'werkzeug.urls',
    'werkzeug.user_agent',
    'werkzeug.wsgi',
    # Jinja2
    'jinja2',
    'jinja2.ext',
    'jinja2.filters',
    'jinja2.loaders',
    'jinja2.runtime',
    'jinja2.nodes',
    'jinja2.parser',
    'jinja2.compiler',
    'jinja2.environment',
    'jinja2.meta',
    'jinja2.optimizer',
    'jinja2.sandbox',
    'jinja2.tests',
    'jinja2.visitor',
    # 基础依赖
    'markupsafe',
    'itsdangerous',
    'click',
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'sqlite3',
    'waitress',
    # 项目特定模块
    'notification',
    'notification.channels',
    'notification.cleanup_manager',
    'notification.flow_rules',
    'notification.notification_manager',
    'notification.simple_notifier',
    # 其他必要依赖
    'sqlalchemy',
    'datetime',
    'json',
    'logging'
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
