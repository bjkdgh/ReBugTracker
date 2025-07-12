# sql_adapter.py: SQL语句适配器模块，处理不同数据库的SQL语法差异
# 主要功能包括占位符转换、函数适配、类型转换等

from config import DB_TYPE
import re

def adapt_sql(query, params):
    """SQL语句适配器
    
    功能：
    - 占位符转换（%s -> ?）
    - 时间函数适配
    - 字符串函数适配
    - 类型转换处理
    - 布尔值处理
    
    Args:
        query (str): 原始SQL查询语句
        params (list): 查询参数列表
        
    Returns:
        tuple: (适配后的SQL语句, 适配后的参数列表)
    """
    if DB_TYPE == 'sqlite':
        # 转换占位符：将Python风格的%s占位符转换为SQLite使用的?
        query = query.replace('%s', '?')
        
        # 时间函数适配：将PostgreSQL的date_trunc函数转换为SQLite的strftime函数
        query = re.sub(r'date_trunc\([\'\"]day[\'\"]', 'strftime("%Y-%m-%d"', query)
        # 将NOW()函数转换为SQLite的CURRENT_TIMESTAMP
        query = query.replace('NOW()', 'CURRENT_TIMESTAMP')
        # 将CURRENT_DATE转换为SQLite的date('now')函数
        query = query.replace('CURRENT_DATE', "date('now')")
        
        # 字符串函数适配：保持LOWER函数不变
        query = query.replace('LOWER', 'LOWER')
        # 将ILIKE操作符转换为LIKE（SQLite默认不区分大小写）
        query = query.replace('ILIKE', 'LIKE')  # SQLite默认不区分大小写
        
        # 类型转换处理：移除文本类型转换
        query = query.replace('::text', '')
        # 移除整数类型转换
        query = query.replace('::integer', '')
        
        # 布尔值处理：将布尔值转换为整数(0/1)
        if params:
            params = [p if not isinstance(p, bool) else int(p) for p in params]
            
    return query, params
