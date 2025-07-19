#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker macOS 启动脚本
专门用于 macOS PyInstaller 打包的启动脚本
"""

import sys
import os
import socket
import time
import threading
from pathlib import Path

# 在导入其他模块之前，先导入加密兼容性模块
try:
    import crypto_compat_macos
    print("✅ macOS 加密兼容性模块已加载")
except ImportError as e:
    print(f"⚠️ macOS 加密兼容性模块加载失败: {e}")

# 导入 macOS 专用配置
from app_config_macos import setup_macos_environment, get_server_config

def check_port_available(host, port):
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"⚠️ 端口 {port} 已被占用，正在尝试其他端口...")
            return False
        return True
    except Exception as e:
        print(f"检查端口时出错: {e}")
        return False

def find_available_port(host, start_port=10001, max_attempts=10):
    """查找可用端口 - macOS 默认从 10001 开始"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(host, port):
            return port
    return None

def setup_paths():
    """设置路径和环境变量"""
    # 获取应用目录
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        app_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录
    os.chdir(app_dir)
    
    # 创建必要目录
    directories = ['uploads', 'logs', 'data_exports']
    for directory in directories:
        full_path = os.path.join(app_dir, directory)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"📁 创建目录: {full_path}")

def init_database():
    """初始化数据库"""
    try:
        # 添加项目根目录到路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, project_root)

        from rebugtracker import init_db
        print("🗄️ 初始化数据库...")
        init_db()
        print("✅ 数据库初始化完成")

        # macOS 专用：修复 admin 用户数据
        fix_admin_user_data()

        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def fix_admin_user_data():
    """修复 admin 用户的中文名和团队信息"""
    try:
        print("🔧 修复 admin 用户数据...")

        # 导入必要的模块
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, project_root)

        from db_factory import get_db_connection
        from sql_adapter import adapt_sql

        conn = get_db_connection()
        if hasattr(conn, 'cursor'):
            cursor = conn.cursor()
        else:
            cursor = conn

        # 检查 admin 用户
        query, params = adapt_sql("SELECT id, username, chinese_name, team, role, role_en FROM users WHERE username = %s", ('admin',))
        cursor.execute(query, params)
        admin_user = cursor.fetchone()

        if admin_user:
            # 根据数据库类型处理结果
            if hasattr(admin_user, '_asdict'):  # DictCursor
                user_data = admin_user._asdict()
                user_id = user_data['id']
                chinese_name = user_data.get('chinese_name')
                team = user_data.get('team')
                role_en = user_data.get('role_en')
            else:  # 普通 cursor
                user_id, username, chinese_name, team, role, role_en = admin_user

            # 检查是否需要更新
            updates = []
            params = []

            if not chinese_name:
                updates.append("chinese_name = %s")
                params.append("系统管理员")

            if not team:
                updates.append("team = %s")
                params.append("管理员")

            if not role_en or role_en != 'gly':
                updates.append("role_en = %s")
                params.append("gly")

            # 尝试设置 team_en
            try:
                updates.append("team_en = %s")
                params.append("gly")
            except:
                pass

            if updates:
                # 执行更新
                params.append(user_id)
                update_sql = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                query, final_params = adapt_sql(update_sql, tuple(params))
                cursor.execute(query, final_params)
                conn.commit()
                print("   ✅ 已修复 admin 用户信息")
            else:
                print("   ℹ️ admin 用户信息已完整")

        conn.close()

    except Exception as e:
        print(f"   ⚠️ admin 用户修复失败: {e}")
        # 不影响主程序启动

def start_cleanup_scheduler():
    """启动清理调度器"""
    try:
        print("🧹 启动通知清理调度器...")
        from notification.cleanup_manager import cleanup_manager
        cleanup_manager.start_cleanup_scheduler(interval_hours=24)
        return True
    except Exception as e:
        print(f"⚠️ 清理调度器启动失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 ReBugTracker macOS 版本启动中...")
    print("=" * 50)
    
    # 设置环境
    setup_macos_environment()
    setup_paths()
    
    # 初始化数据库
    if not init_database():
        input("按回车键退出...")
        return
    
    # 启动清理调度器
    start_cleanup_scheduler()
    
    # 获取服务器配置
    HOST, PORT = get_server_config()
    
    # 检查端口是否可用，如果不可用则寻找其他端口
    if not check_port_available(HOST, PORT):
        PORT = find_available_port(HOST, PORT)
        if PORT is None:
            print("❌ 无法找到可用端口")
            input("按回车键退出...")
            return
    
    print(f"🌐 使用端口: {PORT}")
    
    try:
        # 导入并启动 Flask 应用
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, project_root)
        
        from rebugtracker import app
        
        print(f"📡 应用程序启动在: http://{HOST}:{PORT}")
        print("💡 按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动应用
        app.run(host=HOST, port=PORT, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 应用程序已停止")
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        input("按回车键退出...")

if __name__ == '__main__':
    main()
