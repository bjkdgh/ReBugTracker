#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker EXE启动脚本
专门用于PyInstaller打包的启动脚本
"""

import sys
import os
import socket
import time
import threading
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# 导入exe专用配置
from app_config_exe import setup_exe_environment, load_config, apply_config_to_env, get_server_config

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

def find_available_port(host, start_port=5000, max_attempts=10):
    """查找可用端口"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(host, port):
            return port
    return None

def setup_paths():
    """设置路径和环境变量"""
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        app_dir = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录
    os.chdir(app_dir)
    
    # 确保必要的目录存在
    dirs_to_create = ['uploads', 'logs', 'data_exports']
    for dir_name in dirs_to_create:
        dir_path = os.path.join(app_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"📁 创建目录: {dir_path}")
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DB_TYPE'] = 'sqlite'  # 默认使用SQLite

    # 设置SQLite数据库路径（相对于exe目录）
    db_path = os.path.join(app_dir, 'rebugtracker.db')
    os.environ['SQLITE_DB_PATH'] = db_path

    # 创建配置文件（如果不存在）
    create_config_file(app_dir)

    return app_dir

def create_config_file(app_dir):
    """创建或更新配置文件"""
    config_path = os.path.join(app_dir, 'app_config.ini')

    if not os.path.exists(config_path):
        config_content = """[DEFAULT]
# ReBugTracker EXE 配置文件

[database]
type = sqlite
sqlite_path = rebugtracker.db

[server]
host = 127.0.0.1
port = 5000
debug = false

[security]
secret_key = your-secret-key-change-this

[uploads]
max_file_size = 16777216
allowed_extensions = png,jpg,jpeg,gif
"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"📄 创建配置文件: {config_path}")
        except Exception as e:
            print(f"⚠️ 创建配置文件失败: {e}")

def init_database():
    """初始化数据库"""
    try:
        # 确保项目根目录在路径中
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from rebugtracker import init_db
        print("🗄️ 初始化数据库...")
        init_db()
        print("✅ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

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

def stop_cleanup_scheduler():
    """停止清理调度器"""
    try:
        from notification.cleanup_manager import cleanup_manager
        cleanup_manager.stop_cleanup_scheduler()
        print("🧹 通知清理调度器已停止")
    except:
        pass

def open_browser(url):
    """延迟打开浏览器"""
    import webbrowser
    time.sleep(2)  # 等待服务器启动
    try:
        webbrowser.open(url)
        print(f"🌐 已在浏览器中打开: {url}")
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        print(f"请手动访问: {url}")

def main():
    """主函数"""
    print("🚀 ReBugTracker 启动中...")
    print("=" * 50)

    # 设置exe环境
    app_dir = setup_exe_environment()
    print(f"📂 工作目录: {app_dir}")

    # 加载配置
    config = load_config()
    apply_config_to_env(config)
    print("⚙️ 配置加载完成")

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
    
    # 初始化数据库
    if not init_database():
        input("按回车键退出...")
        return
    
    # 启动清理调度器
    start_cleanup_scheduler()
    
    try:
        # 确保项目根目录在路径中
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        # 确保配置已加载
        import config_adapter  # 这会自动设置环境变量

        # 导入Flask应用
        from rebugtracker import app

        # 应用配置到Flask应用
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))
        
        # 在后台线程中打开浏览器
        url = f"http://{HOST}:{PORT}"
        browser_thread = threading.Thread(target=open_browser, args=(url,))
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"📡 应用程序启动在: {url}")
        print("💡 按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动Flask应用
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n👋 应用程序已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止清理调度器
        stop_cleanup_scheduler()
        
        print("\n🔄 正在清理资源...")
        time.sleep(1)
        print("✅ 清理完成")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 程序异常退出: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")
