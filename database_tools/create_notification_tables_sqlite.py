#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为SQLite数据库创建通知系统相关数据库表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 强制使用SQLite
os.environ['DB_TYPE'] = 'sqlite'

from db_factory import get_db_connection
from sql_adapter import adapt_sql

def create_notification_tables_sqlite():
    """为SQLite创建通知系统相关表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔧 开始为SQLite数据库创建通知系统表...")
        
        # 1. 检查并添加用户表的email和phone字段
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
        
        # 为现有用户设置默认邮箱
        cursor.execute("UPDATE users SET email = username || '@example.com' WHERE email IS NULL OR email = ''")
        updated_count = cursor.rowcount
        print(f"  ✅ 为 {updated_count} 个用户设置了默认邮箱")
        
        # 2. 创建系统配置表
        print("📋 创建系统配置表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT NOT NULL,
                description TEXT,
                updated_by INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ system_config表创建成功")
        
        # 插入默认配置
        cursor.execute("SELECT COUNT(*) FROM system_config WHERE config_key = 'notification_enabled'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO system_config (config_key, config_value, description) 
                VALUES ('notification_enabled', 'true', '服务器通知功能开关')
            """)
            print("  ✅ 插入默认通知配置")
        
        # 3. 创建用户通知偏好表
        print("📋 创建用户通知偏好表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_notification_preferences (
                user_id INTEGER PRIMARY KEY,
                email_enabled BOOLEAN DEFAULT 1,
                gotify_enabled BOOLEAN DEFAULT 1,
                inapp_enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  ✅ user_notification_preferences表创建成功")
        
        # 4. 创建应用内通知表
        print("📋 创建应用内通知表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                read_status BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL,
                related_bug_id INTEGER NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (related_bug_id) REFERENCES bugs(id)
            )
        """)
        print("  ✅ notifications表创建成功")
        
        # 5. 为现有用户创建默认通知偏好
        print("📋 为现有用户创建默认通知偏好...")
        cursor.execute("""
            INSERT OR IGNORE INTO user_notification_preferences (user_id, email_enabled, gotify_enabled, inapp_enabled)
            SELECT id, 1, 1, 1 FROM users 
        """)
        
        affected_rows = cursor.rowcount
        print(f"  ✅ 为 {affected_rows} 个用户创建了默认通知偏好")
        
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
        
        print("✅ SQLite通知系统数据库表创建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建SQLite通知系统表失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def check_sqlite_tables():
    """检查SQLite表是否创建成功"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tables = ['system_config', 'user_notification_preferences', 'notifications']
        
        print("\n🔍 检查SQLite表创建状态:")
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            status = "✅ 存在" if exists else "❌ 不存在"
            print(f"  {table}: {status}")
            
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"    记录数: {count}")
        
        # 检查用户表字段
        print("\n🔍 检查用户表字段:")
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        for field in ['email', 'phone']:
            status = "✅ 存在" if field in columns else "❌ 不存在"
            print(f"  {field}: {status}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查SQLite表状态失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker SQLite通知系统数据库初始化")
    print("=" * 50)
    
    success = create_notification_tables_sqlite()
    
    if success:
        check_sqlite_tables()
        print("\n🎉 SQLite通知系统数据库初始化完成！")
    else:
        print("\n💥 SQLite通知系统数据库初始化失败！")
        sys.exit(1)
