#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL数据库详细表结构检查工具
提供比基础检查工具更详细的PostgreSQL表结构信息，包括外键约束、索引等
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import psycopg2
from psycopg2.extras import DictCursor
from config import POSTGRES_CONFIG

def get_postgres_detailed_structure():
    """获取PostgreSQL数据库的详细表结构"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        print("🔍 PostgreSQL数据库详细表结构分析")
        print("=" * 80)
        
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
        
        print(f"📋 发现 {len(tables)} 个表: {tables}")
        print()
        
        for table in tables:
            print(f"=== {table} 表详细结构 ===")
            
            # 获取表的详细列信息
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            
            columns = cursor.fetchall()
            
            print("📋 字段信息:")
            for col in columns:
                name, data_type, nullable, default, max_length, position = col
                null_str = "NULL" if nullable == 'YES' else "NOT NULL"
                default_str = f"DEFAULT {default}" if default else ""
                length_str = f"({max_length})" if max_length else ""
                
                print(f"  {position:>2}. {name:<25} {data_type}{length_str:<20} {null_str:<8} {default_str}")
            
            # 获取外键约束
            cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule,
                    rc.update_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s
            """, (table,))
            
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print("\n🔗 外键约束:")
                for fk in foreign_keys:
                    col_name, ref_table, ref_col, delete_rule, update_rule = fk
                    print(f"  {col_name} -> {ref_table}({ref_col})")
                    print(f"    ON DELETE {delete_rule}, ON UPDATE {update_rule}")
            
            # 获取索引信息
            cursor.execute("""
                SELECT
                    i.relname AS index_name,
                    a.attname AS column_name,
                    ix.indisunique AS is_unique,
                    ix.indisprimary AS is_primary
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                WHERE t.relname = %s
                ORDER BY i.relname, a.attnum
            """, (table,))
            
            indexes = cursor.fetchall()
            if indexes:
                print("\n📊 索引信息:")
                current_index = None
                for idx in indexes:
                    index_name, column_name, is_unique, is_primary = idx
                    if index_name != current_index:
                        current_index = index_name
                        unique_str = "UNIQUE" if is_unique else ""
                        primary_str = "PRIMARY KEY" if is_primary else ""
                        type_str = f"({primary_str} {unique_str})".strip("() ")
                        print(f"  {index_name} {type_str}")
                    print(f"    - {column_name}")
            
            # 获取记录数
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            print(f"\n📊 记录数: {count}")
            print("-" * 60)
            print()
        
        conn.close()
        return True

    except Exception as e:
        print(f"❌ 获取PostgreSQL详细结构失败: {e}")
        import traceback
        traceback.print_exc()
        try:
            if 'conn' in locals():
                conn.close()
        except:
            pass
        return False

def main():
    """主函数"""
    try:
        success = get_postgres_detailed_structure()
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
