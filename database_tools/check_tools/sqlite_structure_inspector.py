#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据库详细表结构检查工具
提供详细的SQLite表结构信息，包括外键约束、索引、触发器等
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sqlite3

def get_sqlite_detailed_structure():
    """获取SQLite数据库的详细表结构"""
    try:
        # 确定数据库路径
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 SQLite数据库详细表结构分析")
        print("=" * 80)
        print(f"📁 数据库路径: {db_path}")
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 发现 {len(tables)} 个表: {tables}")
        print()
        
        for table in tables:
            print(f"=== {table} 表详细结构 ===")
            
            # 获取表的列信息
            cursor.execute(f'PRAGMA table_info({table})')
            columns = cursor.fetchall()
            
            print("📋 字段信息:")
            for col in columns:
                cid, name, data_type, not_null, default_value, pk = col
                null_str = "NOT NULL" if not_null else "NULL"
                default_str = f"DEFAULT {default_value}" if default_value is not None else ""
                pk_str = "PRIMARY KEY" if pk else ""
                
                print(f"  {cid+1:>2}. {name:<25} {data_type:<15} {null_str:<8} {default_str} {pk_str}".strip())
            
            # 获取外键信息
            cursor.execute(f'PRAGMA foreign_key_list({table})')
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print("\n🔗 外键约束:")
                for fk in foreign_keys:
                    id, seq, ref_table, from_col, to_col, on_update, on_delete, match = fk
                    print(f"  {from_col} -> {ref_table}({to_col})")
                    print(f"    ON DELETE {on_delete}, ON UPDATE {on_update}")
            
            # 获取索引信息
            cursor.execute(f'PRAGMA index_list({table})')
            indexes = cursor.fetchall()
            if indexes:
                print("\n📊 索引信息:")
                for idx in indexes:
                    seq, name, unique, origin, partial = idx
                    unique_str = "UNIQUE" if unique else ""
                    origin_str = f"({origin})" if origin != 'c' else ""
                    print(f"  {name} {unique_str} {origin_str}")
                    
                    # 获取索引的列信息
                    cursor.execute(f'PRAGMA index_info({name})')
                    index_columns = cursor.fetchall()
                    for col_info in index_columns:
                        seqno, cid, col_name = col_info
                        print(f"    - {col_name}")
            
            # 获取表的创建语句
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
            create_sql = cursor.fetchone()
            if create_sql and create_sql[0]:
                print(f"\n📝 创建语句:")
                # 格式化SQL语句
                sql_lines = create_sql[0].split('\n')
                for line in sql_lines:
                    print(f"  {line.strip()}")
            
            # 获取记录数
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            print(f"\n📊 记录数: {count}")
            print("-" * 60)
            print()
        
        # 获取数据库统计信息
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchall()
        print("📊 数据库信息:")
        for db in db_info:
            seq, name, file = db
            print(f"  {name}: {file}")
        
        # 获取数据库大小
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        db_size = page_count * page_size
        print(f"  大小: {db_size:,} bytes ({db_size/1024/1024:.2f} MB)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 获取SQLite详细结构失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        success = get_sqlite_detailed_structure()
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
