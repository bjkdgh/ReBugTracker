#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表结构检查工具
对比PostgreSQL和SQLite的表结构差异
"""

import sys
import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

# PostgreSQL配置
POSTGRES_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres', 
    'password': '$RFV5tgb',
    'host': '192.168.1.5',
    'port': 5432
}

def get_postgres_table_info():
    """获取PostgreSQL表详细信息"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        tables_info = {}
        
        # 获取所有表名（排除备份表）
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE '%_bak'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # 获取表的列信息
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            
            columns = cursor.fetchall()
            tables_info[table] = {
                'columns': [(col[0], col[1], col[2], col[3]) for col in columns],
                'column_count': len(columns)
            }
        
        conn.close()
        return tables_info
    except Exception as e:
        print(f"❌ 获取PostgreSQL表信息失败: {e}")
        return {}

def get_sqlite_table_info():
    """获取SQLite表详细信息"""
    try:
        # 确定数据库路径
        db_path = '../rebugtracker.db'

        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return {}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tables_info = {}
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # 获取表的列信息
            cursor.execute(f'PRAGMA table_info({table})')
            columns = cursor.fetchall()
            
            tables_info[table] = {
                'columns': [(col[1], col[2], 'YES' if not col[3] else 'NO', col[4]) for col in columns],
                'column_count': len(columns)
            }
        
        conn.close()
        return tables_info
    except Exception as e:
        print(f"❌ 获取SQLite表信息失败: {e}")
        import traceback
        traceback.print_exc()
        return {}

def compare_table_structures():
    """对比表结构"""
    print("🔍 数据库表结构对比工具")
    print("=" * 80)
    
    # 获取两个数据库的表信息
    print("📊 获取PostgreSQL表信息...")
    pg_info = get_postgres_table_info()
    
    print("📊 获取SQLite表信息...")
    sqlite_info = get_sqlite_table_info()
    
    if not pg_info:
        print("❌ 无法获取PostgreSQL表信息")
        return False
    
    if not sqlite_info:
        print("❌ 无法获取SQLite表信息")
        return False
    
    # 对比表的存在性
    pg_tables = set(pg_info.keys())
    sqlite_tables = set(sqlite_info.keys())
    
    print(f"\n📋 表数量对比:")
    print(f"  PostgreSQL: {len(pg_tables)} 个表")
    print(f"  SQLite: {len(sqlite_tables)} 个表")
    
    missing_in_sqlite = pg_tables - sqlite_tables
    extra_in_sqlite = sqlite_tables - pg_tables
    common_tables = pg_tables & sqlite_tables
    
    if missing_in_sqlite:
        print(f"\n❌ SQLite缺少的表: {sorted(missing_in_sqlite)}")
    
    if extra_in_sqlite:
        print(f"\n⚠️ SQLite多余的表: {sorted(extra_in_sqlite)}")
    
    print(f"\n✅ 共同表: {len(common_tables)} 个")
    
    # 详细对比每个共同表
    issues_found = False
    
    for table in sorted(common_tables):
        print(f"\n📋 表: {table}")
        print("-" * 60)
        
        pg_cols = {col[0]: col for col in pg_info[table]['columns']}
        sqlite_cols = {col[0]: col for col in sqlite_info[table]['columns']}
        
        pg_col_names = set(pg_cols.keys())
        sqlite_col_names = set(sqlite_cols.keys())
        
        missing_cols = pg_col_names - sqlite_col_names
        extra_cols = sqlite_col_names - pg_col_names
        common_cols = pg_col_names & sqlite_col_names
        
        table_has_issues = False
        
        if missing_cols:
            print(f"  ❌ SQLite缺少字段: {sorted(missing_cols)}")
            table_has_issues = True
            issues_found = True
        
        if extra_cols:
            print(f"  ⚠️ SQLite多余字段: {sorted(extra_cols)}")
            table_has_issues = True
        
        # 检查共同字段的详细信息
        if common_cols:
            print(f"  📊 共同字段对比 ({len(common_cols)} 个):")
            for col in sorted(common_cols):
                pg_col = pg_cols[col]
                sqlite_col = sqlite_cols[col]
                
                # 简化的类型对比
                pg_type = pg_col[1].lower()
                sqlite_type = sqlite_col[1].lower()
                
                type_match = (
                    pg_type == sqlite_type or
                    (pg_type in ['integer', 'bigint'] and sqlite_type == 'integer') or
                    (pg_type in ['text', 'character varying'] and sqlite_type == 'text') or
                    (pg_type == 'boolean' and sqlite_type == 'boolean') or
                    (pg_type.startswith('timestamp') and sqlite_type == 'timestamp')
                )
                
                if type_match:
                    print(f"    ✅ {col}: {pg_type} ↔ {sqlite_type}")
                else:
                    print(f"    ❌ {col}: {pg_type} ≠ {sqlite_type}")
                    table_has_issues = True
                    issues_found = True
        
        if not table_has_issues:
            print(f"  ✅ 表结构完全一致")
    
    # 总结
    print(f"\n{'='*80}")
    if issues_found or missing_in_sqlite:
        print("❌ 发现表结构不一致问题")
        print("\n建议操作:")
        print("1. 运行 smart_sync_postgres_to_sqlite.py 重建SQLite表结构")
        print("2. 或使用 enhanced_smart_sync.py 进行智能同步")
        return False
    else:
        print("✅ 所有表结构完全一致，可以安全进行数据同步")
        return True

def main():
    """主函数"""
    try:
        success = compare_table_structures()
        return success
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        return False
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
