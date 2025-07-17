#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能同步PostgreSQL到SQLite
在同步过程中自动过滤孤儿记录，确保数据完整性
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

def backup_sqlite_db(db_path):
    """备份SQLite数据库"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"📦 已备份SQLite数据库到: {backup_path}")
        return backup_path
    return None

def check_table_structure_compatibility():
    """检查表结构兼容性"""
    print("🔍 检查表结构兼容性...")

    # 确定数据库路径
    db_path = '../rebugtracker.db'

    if not os.path.exists(db_path):
        print("📝 SQLite数据库不存在，将创建新数据库")
        return False

    try:
        # 简单检查关键字段是否存在
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查users表是否有role_en字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'role_en' not in columns:
            print("❌ SQLite表结构过时，缺少关键字段role_en")
            conn.close()
            return False

        print("✅ 表结构检查通过")
        conn.close()
        return True

    except Exception as e:
        print(f"❌ 表结构检查失败: {e}")
        return False

def clear_sqlite_data(conn):
    """清空SQLite数据，保持表结构"""
    cursor = conn.cursor()

    print("🗑️ 清空现有数据...")

    # 按依赖关系顺序删除数据
    tables_to_clear = [
        'notifications', 'user_notification_preferences', 'system_config',
        'bug_images', 'bugs', 'users'
    ]

    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"   ✅ 清空表: {table}")
        except Exception as e:
            print(f"   ⚠️ 清空表 {table} 失败: {e}")

    # 重置自增ID
    cursor.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    print("✅ 数据清空完成")

def recreate_sqlite_tables(conn):
    """重新创建SQLite表结构"""
    cursor = conn.cursor()

    print("🔄 重建SQLite表结构...")

    # 删除现有表
    tables_to_drop = [
        'notifications', 'user_notification_preferences', 'system_config',
        'bug_images', 'bugs', 'users'
    ]

    for table in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    
    # 创建users表 - 与PostgreSQL结构保持一致
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            chinese_name TEXT,
            role TEXT DEFAULT 'zncy',
            role_en TEXT DEFAULT 'zncy',
            team TEXT,
            team_en TEXT,
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
            image_path TEXT,
            FOREIGN KEY (assigned_to) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # 创建其他表...
    cursor.execute('''
        CREATE TABLE bug_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bug_id) REFERENCES bugs (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE system_config (
            config_key TEXT PRIMARY KEY,
            config_value TEXT,
            description TEXT,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE user_notification_preferences (
            user_id INTEGER PRIMARY KEY,
            email_enabled BOOLEAN DEFAULT 1,
            inapp_enabled BOOLEAN DEFAULT 1,
            gotify_enabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            read_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP,
            related_bug_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (related_bug_id) REFERENCES bugs (id)
        )
    ''')
    
    conn.commit()
    print("✅ 表结构重建完成")

def get_valid_user_ids(sqlite_conn):
    """获取SQLite中有效的用户ID列表"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id FROM users")
    return {row[0] for row in cursor.fetchall()}

