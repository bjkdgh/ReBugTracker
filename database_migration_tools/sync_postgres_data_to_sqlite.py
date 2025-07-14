#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步PostgreSQL数据到SQLite
将PostgreSQL数据库中的数据同步到SQLite数据库
要求SQLite表结构已与PostgreSQL保持一致
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

def clear_sqlite_tables(sqlite_conn):
    """清空SQLite表数据"""
    cursor = sqlite_conn.cursor()
    
    print("🗑️ 清空SQLite表数据...")
    
    # 按依赖关系顺序清空表
    tables = [
        'notifications',
        'user_notification_preferences', 
        'system_config',
        'bugs',
        'users'
    ]
    
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"  🗑️ 清空 {table}")
    
    sqlite_conn.commit()
    print("✅ 表数据清空完成")

def migrate_users_table(pg_cursor, sqlite_conn):
    """迁移users表"""
    print("👥 迁移users表...")
    
    pg_cursor.execute("SELECT * FROM users ORDER BY id")
    users = pg_cursor.fetchall()
    
    sqlite_cursor = sqlite_conn.cursor()
    
    for user in users:
        # PostgreSQL字段顺序: id, username, password, role, team, role_en, team_en, chinese_name, email, phone, gotify_app_token, gotify_user_id
        # SQLite插入时跳过id（自增）
        values = [
            user[1],   # username
            user[2],   # password
            user[3],   # role
            user[4],   # team
            user[5],   # role_en
            user[6],   # team_en
            user[7],   # chinese_name
            user[8],   # email
            user[9],   # phone
            user[10],  # gotify_app_token
            user[11]   # gotify_user_id
        ]
        
        sqlite_cursor.execute('''
            INSERT INTO users 
            (username, password, role, team, role_en, team_en, chinese_name, 
             email, phone, gotify_app_token, gotify_user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)
    
    sqlite_conn.commit()
    print(f"  ✅ 迁移了 {len(users)} 个用户")

def migrate_bugs_table(pg_cursor, sqlite_conn):
    """迁移bugs表"""
    print("🐛 迁移bugs表...")
    
    pg_cursor.execute("SELECT * FROM bugs ORDER BY id")
    bugs = pg_cursor.fetchall()
    
    sqlite_cursor = sqlite_conn.cursor()
    
    for bug in bugs:
        # PostgreSQL字段: id, title, description, status, assigned_to, created_by, project, created_at, resolved_at, resolution, image_path
        # SQLite插入时跳过id（自增）
        values = [
            bug[1],   # title
            bug[2],   # description
            bug[3],   # status
            bug[4],   # assigned_to
            bug[5],   # created_by
            bug[6],   # project
            bug[7],   # created_at
            bug[8],   # resolved_at
            bug[9],   # resolution
            bug[10]   # image_path
        ]
        
        sqlite_cursor.execute('''
            INSERT INTO bugs 
            (title, description, status, assigned_to, created_by, project,
             created_at, resolved_at, resolution, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)
    
    sqlite_conn.commit()
    print(f"  ✅ 迁移了 {len(bugs)} 个问题")

def migrate_system_config_table(pg_cursor, sqlite_conn):
    """迁移system_config表"""
    print("⚙️ 迁移system_config表...")
    
    try:
        # PostgreSQL的system_config表字段: config_key, config_value, description, updated_by, updated_at
        pg_cursor.execute("SELECT config_key, config_value, description, updated_by, updated_at FROM system_config ORDER BY config_key")
        configs = pg_cursor.fetchall()
        
        sqlite_cursor = sqlite_conn.cursor()
        
        for config in configs:
            values = [
                config[0],  # config_key
                config[1],  # config_value
                config[2],  # description
                config[3],  # updated_by
                config[4]   # updated_at
            ]
            
            sqlite_cursor.execute('''
                INSERT INTO system_config 
                (config_key, config_value, description, updated_by, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', values)
        
        sqlite_conn.commit()
        print(f"  ✅ 迁移了 {len(configs)} 个配置项")
        
    except Exception as e:
        print(f"  ⚠️ system_config表迁移失败: {e}")
        import traceback
        traceback.print_exc()

def migrate_user_notification_preferences_table(pg_cursor, sqlite_conn):
    """迁移user_notification_preferences表"""
    print("🔔 迁移user_notification_preferences表...")
    
    try:
        pg_cursor.execute("SELECT user_id, email_enabled, gotify_enabled, inapp_enabled, created_at, updated_at FROM user_notification_preferences ORDER BY user_id")
        preferences = pg_cursor.fetchall()
        
        sqlite_cursor = sqlite_conn.cursor()
        
        for pref in preferences:
            values = [
                pref[0],  # user_id
                pref[1],  # email_enabled
                pref[2],  # gotify_enabled
                pref[3],  # inapp_enabled
                pref[4],  # created_at
                pref[5]   # updated_at
            ]
            
            sqlite_cursor.execute('''
                INSERT INTO user_notification_preferences 
                (user_id, email_enabled, gotify_enabled, inapp_enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', values)
        
        sqlite_conn.commit()
        print(f"  ✅ 迁移了 {len(preferences)} 个用户偏好")
        
    except Exception as e:
        print(f"  ⚠️ user_notification_preferences表迁移失败: {e}")
        import traceback
        traceback.print_exc()

def migrate_notifications_table(pg_cursor, sqlite_conn):
    """迁移notifications表"""
    print("📬 迁移notifications表...")
    
    try:
        pg_cursor.execute("SELECT id, user_id, title, content, read_status, created_at, read_at, related_bug_id FROM notifications ORDER BY id")
        notifications = pg_cursor.fetchall()
        
        sqlite_cursor = sqlite_conn.cursor()
        
        for notif in notifications:
            # PostgreSQL字段: id, user_id, title, content, read_status, created_at, read_at, related_bug_id
            # SQLite插入时跳过id（自增）
            values = [
                notif[1],  # user_id
                notif[2],  # title
                notif[3],  # content
                notif[4],  # read_status
                notif[5],  # created_at
                notif[6],  # read_at
                notif[7]   # related_bug_id
            ]
            
            sqlite_cursor.execute('''
                INSERT INTO notifications 
                (user_id, title, content, read_status, created_at, read_at, related_bug_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', values)
        
        sqlite_conn.commit()
        print(f"  ✅ 迁移了 {len(notifications)} 个通知")
        
    except Exception as e:
        print(f"  ⚠️ notifications表迁移失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主迁移函数"""
    print("🚀 开始同步PostgreSQL数据到SQLite")
    print("=" * 60)
    
    # 创建SQLite数据库连接
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
    print(f"📁 SQLite数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ SQLite数据库文件不存在，请先运行表结构同步脚本")
        return
    
    sqlite_conn = sqlite3.connect(db_path)
    
    # 创建PostgreSQL连接
    print(f"🔗 连接PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG.get('port', 5432)}")
    pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
    pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
    
    try:
        # 1. 清空现有数据
        clear_sqlite_tables(sqlite_conn)
        
        # 2. 迁移各个表的数据
        migrate_users_table(pg_cursor, sqlite_conn)
        migrate_bugs_table(pg_cursor, sqlite_conn)
        migrate_system_config_table(pg_cursor, sqlite_conn)
        migrate_user_notification_preferences_table(pg_cursor, sqlite_conn)
        migrate_notifications_table(pg_cursor, sqlite_conn)
        
        print("\n🎉 PostgreSQL数据同步到SQLite完成！")
        print("=" * 60)
        
        # 验证迁移结果
        print("📊 迁移结果验证:")
        cursor = sqlite_conn.cursor()
        
        tables = ['users', 'bugs', 'system_config', 'user_notification_preferences', 'notifications']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")
        
    except Exception as e:
        print(f"❌ 数据同步失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 关闭连接
        sqlite_conn.close()
        pg_conn.close()
        print("\n✅ 数据库连接已关闭")

if __name__ == "__main__":
    main()
