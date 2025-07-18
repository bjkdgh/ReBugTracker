#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker EXE打包脚本
使用PyInstaller将Flask应用打包成Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🚀 ReBugTracker EXE 打包工具")
    print("=" * 60)
    print()

def print_step(step, message):
    """打印步骤信息"""
    print(f"📋 步骤 {step}: {message}")

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_warning(message):
    """打印警告信息"""
    print(f"⚠️ {message}")

def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")

def check_requirements():
    """检查打包要求"""
    print_step(1, "检查打包要求")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version < (3, 8):
        print_error(f"Python版本过低: {python_version.major}.{python_version.minor}")
        print("需要Python 3.8或更高版本")
        return False
    print_success(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print_success(f"PyInstaller已安装: {PyInstaller.__version__}")
    except ImportError:
        print_error("PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查必要文件
    required_files = [
        'rebugtracker.py',
        'rebugtracker_exe.py',
        'rebugtracker.spec',
        'config.py',
        'db_factory.py',
        'sql_adapter.py',
        'requirements.txt'
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
    print_step(2, "清理构建目录")
    
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

def run_pyinstaller():
    """运行PyInstaller"""
    print_step(3, "运行PyInstaller打包")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不询问覆盖
        'rebugtracker.spec'  # 使用spec文件
    ]
    
    print(f"🔧 执行命令: {' '.join(cmd)}")
    print()
    
    try:
        # 运行PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        print_success("PyInstaller打包完成")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"PyInstaller打包失败: {e}")
        return False
    except Exception as e:
        print_error(f"执行PyInstaller时出错: {e}")
        return False

def copy_additional_files():
    """复制额外文件到dist目录"""
    print_step(4, "复制额外文件")
    
    dist_dir = 'dist'
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

def create_startup_script():
    """创建启动脚本"""
    print_step(5, "创建启动脚本")
    
    dist_dir = 'dist'
    script_content = '''@echo off
chcp 65001 >nul
REM ReBugTracker 启动脚本
title ReBugTracker 启动器

echo.
echo ========================================
echo   🚀 ReBugTracker 缺陷跟踪系统
echo ========================================
echo.

REM 检查可执行文件是否存在
if not exist "ReBugTracker.exe" (
    echo ❌ 错误: ReBugTracker.exe 不存在
    echo 请确保在正确的目录中运行此脚本
    echo.
    pause
    exit /b 1
)

REM 检查配置文件
if not exist "app_config.ini" (
    echo 📄 首次运行，将创建默认配置文件
)

REM 检查数据库文件
if not exist "rebugtracker.db" (
    echo 🗄️ 首次运行，将初始化数据库
)

echo 📡 正在启动应用程序...
echo 💡 启动后会自动打开浏览器
echo.

REM 启动应用（在新窗口中）
start "ReBugTracker" "ReBugTracker.exe"

echo ✅ 应用程序已启动
echo.
echo 📌 使用说明:
echo    - 默认访问地址: http://127.0.0.1:5000
echo    - 默认管理员: admin / admin
echo    - 配置文件: app_config.ini
echo    - 数据库文件: rebugtracker.db
echo.
echo 🔧 如需停止服务，请关闭ReBugTracker窗口
echo.
echo 按任意键关闭此窗口...
pause >nul
'''
    
    script_path = os.path.join(dist_dir, 'start_rebugtracker.bat')
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print_success(f"已创建启动脚本: {script_path}")
        return True
    except Exception as e:
        print_error(f"创建启动脚本失败: {e}")
        return False

def create_config_info():
    """创建配置说明文件"""
    print_step(6, "创建配置说明")

    dist_dir = 'dist'
    if not os.path.exists(dist_dir):
        print_error("dist目录不存在")
        return False

    # 创建配置说明文件
    config_info_content = '''# ReBugTracker 配置说明

## 📋 配置文件位置
- `.env` - 主配置文件（程序自动生成）
- `.env.template` - 配置模板文件

## 🔧 修改配置的方法

### 1. 编辑 .env 文件
用记事本或任何文本编辑器打开 `.env` 文件进行修改：
```
notepad .env
```

### 2. 常用配置项

#### 修改端口
```
SERVER_PORT=8080
```

#### 切换到PostgreSQL数据库
```
DB_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_NAME=rebugtracker
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
```

#### 修改文件路径
```
UPLOAD_FOLDER=D:\\MyUploads
LOG_FOLDER=D:\\MyLogs
SQLITE_DB_PATH=D:\\MyData\\rebugtracker.db
```

#### 配置邮件通知
```
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your_email@qq.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
```

## ⚠️ 注意事项
1. 修改配置后需要重启应用
2. 路径中的反斜杠需要使用双反斜杠 `\\`
3. 密码等敏感信息请妥善保管
4. 建议修改前备份原配置文件

## 🔄 应用配置的步骤
1. 停止ReBugTracker应用
2. 编辑 .env 文件
3. 保存文件
4. 重新启动应用
'''

    config_info_path = os.path.join(dist_dir, '配置说明.md')
    try:
        with open(config_info_path, 'w', encoding='utf-8') as f:
            f.write(config_info_content)
        print_success(f"已创建配置说明: {config_info_path}")
        return True
    except Exception as e:
        print_error(f"创建配置说明失败: {e}")
        return False



def create_readme():
    """创建使用说明"""
    print_step(7, "创建使用说明")
    
    dist_dir = 'dist'
    readme_content = '''# ReBugTracker 可执行版本

## 📋 使用说明

### 快速启动
1. 双击 `start_rebugtracker.bat` 启动应用
2. 或者直接运行 `ReBugTracker.exe`
3. 应用启动后会自动打开浏览器访问 http://127.0.0.1:5000

### 文件说明
- `ReBugTracker.exe` - 主程序
- `start_rebugtracker.bat` - 启动脚本
- `配置说明.md` - 配置修改说明文档
- `rebugtracker.db` - SQLite数据库文件
- `.env` - 环境变量配置文件（自动生成）
- `.env.template` - 配置模板文件
- `uploads/` - 文件上传目录
- `logs/` - 日志文件目录
- `data_exports/` - 数据导出目录

### 配置修改
1. **编辑配置文件**: 用记事本打开 `.env` 文件进行修改
2. **参考说明**: 查看 `配置说明.md` 了解详细配置方法

### 常用配置修改
- **修改端口**: 在.env中设置 `SERVER_PORT=8080`
- **切换数据库**: 设置 `DB_TYPE=postgres` 并配置数据库连接
- **修改上传目录**: 设置 `UPLOAD_FOLDER=D:\\MyUploads`
- **配置邮件**: 设置SMTP服务器相关参数

### 配置修改步骤
1. 停止ReBugTracker应用
2. 用记事本打开 `.env` 文件: `notepad .env`
3. 修改需要的配置项
4. 保存文件
5. 重新启动应用

### 注意事项
1. 首次运行会自动初始化数据库
2. 默认管理员账号: admin / admin
3. 请及时修改默认密码
4. 数据库文件包含所有数据，请注意备份
5. 修改配置后需要重启应用

### 故障排除
1. 如果端口5000被占用，程序会自动寻找其他可用端口
2. 如果启动失败，请检查控制台输出的错误信息
3. 确保有足够的磁盘空间用于数据库和上传文件

### 技术支持
- 项目地址: https://github.com/bjkdgh/ReBugTracker
- 问题反馈: 请在GitHub上提交Issue

---
构建时间: ''' + time.strftime('%Y-%m-%d %H:%M:%S') + '''
'''
    
    readme_path = os.path.join(dist_dir, 'README_EXE.md')
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print_success(f"已创建使用说明: {readme_path}")
        return True
    except Exception as e:
        print_error(f"创建使用说明失败: {e}")
        return False

def show_results():
    """显示打包结果"""
    print()
    print("=" * 60)
    print("🎉 打包完成!")
    print("=" * 60)
    
    dist_dir = 'dist'
    if os.path.exists(dist_dir):
        print(f"📂 输出目录: {os.path.abspath(dist_dir)}")
        
        # 列出主要文件
        exe_file = os.path.join(dist_dir, 'ReBugTracker.exe')
        if os.path.exists(exe_file):
            size = os.path.getsize(exe_file) / (1024 * 1024)  # MB
            print(f"📦 可执行文件: ReBugTracker.exe ({size:.1f} MB)")
        
        print()
        print("🚀 使用方法:")
        print("1. 进入 dist 目录")
        print("2. 双击 start_rebugtracker.bat 启动")
        print("3. 或直接运行 ReBugTracker.exe")
        print()
        print("💡 提示: 首次运行会自动初始化数据库")
    else:
        print_error("dist目录不存在，打包可能失败")

def main():
    """主函数"""
    print_banner()
    
    # 检查要求
    if not check_requirements():
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 运行PyInstaller
    if not run_pyinstaller():
        return False
    
    # 复制额外文件
    copy_additional_files()
    
    # 创建启动脚本
    create_startup_script()

    # 创建配置说明
    create_config_info()

    # 创建使用说明
    create_readme()
    
    # 显示结果
    show_results()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n✅ 打包成功完成!")
        else:
            print("\n❌ 打包失败!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断打包过程")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 打包过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        input("\n按回车键退出...")