def smart_sync_notifications(pg_cursor, sqlite_conn, valid_user_ids):
    """智能同步notifications表，过滤孤儿记录"""
    print("📋 智能同步notifications表...")
    
    # 获取PostgreSQL中的通知数据
    pg_cursor.execute("""
        SELECT user_id, title, content, read_status, created_at, read_at, related_bug_id 
        FROM notifications 
        ORDER BY id
    """)
    
    notifications = pg_cursor.fetchall()
    sqlite_cursor = sqlite_conn.cursor()
    
    synced_count = 0
    skipped_count = 0
    
    for notif in notifications:
        user_id = notif[0]
        
        # 检查用户ID是否有效
        if user_id in valid_user_ids:
            sqlite_cursor.execute('''
                INSERT INTO notifications 
                (user_id, title, content, read_status, created_at, read_at, related_bug_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', notif)
            synced_count += 1
        else:
            skipped_count += 1
            print(f"  ⚠️ 跳过孤儿通知: user_id={user_id}, title={notif[1][:30]}...")
    
    sqlite_conn.commit()
    print(f"  ✅ 同步了 {synced_count} 条通知")
    if skipped_count > 0:
        print(f"  🗑️ 跳过了 {skipped_count} 条孤儿通知")
    
    return synced_count

def sync_table_data(pg_cursor, sqlite_conn, table_name, select_query, insert_query, value_indices):
    """同步表数据的通用函数"""
    print(f"📋 同步{table_name}表数据...")
    
    pg_cursor.execute(select_query)
    rows = pg_cursor.fetchall()
    
    sqlite_cursor = sqlite_conn.cursor()
    
    for row in rows:
        values = [row[i] for i in value_indices]
        sqlite_cursor.execute(insert_query, values)
    
    sqlite_conn.commit()
    print(f"  ✅ 同步了 {len(rows)} 条记录")
    return len(rows)

def main():
    """主函数"""
    print("🚀 开始智能同步PostgreSQL到SQLite")
    print("=" * 60)
    
    # SQLite数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
    print(f"📁 SQLite数据库路径: {db_path}")
    
    # 备份现有数据库
    backup_path = backup_sqlite_db(db_path)
    
    try:
        # 连接PostgreSQL
        print(f"🔗 连接PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
        pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
        pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        
        # 连接SQLite
        sqlite_conn = sqlite3.connect(db_path)

        # 检查表结构兼容性
        structure_compatible = check_table_structure_compatibility()

        if not structure_compatible:
            print("🔄 表结构不兼容，需要重建...")
            # 重建表结构
            recreate_sqlite_tables(sqlite_conn)
        else:
            print("✅ 表结构兼容，清空现有数据...")
            # 清空现有数据，保持表结构
            clear_sqlite_data(sqlite_conn)

        print("📊 开始智能同步数据...")
        total_records = 0
        
        # 1. 同步users表 - 包含所有字段
        count = sync_table_data(
            pg_cursor, sqlite_conn, "users",
            "SELECT username, password, chinese_name, role, role_en, team, team_en, email, phone, gotify_app_token, gotify_user_id FROM users ORDER BY id",
            '''INSERT INTO users
               (username, password, chinese_name, role, role_en, team, team_en, email, phone, gotify_app_token, gotify_user_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        )
        total_records += count
        
        # 获取有效用户ID
        valid_user_ids = get_valid_user_ids(sqlite_conn)
        print(f"📋 有效用户ID数量: {len(valid_user_ids)}")
        
        # 2. 同步bugs表
        count = sync_table_data(
            pg_cursor, sqlite_conn, "bugs",
            "SELECT title, description, status, assigned_to, created_by, project, created_at, resolved_at, resolution, image_path FROM bugs ORDER BY id",
            '''INSERT INTO bugs 
               (title, description, status, assigned_to, created_by, project, created_at, resolved_at, resolution, image_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        )
        total_records += count
        
        # 3. 同步其他表
        count = sync_table_data(
            pg_cursor, sqlite_conn, "bug_images",
            "SELECT bug_id, image_path, created_at FROM bug_images ORDER BY id",
            '''INSERT INTO bug_images (bug_id, image_path, created_at) VALUES (?, ?, ?)''',
            [0, 1, 2]
        )
        total_records += count
        
        count = sync_table_data(
            pg_cursor, sqlite_conn, "system_config",
            "SELECT config_key, config_value, description, updated_at, updated_by FROM system_config",
            '''INSERT INTO system_config
               (config_key, config_value, description, updated_at, updated_by)
               VALUES (?, ?, ?, ?, ?)''',
            [0, 1, 2, 3, 4]
        )
        total_records += count
        
        count = sync_table_data(
            pg_cursor, sqlite_conn, "user_notification_preferences",
            "SELECT user_id, email_enabled, inapp_enabled, gotify_enabled, created_at, updated_at FROM user_notification_preferences",
            '''INSERT INTO user_notification_preferences
               (user_id, email_enabled, inapp_enabled, gotify_enabled, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            [0, 1, 2, 3, 4, 5]
        )
        total_records += count
        
        # 4. 智能同步notifications表（过滤孤儿记录）
        count = smart_sync_notifications(pg_cursor, sqlite_conn, valid_user_ids)
        total_records += count
        
        print(f"\n✅ 智能同步完成，共同步 {total_records} 条记录")
        
        # 验证结果
        print("\n📊 验证同步结果:")
        cursor = sqlite_conn.cursor()
        tables = ['users', 'bugs', 'bug_images', 'system_config', 'user_notification_preferences', 'notifications']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")
        
        print(f"\n🎉 智能同步成功！")
        print(f"📊 共同步 {total_records} 条记录")
        if backup_path:
            print(f"📦 原数据库已备份到: {backup_path}")
        print("🧹 已自动过滤孤儿记录，确保数据完整性")
        
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
