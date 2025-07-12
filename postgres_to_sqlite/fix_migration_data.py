#!/usr/bin/env python3
# 修复PostgreSQL到SQLite数据迁移中的关联关系问题

import sys
import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
import traceback

# PostgreSQL连接配置
PG_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb', 
    'host': '192.168.1.5'
}

def fix_migration_data():
    """修复数据迁移中的关联关系问题"""
    try:
        print("🔧 开始修复数据迁移中的关联关系问题...")
        
        # 连接SQLite数据库
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        sqlite_conn = sqlite3.connect(db_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # 连接PostgreSQL数据库
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
        
        print("📋 第一步：创建用户名到新ID的映射...")
        
        # 获取PostgreSQL中的用户数据（用户名 -> 原始ID）
        pg_cursor.execute("SELECT id, username FROM users ORDER BY id")
        pg_users = {row['username']: row['id'] for row in pg_cursor.fetchall()}
        
        # 获取SQLite中的用户数据（用户名 -> 新ID）
        sqlite_cursor.execute("SELECT id, username FROM users")
        sqlite_users = {row[1]: row[0] for row in sqlite_cursor.fetchall()}
        
        # 创建原始ID到新ID的映射
        id_mapping = {}
        for username in pg_users:
            if username in sqlite_users:
                old_id = pg_users[username]
                new_id = sqlite_users[username]
                id_mapping[old_id] = new_id
                print(f"   {username}: {old_id} -> {new_id}")
        
        print(f"📊 创建了 {len(id_mapping)} 个用户ID映射")
        
        print("\n🐛 第二步：修复bugs表的关联关系...")
        
        # 获取PostgreSQL中的bugs数据
        pg_cursor.execute("SELECT id, created_by, assigned_to, title FROM bugs ORDER BY id")
        pg_bugs = pg_cursor.fetchall()
        
        # 获取SQLite中的bugs数据
        sqlite_cursor.execute("SELECT id, created_by, assigned_to, title FROM bugs ORDER BY id")
        sqlite_bugs = sqlite_cursor.fetchall()
        
        # 修复每个bug的关联关系
        fixed_count = 0
        for i, sqlite_bug in enumerate(sqlite_bugs):
            if i < len(pg_bugs):
                pg_bug = pg_bugs[i]
                sqlite_bug_id = sqlite_bug[0]
                
                # 获取原始的created_by和assigned_to
                old_created_by = pg_bug['created_by']
                old_assigned_to = pg_bug['assigned_to']
                
                # 映射到新的ID
                new_created_by = id_mapping.get(old_created_by)
                new_assigned_to = id_mapping.get(old_assigned_to)
                
                # 更新SQLite中的数据
                sqlite_cursor.execute("""
                    UPDATE bugs 
                    SET created_by = ?, assigned_to = ? 
                    WHERE id = ?
                """, (new_created_by, new_assigned_to, sqlite_bug_id))
                
                print(f"   Bug {sqlite_bug_id}: created_by {old_created_by}->{new_created_by}, assigned_to {old_assigned_to}->{new_assigned_to}")
                fixed_count += 1
        
        print(f"✅ 修复了 {fixed_count} 个问题的关联关系")
        
        print("\n👥 第三步：修复用户的中文姓名...")
        
        # 获取PostgreSQL中的完整用户信息
        pg_cursor.execute("SELECT username, chinese_name, role, team, role_en, team_en FROM users")
        pg_user_details = {row['username']: dict(row) for row in pg_cursor.fetchall()}
        
        # 更新SQLite中的用户信息
        updated_users = 0
        for username, details in pg_user_details.items():
            if username in sqlite_users:
                sqlite_cursor.execute("""
                    UPDATE users 
                    SET chinese_name = ?, role = ?, team = ?, role_en = ?, team_en = ?
                    WHERE username = ?
                """, (
                    details['chinese_name'],
                    details['role'], 
                    details['team'],
                    details['role_en'],
                    details['team_en'],
                    username
                ))
                print(f"   更新用户 {username}: {details['chinese_name']}")
                updated_users += 1
        
        print(f"✅ 更新了 {updated_users} 个用户的详细信息")
        
        # 提交所有更改
        sqlite_conn.commit()
        
        print("\n🔍 第四步：验证修复结果...")
        
        # 检查孤立问题
        sqlite_cursor.execute("""
            SELECT COUNT(*) FROM bugs b 
            LEFT JOIN users u ON b.created_by = u.id 
            WHERE b.created_by IS NOT NULL AND u.id IS NULL
        """)
        orphan_bugs_creator = sqlite_cursor.fetchone()[0]
        
        sqlite_cursor.execute("""
            SELECT COUNT(*) FROM bugs b 
            LEFT JOIN users u ON b.assigned_to = u.id 
            WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
        """)
        orphan_bugs_assignee = sqlite_cursor.fetchone()[0]
        
        print(f"   孤立问题(创建者不存在): {orphan_bugs_creator}")
        print(f"   孤立问题(分配者不存在): {orphan_bugs_assignee}")
        
        # 检查特定用户
        test_users = ['wbx', 'zrq', 'lrz', 'fcl', 'wxw']
        print("\n🎯 检查关键用户:")
        for username in test_users:
            sqlite_cursor.execute("SELECT id, chinese_name, role, team FROM users WHERE username = ?", (username,))
            user = sqlite_cursor.fetchone()
            if user:
                user_id = user[0]
                # 检查分配给该用户的问题
                sqlite_cursor.execute("SELECT COUNT(*) FROM bugs WHERE assigned_to = ?", (user_id,))
                assigned_count = sqlite_cursor.fetchone()[0]
                print(f"   ✅ {username} (ID:{user_id}): {user[1]}, 分配的问题: {assigned_count}")
        
        # 关闭连接
        sqlite_conn.close()
        pg_conn.close()
        
        print(f"\n🎉 数据修复完成!")
        print(f"   - 修复了 {fixed_count} 个问题的关联关系")
        print(f"   - 更新了 {updated_users} 个用户的详细信息")
        print(f"   - 孤立问题数量: {orphan_bugs_creator + orphan_bugs_assignee}")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    fix_migration_data()
