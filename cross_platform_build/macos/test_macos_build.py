#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 macOS 构建是否成功修复 hashlib.pbkdf2_hmac 问题
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_crypto_modules():
    """测试加密模块"""
    print("🔍 测试 macOS 加密模块...")
    
    try:
        # 添加当前目录到路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        from crypto_compat_macos import safe_generate_password_hash, pbkdf2_hmac_fallback
        
        # 测试后备实现
        password = "test123"
        salt = b"testsalt"
        result = pbkdf2_hmac_fallback('sha256', password, salt, 1000)
        print(f"   ✅ pbkdf2_hmac_fallback 成功: {len(result)} bytes")
        
        # 测试安全密码哈希
        hashed = safe_generate_password_hash(password)
        print(f"   ✅ safe_generate_password_hash 成功: {hashed[:30]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ macOS 加密模块测试失败: {e}")
        return False

def test_app_startup():
    """测试应用启动"""
    print("🚀 测试 macOS 应用启动...")
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    exe_path = os.path.join(project_root, 'dist_mac', 'ReBugTracker')
    
    if not os.path.exists(exe_path):
        print(f"   ❌ 可执行文件不存在: {exe_path}")
        return False
    
    try:
        # 启动应用（后台运行）
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(exe_path)
        )
        
        # 等待应用启动
        print("   ⏳ 等待应用启动...")
        time.sleep(10)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("   ✅ 应用进程正在运行")
            
            # 尝试访问应用
            try:
                response = requests.get("http://127.0.0.1:10001", timeout=5)
                if response.status_code in [200, 302]:  # 302 是重定向到登录页面
                    print("   ✅ 应用响应正常")
                    print(f"   📡 HTTP状态码: {response.status_code}")
                    success = True
                else:
                    print(f"   ⚠️ 应用响应异常: {response.status_code}")
                    success = False
            except requests.exceptions.RequestException as e:
                print(f"   ❌ 无法连接到应用: {e}")
                success = False
            
            # 停止应用
            process.terminate()
            try:
                process.wait(timeout=5)
                print("   ✅ 应用已正常停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print("   ⚠️ 应用被强制停止")
            
            return success
            
        else:
            # 进程已退出，检查错误
            stdout, stderr = process.communicate()
            print(f"   ❌ 应用启动失败")
            print(f"   📝 标准输出: {stdout}")
            print(f"   ❌ 错误输出: {stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ 启动测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 ReBugTracker macOS 构建测试")
    print("=" * 50)
    print("🎯 测试端口: 10001")
    print("=" * 50)
    
    # 检查构建结果
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.exists(os.path.join(project_root, 'dist_mac', 'ReBugTracker')):
        print("❌ 请确保已经构建了 macOS 应用程序")
        print("💡 运行: python build_macos_fixed.py")
        sys.exit(1)
    
    tests = [
        ("macOS 加密模块测试", test_crypto_modules),
        ("macOS 应用启动测试", test_app_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！")
        print("✅ hashlib.pbkdf2_hmac 问题已在 macOS 版本中修复")
        print("✅ 应用可以正常运行在端口 10001")
        print("\n💡 使用方法:")
        print("   cd ../../dist_mac")
        print("   ./ReBugTracker")
        print("   然后访问: http://127.0.0.1:10001")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
