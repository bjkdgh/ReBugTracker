#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用通知系统数据库表创建工具
支持PostgreSQL和SQLite数据库
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection, DB_TYPE
from sql_adapter import adapt_sql

def check_and_add_user_fields(cursor):
    """检查并添加用户表的email和phone字段（仅SQLite需要）"""
    if DB_TYPE == 'sqlite':
        print("📧 检查用户表字段...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'email' not in columns:
            print("  添加email字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            print("  ✅ email字段添加成功")
        else:
            print("  ✅ email字段已存在")

        if 'phone' not in columns:
            print("  添加phone字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            print("  ✅ phone字段添加成功")
        else:
            print("  ✅ phone字段已存在")

        if 'gotify_app_token' not in columns:
            print("  添加gotify_app_token字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN gotify_app_token TEXT")
            print("  ✅ gotify_app_token字段添加成功")
        else:
            print("  ✅ gotify_app_token字段已存在")

        if 'gotify_user_id' not in columns:
            print("  添加gotify_user_id字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN gotify_user_id TEXT")
            print("  ✅ gotify_user_id字段添加成功")
        else:
            print("  ✅ gotify_user_id字段已存在")

        # 为现有用户设置默认邮箱
        cursor.execute("UPDATE users SET email = username || '@example.com' WHERE email IS NULL OR email = ''")
        updated_count = cursor.rowcount
        print(f"  ✅ 为 {updated_count} 个用户设置了默认邮箱")

def create_notification_tables():
    """创建通知系统相关表（通用版本，支持PostgreSQL和SQLite）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print(f"🔧 开始为{DB_TYPE.upper()}数据库创建通知系统表...")

        # 1. 检查并添加用户表字段（仅SQLite需要）
        check_and_add_user_fields(cursor)

        # 2. 系统配置表
        print("📋 创建系统配置表...")
        if DB_TYPE == 'postgres':
            system_config_sql = """
            CREATE TABLE IF NOT EXISTS system_config (
                config_key VARCHAR(50) PRIMARY KEY,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_by INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:  # SQLite
            system_config_sql = """
            CREATE TABLE IF NOT EXISTS system_config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_by INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

        query, params = adapt_sql(system_config_sql, ())
        cursor.execute(query, params)
        print("  ✅ system_config表创建成功")

        # 插入默认配置
        check_sql = "SELECT COUNT(*) FROM system_config WHERE config_key = ?"
        if DB_TYPE == 'postgres':
            check_sql = "SELECT COUNT(*) FROM system_config WHERE config_key = %s"

        cursor.execute(check_sql, ('notification_enabled',))
        if cursor.fetchone()[0] == 0:
            default_config_sql = """
            INSERT INTO system_config (config_key, config_value, description)
            VALUES (?, ?, ?)
            """
            if DB_TYPE == 'postgres':
                default_config_sql = """
                INSERT INTO system_config (config_key, config_value, description)
                VALUES (%s, %s, %s)
                """

            query, params = adapt_sql(default_config_sql, ('notification_enabled', 'true', '服务器通知功能开关'))
            cursor.execute(query, params)
            print("  ✅ 插入默认通知配置")

        # 3. 用户通知偏好表
        print("📋 创建用户通知偏好表...")
        if DB_TYPE == 'postgres':
            user_prefs_sql = """
            CREATE TABLE IF NOT EXISTS user_notification_preferences (
                user_id INTEGER PRIMARY KEY,
                email_enabled BOOLEAN DEFAULT TRUE,
                gotify_enabled BOOLEAN DEFAULT TRUE,
                inapp_enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        else:  # SQLite
            user_prefs_sql = """
            CREATE TABLE IF NOT EXISTS user_notification_preferences (
                user_id INTEGER PRIMARY KEY,
                email_enabled BOOLEAN DEFAULT 1,
                gotify_enabled BOOLEAN DEFAULT 1,
                inapp_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """

        query, params = adapt_sql(user_prefs_sql, ())
        cursor.execute(query, params)
        print("  ✅ user_notification_preferences表创建成功")

        # 4. 应用内通知表
        print("📋 创建应用内通知表...")
        if DB_TYPE == 'postgres':
            notifications_sql = """
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                read_status BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL,
                related_bug_id INTEGER NULL
            )
            """
        else:  # SQLite
            notifications_sql = """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                read_status BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                related_bug_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        
        query, params = adapt_sql(notifications_sql, ())
        cursor.execute(query, params)
        print("  ✅ notifications表创建成功")

        # 5. 为现有用户创建默认通知偏好
        print("📋 为现有用户创建默认通知偏好...")
        if DB_TYPE == 'postgres':
            insert_prefs_sql = """
                INSERT INTO user_notification_preferences (user_id, email_enabled, gotify_enabled, inapp_enabled)
                SELECT id, TRUE, TRUE, TRUE FROM users
                WHERE id NOT IN (SELECT user_id FROM user_notification_preferences)
            """
        else:  # SQLite
            insert_prefs_sql = """
                INSERT INTO user_notification_preferences (user_id, email_enabled, gotify_enabled, inapp_enabled)
                SELECT id, 1, 1, 1 FROM users
                WHERE id NOT IN (SELECT user_id FROM user_notification_preferences)
            """

        cursor.execute(insert_prefs_sql)
        affected_rows = cursor.rowcount
        if affected_rows > 0:
            print(f"  ✅ 为 {affected_rows} 个用户创建了默认通知偏好")
        else:
            print("  ✅ 所有用户已有通知偏好设置")

        # 6. 创建索引
        print("📋 创建索引...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read_status ON notifications(read_status)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_related_bug_id ON notifications(related_bug_id)"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        print("  ✅ 索引创建完成")

        conn.commit()
        conn.close()

        print(f"✅ {DB_TYPE.upper()}通知系统数据库表创建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建通知系统表失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def check_tables():
    """检查表是否创建成功"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        tables = ['system_config', 'user_notification_preferences', 'notifications']

        print(f"\n🔍 检查{DB_TYPE.upper()}表创建状态:")
        for table in tables:
            try:
                if DB_TYPE == 'postgres':
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM information_schema.tables
                        WHERE table_name = '{table}'
                    """)
                    exists = cursor.fetchone()[0] > 0
                else:  # SQLite
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM sqlite_master
                        WHERE type='table' AND name='{table}'
                    """)
                    exists = cursor.fetchone()[0] > 0

                status = "✅ 存在" if exists else "❌ 不存在"
                print(f"  {table}: {status}")

                if exists:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"    记录数: {count}")
            except Exception as e:
                print(f"  {table}: ❌ 检查失败 - {e}")

        conn.close()

    except Exception as e:
        print(f"❌ 检查表状态失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker 通知系统数据库初始化")
    print("=" * 50)
    
    success = create_notification_tables()
    
    if success:
        check_tables()
        print("\n🎉 通知系统数据库初始化完成！")
    else:
        print("\n💥 通知系统数据库初始化失败！")
        sys.exit(1)
