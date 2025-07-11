# 数据库配置
import os

# 开发/测试环境配置（带默认值）
DB_CONFIG = {
    'dbname': os.getenv('DATABASE_NAME', 'postgres'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', '$RFV5tgb'),
    'host': os.getenv('DATABASE_HOST', '192.168.1.5'),
    'port': int(os.getenv('DATABASE_PORT', '5432'))
}

# 生产环境配置（需手动启用，不带默认值）
# DB_CONFIG = {
#     'dbname': os.getenv('DATABASE_NAME'),  # 必须设置
#     'user': os.getenv('DATABASE_USER'),    # 必须设置
#     'password': os.getenv('DATABASE_PASSWORD'),  # 必须设置
#     'host': os.getenv('DATABASE_HOST'),    # 必须设置
#     'port': int(os.getenv('DATABASE_PORT'))  # 生产环境建议显式设置
# }
