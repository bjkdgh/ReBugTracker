#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试工具
测试PostgreSQL和SQLite数据库连接是否正常
"""

import os
import sys
import sqlite3

# PostgreSQL配置
POSTGRES_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5',
    'port': 5432
}

try:
    import psycopg2
    from psycopg2.extras import DictCursor
except ImportError as e:
    print(f"导入错误: {e}")
    POSTGRES_CONFIG = None

def test_sqlite_connection():
    """测试SQLite数据库连接"""
    print("🔍 测试SQLite数据库连接...")
    
    try:
        # SQLite数据库路径
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表列表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"✅ SQLite连接成功！")
        print(f"📁 数据库路径: {db_path}")
        print(f"📊 找到 {len(tables)} 个表:")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ SQLite连接失败: {e}")
        return False

def test_postgres_connection():
    """测试PostgreSQL数据库连接"""
    print("\n🔍 测试PostgreSQL数据库连接...")
    
    if not POSTGRES_CONFIG:
        print("❌ PostgreSQL配置未找到")
        return False
    
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # 获取表列表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"✅ PostgreSQL连接成功！")
        print(f"🔗 服务器: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG.get('port', 5432)}")
        print(f"📊 找到 {len(tables)} 个表:")
        
        for table in tables:
            table_name = table['table_name']
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始数据库连接测试")
    print("=" * 50)
    
    # 测试SQLite
    sqlite_ok = test_sqlite_connection()
    
    # 测试PostgreSQL
    postgres_ok = test_postgres_connection()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   SQLite: {'✅ 正常' if sqlite_ok else '❌ 失败'}")
    print(f"   PostgreSQL: {'✅ 正常' if postgres_ok else '❌ 失败'}")
    
    if sqlite_ok and postgres_ok:
        print("\n🎉 所有数据库连接正常！")
        print("💡 双数据库切换系统已就绪")
    else:
        print("\n⚠️ 部分数据库连接异常，请检查配置")

if __name__ == "__main__":
    main()
