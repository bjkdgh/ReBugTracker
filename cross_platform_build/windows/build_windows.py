#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker Windows 打包脚本
支持在 Windows 系统上打包 ReBugTracker 为可执行文件
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
    
    if platform.system() != 'Windows':
        print_error("此脚本只能在 Windows 系统上运行")
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
        print_error("PyInstaller 未安装，请运行: pip install pyinstaller")
        return False
    
    return True

def get_project_root():
    """获取项目根目录"""
    # 从 cross_platform_build/windows 回到项目根目录
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    return project_root.resolve()

def setup_build_environment():
    """设置构建环境"""
    print_step(2, "设置构建环境")
    
    project_root = get_project_root()
    print_success(f"项目根目录: {project_root}")
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 检查必要文件
    required_files = [
        'rebugtracker.py',
        'config.py',
        'db_factory.py',
        'sql_adapter.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not (project_root / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print_error(f"缺少必要文件: {', '.join(missing_files)}")
        return False
    
    print_success("所有必要文件都存在")
    return True

def clean_build_dirs():
    """清理构建目录"""
    print_step(3, "清理构建目录")
    
    dirs_to_clean = ['build', '__pycache__']
    
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
    print_step(4, "运行PyInstaller打包")
    
    # 使用windows目录下的spec文件
    windows_dir = Path(__file__).parent
    spec_file = windows_dir / 'rebugtracker.spec'
    
    if not spec_file.exists():
        print_error(f"未找到spec文件: {spec_file}")
        return False
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    print(f"🔧 执行命令: {' '.join(cmd)}")
    print()
    
    try:
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
    print_step(5, "复制额外文件")
    
    windows_dir = Path(__file__).parent
    dist_dir = windows_dir / 'dist'
    
    if not dist_dir.exists():
        print_error("dist目录不存在")
        return False
    
    project_root = get_project_root()
    
    # 要复制的文件和目录
    items_to_copy = [
        ('rebugtracker.db', '数据库文件'),
        ('uploads', '上传文件目录'),
        ('logs', '日志目录'),
        ('data_exports', '数据导出目录'),
        ('README.md', '说明文档'),
    ]
    
    for item, description in items_to_copy:
        source = project_root / item
        if source.exists():
            dest = dist_dir / item
            try:
                if source.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                else:
                    shutil.copy2(source, dest)
                print_success(f"已复制 {description}: {item}")
            except Exception as e:
                print_warning(f"复制 {item} 失败: {e}")
        else:
            print(f"📁 {item} 不存在，跳过")

def create_startup_scripts():
    """创建启动脚本"""
    print_step(6, "创建启动脚本和说明文档")
    
    windows_dir = Path(__file__).parent
    dist_dir = windows_dir / 'dist'
    
    # 这些脚本已经在移动过程中包含在dist目录中了
    scripts = ['start_rebugtracker.bat', 'install_service.bat', 'manage_service.bat']
    
    for script in scripts:
        script_path = dist_dir / script
        if script_path.exists():
            print_success(f"启动脚本已存在: {script}")
        else:
            print_warning(f"启动脚本不存在: {script}")

def show_results():
    """显示打包结果"""
    print_step(7, "打包完成")
    
    windows_dir = Path(__file__).parent
    dist_dir = windows_dir / 'dist'
    
    if dist_dir.exists():
        print_success(f"输出目录: {dist_dir.absolute()}")
        
        # 列出主要文件
        exe_file = dist_dir / 'ReBugTracker.exe'
        if exe_file.exists():
            size = exe_file.stat().st_size / (1024 * 1024)  # MB
            print_success(f"可执行文件: ReBugTracker.exe ({size:.1f} MB)")
        
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
    print("🚀 ReBugTracker Windows 打包工具")
    print("=" * 60)
    
    # 检查系统环境
    if not check_system():
        return False
    
    # 设置构建环境
    if not setup_build_environment():
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 运行PyInstaller
    if not run_pyinstaller():
        return False
    
    # 复制额外文件
    copy_additional_files()
    
    # 检查启动脚本
    create_startup_scripts()
    
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
