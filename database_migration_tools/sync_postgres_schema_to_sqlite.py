#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步PostgreSQL表结构到SQLite
将PostgreSQL数据库的表结构同步到SQLite数据库
"""

import sys
import os
import sqlite3

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def recreate_sqlite_tables(conn):
    """重新创建SQLite表，使其与PostgreSQL保持一致"""
    cursor = conn.cursor()
    
    print("🔄 同步PostgreSQL表结构到SQLite...")
    
    # 删除现有表（按依赖关系顺序）
    tables_to_drop = [
        'notifications',
        'user_notification_preferences', 
        'system_config',
        'bugs',
        'users'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  🗑️ 删除表: {table}")
        except Exception as e:
            print(f"  ⚠️ 删除表 {table} 失败: {e}")
    
    # 创建users表（与PostgreSQL一致）
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
    print("  ✅ 创建users表")
    
    # 创建bugs表（与PostgreSQL一致）
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
    print("  ✅ 创建bugs表")
    
    # 创建system_config表（与PostgreSQL一致，config_key为主键）
    cursor.execute('''
        CREATE TABLE system_config (
            config_key TEXT PRIMARY KEY,
            config_value TEXT NOT NULL,
            description TEXT,
            updated_by INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ 创建system_config表")
    
    # 创建user_notification_preferences表（与PostgreSQL一致，user_id为主键）
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
    print("  ✅ 创建user_notification_preferences表")
    
    # 创建notifications表（与PostgreSQL一致）
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
    print("  ✅ 创建notifications表")
    
    conn.commit()
    print("✅ PostgreSQL表结构同步到SQLite完成")

def show_sqlite_structure(conn):
    """显示SQLite表结构"""
    cursor = conn.cursor()
    
    print("\n📋 SQLite表结构（已同步PostgreSQL）:")
    print("=" * 60)
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📊 表: {table_name}")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, name, data_type, not_null, default_value, pk = col
            nullable = "非空" if not_null else "可空"
            default = f" 默认:{default_value}" if default_value else ""
            primary = " [主键]" if pk else ""
            print(f"  - {name}: {data_type} ({nullable}){default}{primary}")

def main():
    """主函数"""
    print("🔄 开始同步PostgreSQL表结构到SQLite")
    print("=" * 60)
    
    # 连接SQLite数据库
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
    print(f"📁 SQLite数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ SQLite数据库文件不存在")
        return
    
    # 备份提示
    print("⚠️ 注意：此操作将删除SQLite中的所有现有数据！")
    print("📋 建议先备份数据库文件")
    
    response = input("是否继续？(y/N): ")
    if response.lower() != 'y':
        print("❌ 操作已取消")
        return
    
    conn = sqlite3.connect(db_path)
    
    try:
        # 重新创建表结构
        recreate_sqlite_tables(conn)
        
        # 显示新的表结构
        show_sqlite_structure(conn)
        
        print("\n🎉 PostgreSQL表结构已成功同步到SQLite！")
        print("💡 现在可以运行数据迁移脚本来同步数据")
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()
        print("\n✅ 数据库连接已关闭")

if __name__ == "__main__":
    main()
