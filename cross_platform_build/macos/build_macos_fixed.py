#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker macOS 构建脚本（修复版）
解决 hashlib.pbkdf2_hmac 缺失问题
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理 macOS 构建目录...")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    dirs_to_clean = [
        os.path.join(project_root, 'build'),
        os.path.join(project_root, 'dist_mac'),
        os.path.join(project_root, '__pycache__')
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"   ✅ 已删除 {dir_path}")
    
    # 清理 .pyc 文件
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def check_dependencies():
    """检查依赖"""
    print("📦 检查 macOS 构建依赖...")
    
    required_modules = [
        'flask',
        'werkzeug', 
        'psycopg2',
        'waitress',
        'requests',
        'openpyxl',
        'reportlab'
    ]
    
    # 可选依赖
    optional_modules = [
        'PIL'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module} (缺失)")
    
    # 检查可选依赖
    for module in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} (可选)")
        except ImportError:
            print(f"   ⚠️ {module} (可选，缺失)")
    
    if missing_modules:
        print(f"\n⚠️ 缺失必需依赖: {', '.join(missing_modules)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def test_crypto_compat():
    """测试加密兼容性模块"""
    print("🔐 测试 macOS 加密兼容性...")
    
    try:
        # 添加当前目录到路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        from crypto_compat_macos import safe_generate_password_hash
        
        # 测试密码哈希
        test_password = "test123"
        hashed = safe_generate_password_hash(test_password)
        print(f"   ✅ macOS 密码哈希测试通过: {hashed[:20]}...")
        
        return True
    except Exception as e:
        print(f"   ❌ macOS 加密兼容性测试失败: {e}")
        return False

def build_app():
    """构建 macOS 应用"""
    print("🔨 开始构建 macOS 应用...")
    
    # 获取当前目录和项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 构建命令
    spec_file = os.path.join(current_dir, 'rebugtracker_macos.spec')
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        spec_file
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print(f"工作目录: {project_root}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=project_root)
        print("✅ macOS 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ macOS 构建失败!")
        print(f"错误输出: {e.stderr}")
        return False

def test_built_app():
    """测试构建的 macOS 应用"""
    print("🧪 测试构建的 macOS 应用...")
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    exe_path = os.path.join(project_root, 'dist_mac', 'ReBugTracker')
    
    if not os.path.exists(exe_path):
        print(f"❌ macOS 可执行文件不存在: {exe_path}")
        return False
    
    print(f"✅ macOS 可执行文件存在: {exe_path}")
    
    # 检查文件大小
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"📏 文件大小: {size_mb:.1f} MB")
    
    # 设置执行权限
    os.chmod(exe_path, 0o755)
    print("✅ 已设置执行权限")
    
    return True

def main():
    """主函数"""
    print("🚀 ReBugTracker macOS 构建（修复版）")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(current_dir, 'rebugtracker_macos.spec')):
        print("❌ 请在 cross_platform_build/macos 目录运行此脚本")
        sys.exit(1)
    
    # 步骤1: 清理构建目录
    clean_build_dirs()
    
    # 步骤2: 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 步骤3: 测试加密兼容性
    if not test_crypto_compat():
        sys.exit(1)
    
    # 步骤4: 构建应用
    if not build_app():
        sys.exit(1)
    
    # 步骤5: 测试构建结果
    if not test_built_app():
        sys.exit(1)
    
    print("\n🎉 macOS 构建完成!")
    print("💡 使用方法:")
    print("   cd ../../dist_mac")
    print("   ./ReBugTracker")
    print("   然后访问: http://127.0.0.1:10001")
    print("\n✅ hashlib.pbkdf2_hmac 问题已在 macOS 版本中修复")

if __name__ == '__main__':
    main()
