#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步SQLite数据到PostgreSQL
将SQLite数据库中的数据同步到PostgreSQL数据库
用于双数据库切换时的反向同步
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

def clear_postgres_tables(pg_cursor, pg_conn):
    """清空PostgreSQL表数据"""
    print("🗑️ 清空PostgreSQL表数据...")
    
    # 按依赖关系顺序清空表
    tables = [
        'notifications',
        'user_notification_preferences', 
        'bugs',
        'users'
    ]
    
    # system_config表不清空，保留配置
    
    for table in tables:
        try:
            pg_cursor.execute(f"DELETE FROM {table}")
            print(f"  🗑️ 清空 {table}")
        except Exception as e:
            print(f"  ⚠️ 清空表 {table} 失败: {e}")
    
    pg_conn.commit()
    print("✅ 表数据清空完成")

def sync_users_table(sqlite_cursor, pg_cursor, pg_conn):
    """同步users表"""
    print("👥 同步users表到PostgreSQL...")
    
    sqlite_cursor.execute("SELECT * FROM users ORDER BY id")
    users = sqlite_cursor.fetchall()
    
    for user in users:
        # SQLite字段: id, username, password, role, team, role_en, team_en, chinese_name, email, phone, gotify_app_token, gotify_user_id
        # PostgreSQL插入时指定id
        values = [
            user[0],   # id
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
        
        pg_cursor.execute('''
            INSERT INTO users 
            (id, username, password, role, team, role_en, team_en, chinese_name, 
             email, phone, gotify_app_token, gotify_user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', values)
    
    # 更新序列
    if users:
        max_id = max(user[0] for user in users)
        pg_cursor.execute(f"SELECT setval('users_id_seq', {max_id})")
    
    pg_conn.commit()
    print(f"  ✅ 同步了 {len(users)} 个用户")

def sync_bugs_table(sqlite_cursor, pg_cursor, pg_conn):
    """同步bugs表"""
    print("🐛 同步bugs表到PostgreSQL...")
    
    sqlite_cursor.execute("SELECT * FROM bugs ORDER BY id")
    bugs = sqlite_cursor.fetchall()
    
    for bug in bugs:
        # SQLite字段: id, title, description, status, assigned_to, created_by, project, created_at, resolved_at, resolution, image_path
        values = [
            bug[0],   # id
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
        
        pg_cursor.execute('''
            INSERT INTO bugs 
            (id, title, description, status, assigned_to, created_by, project,
             created_at, resolved_at, resolution, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', values)
    
    # 更新序列
    if bugs:
        max_id = max(bug[0] for bug in bugs)
        pg_cursor.execute(f"SELECT setval('bugs_id_seq', {max_id})")
    
    pg_conn.commit()
    print(f"  ✅ 同步了 {len(bugs)} 个问题")

def sync_user_notification_preferences_table(sqlite_cursor, pg_cursor, pg_conn):
    """同步user_notification_preferences表"""
    print("🔔 同步user_notification_preferences表到PostgreSQL...")
    
    try:
        sqlite_cursor.execute("SELECT * FROM user_notification_preferences ORDER BY user_id")
        preferences = sqlite_cursor.fetchall()
        
        for pref in preferences:
            values = [
                pref[0],  # user_id
                pref[1],  # email_enabled
                pref[2],  # gotify_enabled
                pref[3],  # inapp_enabled
                pref[4],  # created_at
                pref[5]   # updated_at
            ]
            
            pg_cursor.execute('''
                INSERT INTO user_notification_preferences 
                (user_id, email_enabled, gotify_enabled, inapp_enabled, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', values)
        
        pg_conn.commit()
        print(f"  ✅ 同步了 {len(preferences)} 个用户偏好")
        
    except Exception as e:
        print(f"  ⚠️ user_notification_preferences表同步失败: {e}")

def sync_notifications_table(sqlite_cursor, pg_cursor, pg_conn):
    """同步notifications表"""
    print("📬 同步notifications表到PostgreSQL...")
    
    try:
        sqlite_cursor.execute("SELECT * FROM notifications ORDER BY id")
        notifications = sqlite_cursor.fetchall()
        
        for notif in notifications:
            # SQLite字段: id, user_id, title, content, read_status, created_at, read_at, related_bug_id
            values = [
                notif[0],  # id
                notif[1],  # user_id
                notif[2],  # title
                notif[3],  # content
                notif[4],  # read_status
                notif[5],  # created_at
                notif[6],  # read_at
                notif[7]   # related_bug_id
            ]
            
            pg_cursor.execute('''
                INSERT INTO notifications 
                (id, user_id, title, content, read_status, created_at, read_at, related_bug_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', values)
        
        # 更新序列
        if notifications:
            max_id = max(notif[0] for notif in notifications)
            pg_cursor.execute(f"SELECT setval('notifications_id_seq', {max_id})")
        
        pg_conn.commit()
        print(f"  ✅ 同步了 {len(notifications)} 个通知")
        
    except Exception as e:
        print(f"  ⚠️ notifications表同步失败: {e}")

def verify_postgres_data(pg_cursor):
    """验证PostgreSQL数据"""
    print("\n📊 验证PostgreSQL同步结果:")
    
    tables = ['users', 'bugs', 'user_notification_preferences', 'notifications']
    for table in tables:
        pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = pg_cursor.fetchone()[0]
        print(f"  {table}: {count} 条记录")

def main():
    """主函数"""
    print("🚀 开始同步SQLite数据到PostgreSQL")
    print("=" * 60)
    
    # SQLite数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
    print(f"📁 SQLite数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ SQLite数据库文件不存在")
        return
    
    # 连接数据库
    print(f"🔗 连接PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG.get('port', 5432)}")
    
    try:
        # SQLite连接
        sqlite_conn = sqlite3.connect(db_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # PostgreSQL连接
        pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
        pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        
        # 警告提示
        print("⚠️ 注意：此操作将清空PostgreSQL中的用户、问题和通知数据！")
        print("📋 system_config配置数据将保留")
        
        response = input("是否继续？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            return
        
        # 1. 清空PostgreSQL数据
        clear_postgres_tables(pg_cursor, pg_conn)
        
        # 2. 同步各个表的数据
        sync_users_table(sqlite_cursor, pg_cursor, pg_conn)
        sync_bugs_table(sqlite_cursor, pg_cursor, pg_conn)
        sync_user_notification_preferences_table(sqlite_cursor, pg_cursor, pg_conn)
        sync_notifications_table(sqlite_cursor, pg_cursor, pg_conn)
        
        # 3. 验证结果
        verify_postgres_data(pg_cursor)
        
        print("\n🎉 SQLite数据同步到PostgreSQL完成！")
        
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
