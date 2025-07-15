#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整同步PostgreSQL到SQLite
一键完成表结构和数据的完整同步
"""

import sys
import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import POSTGRES_CONFIG

def backup_sqlite_db(db_path):
    """备份SQLite数据库"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📦 已备份SQLite数据库到: {backup_path}")
        return backup_path
    return None

def recreate_sqlite_tables(conn):
    """重新创建SQLite表结构"""
    cursor = conn.cursor()
    
    print("🔄 同步PostgreSQL表结构到SQLite...")
    
    # 删除现有表（按依赖关系顺序）
    tables_to_drop = ['notifications', 'user_notification_preferences', 'system_config', 'bug_images', 'bugs', 'users']
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        except Exception as e:
            print(f"  ⚠️ 删除表 {table} 失败: {e}")
    
    # 创建users表
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            team TEXT,
            role_en TEXT,
            team_en TEXT,
            chinese_name TEXT,
            email TEXT,
            phone TEXT,
            gotify_app_token TEXT,
            gotify_user_id TEXT
        )
    ''')
    
    # 创建bugs表
    cursor.execute('''
        CREATE TABLE bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT '待处理',
            assigned_to INTEGER,
            created_by INTEGER,
            project TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            resolution TEXT,
            image_path TEXT
        )
    ''')

    # 创建bug_images表
    cursor.execute('''
        CREATE TABLE bug_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bug_id) REFERENCES bugs(id)
        )
    ''')

    # 创建system_config表
    cursor.execute('''
        CREATE TABLE system_config (
            config_key TEXT PRIMARY KEY,
            config_value TEXT NOT NULL,
            description TEXT,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建user_notification_preferences表
    cursor.execute('''
        CREATE TABLE user_notification_preferences (
            user_id INTEGER PRIMARY KEY,
            email_enabled BOOLEAN DEFAULT 1,
            gotify_enabled BOOLEAN DEFAULT 1,
            inapp_enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建notifications表
    cursor.execute('''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            read_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            related_bug_id INTEGER
        )
    ''')
    
    conn.commit()
    print("✅ 表结构同步完成")

def sync_table_data(pg_cursor, sqlite_conn, table_name, pg_query, sqlite_insert, field_mapping):
    """通用表数据同步函数"""
    print(f"📋 同步{table_name}表数据...")
    
    try:
        pg_cursor.execute(pg_query)
        records = pg_cursor.fetchall()
        
        sqlite_cursor = sqlite_conn.cursor()
        
        for record in records:
            # 根据字段映射提取数据
            values = []
            for field_index in field_mapping:
                if field_index < len(record):
                    values.append(record[field_index])
                else:
                    values.append(None)
            
            sqlite_cursor.execute(sqlite_insert, values)
        
        sqlite_conn.commit()
        print(f"  ✅ 同步了 {len(records)} 条记录")
        return len(records)
        
    except Exception as e:
        print(f"  ❌ {table_name}表同步失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

def sync_all_data(pg_cursor, sqlite_conn):
    """同步所有表数据"""
    print("📊 开始同步所有表数据...")
    
    total_records = 0
    
    # 同步users表
    count = sync_table_data(
        pg_cursor, sqlite_conn, "users",
        "SELECT * FROM users ORDER BY id",
        '''INSERT INTO users 
           (username, password, role, team, role_en, team_en, chinese_name, 
            email, phone, gotify_app_token, gotify_user_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # 跳过id字段
    )
    total_records += count
    
    # 同步bugs表（保持原始ID）
    count = sync_table_data(
        pg_cursor, sqlite_conn, "bugs",
        "SELECT * FROM bugs ORDER BY id",
        '''INSERT INTO bugs
           (id, title, description, status, assigned_to, created_by, project,
            created_at, resolved_at, resolution, image_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 包含id字段
    )
    total_records += count

    # 同步bug_images表（保持原始ID）
    count = sync_table_data(
        pg_cursor, sqlite_conn, "bug_images",
        "SELECT * FROM bug_images ORDER BY id",
        '''INSERT INTO bug_images
           (id, bug_id, image_path, created_at)
           VALUES (?, ?, ?, ?)''',
        [0, 1, 2, 3]  # 包含id字段
    )
    total_records += count

    # 同步system_config表
    count = sync_table_data(
        pg_cursor, sqlite_conn, "system_config",
        "SELECT config_key, config_value, description, updated_by, updated_at FROM system_config ORDER BY config_key",
        '''INSERT INTO system_config 
           (config_key, config_value, description, updated_by, updated_at)
           VALUES (?, ?, ?, ?, ?)''',
        [0, 1, 2, 3, 4]
    )
    total_records += count
    
    # 同步user_notification_preferences表
    count = sync_table_data(
        pg_cursor, sqlite_conn, "user_notification_preferences",
        "SELECT user_id, email_enabled, gotify_enabled, inapp_enabled, created_at, updated_at FROM user_notification_preferences ORDER BY user_id",
        '''INSERT INTO user_notification_preferences 
           (user_id, email_enabled, gotify_enabled, inapp_enabled, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        [0, 1, 2, 3, 4, 5]
    )
    total_records += count
    
    # 同步notifications表
    count = sync_table_data(
        pg_cursor, sqlite_conn, "notifications",
        "SELECT id, user_id, title, content, read_status, created_at, read_at, related_bug_id FROM notifications ORDER BY id",
        '''INSERT INTO notifications 
           (user_id, title, content, read_status, created_at, read_at, related_bug_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        [1, 2, 3, 4, 5, 6, 7]  # 跳过id字段
    )
    total_records += count
    
    print(f"✅ 数据同步完成，共同步 {total_records} 条记录")
    return total_records

def verify_sync_result(sqlite_conn):
    """验证同步结果"""
    print("\n📊 验证同步结果:")
    cursor = sqlite_conn.cursor()
    
    tables = ['users', 'bugs', 'bug_images', 'system_config', 'user_notification_preferences', 'notifications']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} 条记录")

def main():
    """主函数"""
    print("🚀 开始完整同步PostgreSQL到SQLite")
    print("=" * 60)
    
    # SQLite数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
    print(f"📁 SQLite数据库路径: {db_path}")
    
    # 备份现有数据库
    backup_path = backup_sqlite_db(db_path)
    
    # 连接数据库
    print(f"🔗 连接PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG.get('port', 5432)}")
    
    try:
        # PostgreSQL连接
        pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
        pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        
        # SQLite连接
        sqlite_conn = sqlite3.connect(db_path)
        
        # 1. 同步表结构
        recreate_sqlite_tables(sqlite_conn)
        
        # 2. 同步数据
        total_records = sync_all_data(pg_cursor, sqlite_conn)
        
        # 3. 验证结果
        verify_sync_result(sqlite_conn)
        
        print(f"\n🎉 完整同步成功！")
        print(f"📊 共同步 {total_records} 条记录")
        if backup_path:
            print(f"📦 原数据库已备份到: {backup_path}")
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            sqlite_conn.close()
            pg_conn.close()
            print("\n✅ 数据库连接已关闭")
        except:
            pass

if __name__ == "__main__":
    main()
