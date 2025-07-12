#!/usr/bin/env python3
# 验证PostgreSQL到SQLite数据迁移结果

import os
import sqlite3
import traceback

def verify_migration():
    """验证数据迁移和修复结果"""
    try:
        print("🔍 验证PostgreSQL到SQLite数据迁移结果...")
        
        # 连接SQLite数据库
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        print(f"✅ 找到SQLite数据库文件: {db_path}")
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 检查表是否存在
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in c.fetchall()]
        print(f"📋 数据库中的表: {tables}")
        
        if 'users' not in tables:
            print("❌ users表不存在")
            return False
        
        if 'bugs' not in tables:
            print("❌ bugs表不存在")
            return False
        
        # 检查用户数据
        print("\n👥 用户数据验证:")
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        print(f"   总用户数: {user_count}")
        
        # 检查关键用户的中文姓名
        test_users = ['wbx', 'zrq', 'lrz', 'fcl', 'wxw', 'testuser']
        for username in test_users:
            c.execute("SELECT id, chinese_name, role, team FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            if user:
                print(f"   ✅ {username}: ID={user[0]}, 姓名={user[1]}, 角色={user[2]}, 团队={user[3]}")
            else:
                print(f"   ❌ {username}: 用户不存在")
        
        # 检查问题数据
        print("\n🐛 问题数据验证:")
        c.execute("SELECT COUNT(*) FROM bugs")
        bug_count = c.fetchone()[0]
        print(f"   总问题数: {bug_count}")
        
        if bug_count > 0:
            # 检查关联关系
            c.execute("""
                SELECT b.id, b.title, u1.username as creator, u2.username as assignee
                FROM bugs b
                LEFT JOIN users u1 ON b.created_by = u1.id
                LEFT JOIN users u2 ON b.assigned_to = u2.id
                LIMIT 5
            """)
            bugs = c.fetchall()
            print("   前5个问题的关联关系:")
            for bug in bugs:
                print(f"     ID:{bug[0]} | {bug[1][:20]}... | 创建者:{bug[2]} | 分配给:{bug[3]}")
        
        # 检查数据完整性
        print("\n🔗 数据完整性验证:")
        
        # 检查孤立问题
        c.execute("""
            SELECT COUNT(*) FROM bugs b 
            LEFT JOIN users u ON b.created_by = u.id 
            WHERE b.created_by IS NOT NULL AND u.id IS NULL
        """)
        orphan_creator = c.fetchone()[0]
        
        c.execute("""
            SELECT COUNT(*) FROM bugs b 
            LEFT JOIN users u ON b.assigned_to = u.id 
            WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
        """)
        orphan_assignee = c.fetchone()[0]
        
        print(f"   孤立问题(创建者不存在): {orphan_creator}")
        print(f"   孤立问题(分配者不存在): {orphan_assignee}")
        
        # 统计每个用户的问题数
        print("\n📊 用户问题统计:")
        c.execute("""
            SELECT u.username, u.chinese_name,
                   COUNT(CASE WHEN b1.created_by = u.id THEN 1 END) as created_count,
                   COUNT(CASE WHEN b2.assigned_to = u.id THEN 1 END) as assigned_count
            FROM users u
            LEFT JOIN bugs b1 ON u.id = b1.created_by
            LEFT JOIN bugs b2 ON u.id = b2.assigned_to
            WHERE u.username IN ('wbx', 'zrq', 'lrz', 'fcl', 'wxw', 'gh', 'zjn', 'admin')
            GROUP BY u.id, u.username, u.chinese_name
            ORDER BY assigned_count DESC
        """)
        user_stats = c.fetchall()
        for stat in user_stats:
            print(f"   {stat[0]} ({stat[1]}): 创建了{stat[2]}个问题, 分配了{stat[3]}个问题")
        
        conn.close()
        
        # 总结
        print(f"\n✅ 验证完成!")
        print(f"   - 用户总数: {user_count}")
        print(f"   - 问题总数: {bug_count}")
        
        if orphan_creator == 0 and orphan_assignee == 0:
            print("🎉 所有关联关系都正确!")
            print("✅ 数据迁移和修复完全成功!")
        else:
            print("⚠️ 仍有部分关联关系问题")
            print(f"   需要修复的孤立问题: {orphan_creator + orphan_assignee}")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verify_migration()
