#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看数据库表结构工具
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection, DB_TYPE
from sql_adapter import adapt_sql

def show_table_structure():
    """显示数据库表结构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🗄️ ReBugTracker 数据库表结构 ({DB_TYPE.upper()})")
        print("=" * 60)
        
        if DB_TYPE == 'postgres':
            show_postgres_structure(cursor)
        else:
            show_sqlite_structure(cursor)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查看表结构失败: {e}")

def show_postgres_structure(cursor):
    """显示PostgreSQL表结构"""
    # 获取所有表名
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    
    print(f"📊 数据库中共有 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "=" * 60)
    
    # 查看每个表的结构
    for table in tables:
        table_name = table[0]
        print(f"\n📋 表: {table_name}")
        print("-" * 40)
        
        # 获取表结构
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        print("字段信息:")
        for col in columns:
            name, type_, nullable, default, max_length = col
            null_str = "可空" if nullable == "YES" else "非空"
            length_str = f"({max_length})" if max_length else ""
            default_str = f" 默认值: {default}" if default else ""
            print(f"  {name}: {type_}{length_str} ({null_str}){default_str}")
        
        # 获取主键信息
        cursor.execute("""
            SELECT column_name
            FROM information_schema.key_column_usage
            WHERE table_name = %s AND constraint_name LIKE '%_pkey'
        """, (table_name,))
        
        primary_keys = cursor.fetchall()
        if primary_keys:
            pk_columns = [pk[0] for pk in primary_keys]
            print(f"主键: {', '.join(pk_columns)}")
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"记录数: {count}")
        
        # 如果是小表，显示一些示例数据
        if count > 0 and count <= 10 and table_name in ['system_config', 'user_notification_preferences']:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print("示例数据:")
                for i, row in enumerate(rows, 1):
                    print(f"  记录{i}: {row}")

def show_sqlite_structure(cursor):
    """显示SQLite表结构"""
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"📊 数据库中共有 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "=" * 60)
    
    # 查看每个表的结构
    for table in tables:
        table_name = table[0]
        print(f"\n📋 表: {table_name}")
        print("-" * 40)
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("字段信息:")
        for col in columns:
            cid, name, type_, notnull, default, pk = col
            null_str = "非空" if notnull else "可空"
            pk_str = " (主键)" if pk else ""
            default_str = f" 默认值: {default}" if default else ""
            print(f"  {name}: {type_} ({null_str}){pk_str}{default_str}")
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"记录数: {count}")
        
        # 如果是小表，显示一些示例数据
        if count > 0 and count <= 10 and table_name in ['system_config', 'user_notification_preferences']:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print("示例数据:")
                for i, row in enumerate(rows, 1):
                    print(f"  记录{i}: {row}")

def show_notification_tables():
    """专门查看通知相关表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n🔔 通知系统相关表详情")
        print("=" * 40)
        
        notification_tables = ['system_config', 'user_notification_preferences', 'notifications']
        
        for table_name in notification_tables:
            try:
                print(f"\n📋 {table_name}")
                print("-" * 30)
                
                if DB_TYPE == 'postgres':
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = %s 
                        ORDER BY ordinal_position
                    """, (table_name,))
                else:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                
                columns = cursor.fetchall()
                
                if columns:
                    print("字段:")
                    for col in columns:
                        if DB_TYPE == 'postgres':
                            name, type_, nullable, default = col
                            null_str = "可空" if nullable == "YES" else "非空"
                            default_str = f" 默认: {default}" if default else ""
                            print(f"  {name}: {type_} ({null_str}){default_str}")
                        else:
                            cid, name, type_, notnull, default, pk = col
                            null_str = "非空" if notnull else "可空"
                            pk_str = " (主键)" if pk else ""
                            default_str = f" 默认: {default}" if default else ""
                            print(f"  {name}: {type_} ({null_str}){pk_str}{default_str}")
                    
                    # 获取记录数
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"记录数: {count}")
                    
                    # 显示所有数据（通知表通常数据不多）
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        print("所有数据:")
                        for i, row in enumerate(rows, 1):
                            print(f"  {i}: {row}")
                else:
                    print("  表不存在")
                    
            except Exception as e:
                print(f"  ❌ 查看表 {table_name} 失败: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查看通知表失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker 数据库表结构查看工具")
    print("=" * 50)
    
    show_table_structure()
    show_notification_tables()
    
    print("\n🎉 表结构查看完成！")
