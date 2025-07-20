#!/usr/bin/env python3
# Waitress生产环境部署工具
# 使用Waitress WSGI服务器运行ReBugTracker应用

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_production_server():
    """使用Waitress运行生产环境服务器"""
    try:
        print(" 启动ReBugTracker生产环境服务器...")

        # 加载环境变量
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # 如果没有python-dotenv，继续运行

        from waitress import serve
        from rebugtracker import app
        
        # 配置参数
        HOST = '0.0.0.0'  # 监听所有网络接口
        PORT = int(os.getenv('APP_PORT', 5000))  # 从环境变量读取端口，默认5000
        THREADS = int(os.getenv('WAITRESS_THREADS', 4))  # 线程数
        
        print(f" 服务器配置:")
        print(f"   主机: {HOST}")
        print(f"   端口: {PORT}")
        print(f"   线程数: {THREADS}")
        print(f"   访问地址: http://localhost:{PORT}")
        
        # 使用 Waitress 作为生产环境的 WSGI 服务器
        serve(
            app, 
            host=HOST, 
            port=PORT,
            threads=THREADS,
            cleanup_interval=30,
            channel_timeout=120
        )
        
    except ImportError as e:
        print(f" 导入失败: {e}")
        print("请安装waitress: pip install waitress")
        sys.exit(1)
    except Exception as e:
        print(f" 服务器启动失败: {e}")
        sys.exit(1)

def check_dependencies():
    """检查依赖包"""
    try:
        import waitress
        # 尝试多种方式获取版本信息
        try:
            # 方式1: 尝试 __version__ 属性
            version = waitress.__version__
        except AttributeError:
            try:
                # 方式2: 使用 importlib.metadata (Python 3.8+)
                from importlib.metadata import version as get_version
                version = get_version('waitress')
            except ImportError:
                try:
                    # 方式3: 使用 pkg_resources (旧版本兼容)
                    import pkg_resources
                    version = pkg_resources.get_distribution('waitress').version
                except:
                    # 方式4: 无法获取版本时的fallback
                    version = "未知版本"
        
        print(f" Waitress版本: {version}")
        return True
    except ImportError:
        print(" 缺少waitress包，请安装: pip install waitress")
        return False

if __name__ == '__main__':
    print(" ReBugTracker生产环境部署工具")
    print("=" * 40)
    
    # 检查依赖
    if check_dependencies():
        # 运行服务器
        run_production_server()
    else:
        print("请先安装必要的依赖包")
        sys.exit(1)

