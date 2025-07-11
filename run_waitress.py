from waitress import serve
from rebugtracker import app, init_db
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logging.info("正在初始化数据库...")
    try:
        init_db()
        logging.info("数据库初始化完成。")
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
        # 根据实际情况决定是否退出
        # import sys
        # sys.exit(1)

    logging.info("Waitress 服务器启动中...")
    # 监听所有可用网络接口的5000端口
    serve(app, host='0.0.0.0', port=5000)
    logging.info("Waitress 服务器已停止。")
