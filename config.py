# 数据库配置
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 数据库类型配置
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # postgres/sqlite

# PostgreSQL配置
POSTGRES_CONFIG = {
    'dbname': os.getenv('DATABASE_NAME', 'postgres'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', '$RFV5tgb'),
    'host': os.getenv('DATABASE_HOST', '192.168.1.5'),
    'port': int(os.getenv('DATABASE_PORT', '5432'))
}

# SQLite配置
SQLITE_CONFIG = {
    'database': os.getenv('SQLITE_DB_PATH', 'rebugtracker.db')
}

# 统一数据库配置接口：根据DB_TYPE选择对应的数据库配置
DATABASE_CONFIG = {
    'postgres': POSTGRES_CONFIG,  # PostgreSQL配置
    'sqlite': SQLITE_CONFIG       # SQLite配置
}
# 开发环境配置
# DB_CONFIG = {
#     'dbname': os.getenv('DATABASE_NAME', 'postgres'),  # 默认值postgres
#     'user': os.getenv('DATABASE_USER', 'postgres'),    # 默认值postgres
#     'password': os.getenv('DATABASE_PASSWORD', '$RFV5tgb'),  # 默认密码
#     'host': os.getenv('DATABASE_HOST', '192.168.1.5'), # 默认主机
#     'port': int(os.getenv('DATABASE_PORT', '5432'))    # 默认端口
# }

#  生产环境配置（需手动启用，不带默认值）
# DB_CONFIG = {
#     'dbname': os.getenv('DATABASE_NAME'),  # 默认值postgres
#     'user': os.getenv('DATABASE_USER'),    # 默认值postgres
#     'password': os.getenv('DATABASE_PASSWORD'),  # 默认密码
#     'host': os.getenv('DATABASE_HOST'), # 默认主机
#     'port': int(os.getenv('DATABASE_PORT'))    # 默认端口
# }

# 文件上传配置 - 从config_adapter导入以支持exe环境
try:
    from config_adapter import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
except ImportError:
    # 如果config_adapter不可用，使用默认值
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'zip', 'rar', 'doc', 'docx', 'xls', 'xlsx', 'pdf', 'tar', 'gz'}
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024  # 1GB
