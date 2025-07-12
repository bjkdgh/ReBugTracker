#!/usr/bin/env python3
# SQLite数据库数据检查工具
# 用于快速查看SQLite数据库中的数据内容

import sqlite3
import os
import traceback

def check_sqlite_data():
    """检查SQLite数据库中的数据"""
    try:
        # 连接到项目根目录下的SQLite数据库
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        print(f"🔍 检查SQLite数据库: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 数据库中的表: {tables}")
        
        # 检查users表
        if 'users' in tables:
            print("\n👥 === Users表数据 ===")
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"总用户数: {user_count}")
            
            print("\n前5条用户记录:")
            cursor.execute("SELECT id, username, chinese_name, role, team FROM users LIMIT 5")
            for row in cursor.fetchall():
                print(f"  ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
        
        # 检查bugs表
        if 'bugs' in tables:
            print("\n🐛 === Bugs表数据 ===")
            cursor.execute("SELECT COUNT(*) FROM bugs")
            bug_count = cursor.fetchone()[0]
            print(f"总问题数: {bug_count}")
            
            print("\n前5条问题记录:")
            cursor.execute("SELECT id, title, status, created_by, assigned_to FROM bugs LIMIT 5")
            for row in cursor.fetchall():
                print(f"  ID:{row[0]} | {row[1][:30]}... | {row[2]} | 创建者:{row[3]} | 分配给:{row[4]}")
        
        # 检查关联关系
        if 'users' in tables and 'bugs' in tables:
            print("\n🔗 === 关联关系检查 ===")
            cursor.execute("""
                SELECT COUNT(*) FROM bugs b 
                LEFT JOIN users u ON b.created_by = u.id 
                WHERE b.created_by IS NOT NULL AND u.id IS NULL
            """)
            orphan_creator = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM bugs b 
                LEFT JOIN users u ON b.assigned_to = u.id 
                WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
            """)
            orphan_assignee = cursor.fetchone()[0]
            
            print(f"孤立问题(创建者不存在): {orphan_creator}")
            print(f"孤立问题(分配者不存在): {orphan_assignee}")
        
        conn.close()
        print("\n✅ 数据检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    check_sqlite_data()
