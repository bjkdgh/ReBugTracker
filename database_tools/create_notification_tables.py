#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建通知系统相关数据库表
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection
from sql_adapter import adapt_sql

def create_notification_tables():
    """创建通知系统相关表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔧 开始创建通知系统数据库表...")
        
        # 1. 系统配置表
        print("📋 创建系统配置表...")
        system_config_sql = """
        CREATE TABLE IF NOT EXISTS system_config (
            config_key VARCHAR(50) PRIMARY KEY,
            config_value TEXT NOT NULL,
            description TEXT,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        query, params = adapt_sql(system_config_sql, ())
        cursor.execute(query, params)
        
        # 插入默认配置
        default_config_sql = """
        INSERT INTO system_config (config_key, config_value, description) 
        VALUES (%s, %s, %s)
        """
        
        # 检查是否已存在
        cursor.execute("SELECT COUNT(*) FROM system_config WHERE config_key = %s", ('notification_enabled',))
        if cursor.fetchone()[0] == 0:
            query, params = adapt_sql(default_config_sql, ('notification_enabled', 'true', '服务器通知功能开关'))
            cursor.execute(query, params)
            print("  ✅ 插入默认通知配置")
        
        # 2. 用户通知偏好表
        print("📋 创建用户通知偏好表...")
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
        
        query, params = adapt_sql(user_prefs_sql, ())
        cursor.execute(query, params)
        
        # 3. 应用内通知表
        print("📋 创建应用内通知表...")
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
        
        query, params = adapt_sql(notifications_sql, ())
        cursor.execute(query, params)
        
        # 4. 为现有用户创建默认通知偏好
        print("📋 为现有用户创建默认通知偏好...")
        cursor.execute("""
            INSERT INTO user_notification_preferences (user_id, email_enabled, gotify_enabled, inapp_enabled)
            SELECT id, TRUE, TRUE, TRUE FROM users 
            WHERE id NOT IN (SELECT user_id FROM user_notification_preferences)
        """)
        
        affected_rows = cursor.rowcount
        if affected_rows > 0:
            print(f"  ✅ 为 {affected_rows} 个用户创建了默认通知偏好")
        
        # 5. 创建索引
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
        
        print("✅ 通知系统数据库表创建完成！")
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
        
        print("\n🔍 检查表创建状态:")
        for table in tables:
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = '{table}'
            """)
            
            exists = cursor.fetchone()[0] > 0
            status = "✅ 存在" if exists else "❌ 不存在"
            print(f"  {table}: {status}")
            
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"    记录数: {count}")
        
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
