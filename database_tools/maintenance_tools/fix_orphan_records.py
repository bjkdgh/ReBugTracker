#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据库孤立记录修复工具
修复bugs表中的孤立用户引用
"""

import os
import sys
import sqlite3
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_orphan_records(sqlite_conn):
    """分析孤立记录"""
    print("🔍 分析孤立记录...")
    
    cursor = sqlite_conn.cursor()
    
    # 分析孤立的创建者
    cursor.execute("""
        SELECT b.id, b.title, b.created_by, b.created_at
        FROM bugs b 
        LEFT JOIN users u ON b.created_by = u.id 
        WHERE b.created_by IS NOT NULL AND u.id IS NULL
        ORDER BY b.id
    """)
    orphan_creators = cursor.fetchall()
    
    # 分析孤立的分配者
    cursor.execute("""
        SELECT b.id, b.title, b.assigned_to, b.created_at
        FROM bugs b 
        LEFT JOIN users u ON b.assigned_to = u.id 
        WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
        ORDER BY b.id
    """)
    orphan_assignees = cursor.fetchall()
    
    print(f"📊 孤立记录统计:")
    print(f"  创建者孤立记录: {len(orphan_creators)} 个")
    print(f"  分配者孤立记录: {len(orphan_assignees)} 个")
    
    if orphan_creators:
        print(f"\n📋 孤立创建者详情:")
        for record in orphan_creators[:10]:  # 只显示前10个
            print(f"  问题ID:{record[0]} | {record[1][:30]}... | 创建者ID:{record[2]} | 时间:{record[3]}")
        if len(orphan_creators) > 10:
            print(f"  ... 还有 {len(orphan_creators) - 10} 个记录")
    
    if orphan_assignees:
        print(f"\n📋 孤立分配者详情:")
        for record in orphan_assignees[:10]:  # 只显示前10个
            print(f"  问题ID:{record[0]} | {record[1][:30]}... | 分配者ID:{record[2]} | 时间:{record[3]}")
        if len(orphan_assignees) > 10:
            print(f"  ... 还有 {len(orphan_assignees) - 10} 个记录")
    
    return orphan_creators, orphan_assignees

def get_available_users(sqlite_conn):
    """获取可用的用户列表"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT id, username, chinese_name, role FROM users ORDER BY id")
    users = cursor.fetchall()
    
    print(f"\n👥 可用用户列表:")
    for user in users:
        print(f"  ID:{user[0]} | {user[1]} ({user[2]}) | {user[3]}")
    
    return users

def fix_orphan_records_interactive(sqlite_conn):
    """交互式修复孤立记录"""
    print("\n🔧 交互式修复孤立记录")
    print("=" * 50)
    
    orphan_creators, orphan_assignees = analyze_orphan_records(sqlite_conn)
    
    if not orphan_creators and not orphan_assignees:
        print("✅ 没有发现孤立记录，数据完整性良好！")
        return True
    
    users = get_available_users(sqlite_conn)
    
    print(f"\n🛠️ 修复选项:")
    print("1. 将所有孤立记录的用户ID设为NULL（推荐）")
    print("2. 将孤立记录分配给默认用户（admin）")
    print("3. 手动指定用户ID")
    print("4. 删除孤立记录")
    print("5. 跳过修复")
    
    choice = input("\n请选择修复方式 (1-5): ").strip()
    
    cursor = sqlite_conn.cursor()
    
    if choice == "1":
        # 设为NULL
        print("🔧 将孤立用户ID设为NULL...")
        
        if orphan_creators:
            cursor.execute("""
                UPDATE bugs SET created_by = NULL 
                WHERE id IN (
                    SELECT b.id FROM bugs b 
                    LEFT JOIN users u ON b.created_by = u.id 
                    WHERE b.created_by IS NOT NULL AND u.id IS NULL
                )
            """)
            print(f"  ✅ 修复了 {len(orphan_creators)} 个孤立创建者")
        
        if orphan_assignees:
            cursor.execute("""
                UPDATE bugs SET assigned_to = NULL 
                WHERE id IN (
                    SELECT b.id FROM bugs b 
                    LEFT JOIN users u ON b.assigned_to = u.id 
                    WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
                )
            """)
            print(f"  ✅ 修复了 {len(orphan_assignees)} 个孤立分配者")
    
    elif choice == "2":
        # 分配给admin用户
        cursor.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ 未找到admin用户，无法执行此操作")
            return False
        
        admin_id = admin_user[0]
        print(f"🔧 将孤立记录分配给admin用户 (ID: {admin_id})...")
        
        if orphan_creators:
            cursor.execute("""
                UPDATE bugs SET created_by = ? 
                WHERE id IN (
                    SELECT b.id FROM bugs b 
                    LEFT JOIN users u ON b.created_by = u.id 
                    WHERE b.created_by IS NOT NULL AND u.id IS NULL
                )
            """, (admin_id,))
            print(f"  ✅ 修复了 {len(orphan_creators)} 个孤立创建者")
        
        if orphan_assignees:
            cursor.execute("""
                UPDATE bugs SET assigned_to = ? 
                WHERE id IN (
                    SELECT b.id FROM bugs b 
                    LEFT JOIN users u ON b.assigned_to = u.id 
                    WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
                )
            """, (admin_id,))
            print(f"  ✅ 修复了 {len(orphan_assignees)} 个孤立分配者")
    
    elif choice == "3":
        # 手动指定用户ID
        try:
            user_id = int(input("请输入要分配的用户ID: "))
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                print(f"❌ 用户ID {user_id} 不存在")
                return False
            
            print(f"🔧 将孤立记录分配给用户 {user[0]} (ID: {user_id})...")
            
            if orphan_creators:
                cursor.execute("""
                    UPDATE bugs SET created_by = ? 
                    WHERE id IN (
                        SELECT b.id FROM bugs b 
                        LEFT JOIN users u ON b.created_by = u.id 
                        WHERE b.created_by IS NOT NULL AND u.id IS NULL
                    )
                """, (user_id,))
                print(f"  ✅ 修复了 {len(orphan_creators)} 个孤立创建者")
            
            if orphan_assignees:
                cursor.execute("""
                    UPDATE bugs SET assigned_to = ? 
                    WHERE id IN (
                        SELECT b.id FROM bugs b 
                        LEFT JOIN users u ON b.assigned_to = u.id 
                        WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
                    )
                """, (user_id,))
                print(f"  ✅ 修复了 {len(orphan_assignees)} 个孤立分配者")
        
        except ValueError:
            print("❌ 无效的用户ID")
            return False
    
    elif choice == "4":
        # 删除孤立记录
        print("⚠️ 警告：这将永久删除孤立的问题记录！")
        confirm = input("确认删除？(输入 'DELETE' 确认): ")
        
        if confirm == "DELETE":
            orphan_bug_ids = set()
            
            for record in orphan_creators:
                orphan_bug_ids.add(record[0])
            for record in orphan_assignees:
                orphan_bug_ids.add(record[0])
            
            if orphan_bug_ids:
                placeholders = ','.join(['?'] * len(orphan_bug_ids))
                cursor.execute(f"DELETE FROM bugs WHERE id IN ({placeholders})", list(orphan_bug_ids))
                print(f"  🗑️ 删除了 {len(orphan_bug_ids)} 个孤立问题记录")
        else:
            print("❌ 删除操作已取消")
            return False
    
    elif choice == "5":
        print("⏭️ 跳过修复")
        return False
    
    else:
        print("❌ 无效选择")
        return False
    
    sqlite_conn.commit()
    print("✅ 修复操作完成")
    return True

def fix_orphan_records_auto(sqlite_conn):
    """自动修复孤立记录（设为NULL）"""
    print("🔧 自动修复孤立记录（设为NULL）...")
    
    cursor = sqlite_conn.cursor()
    
    # 修复孤立创建者
    cursor.execute("""
        UPDATE bugs SET created_by = NULL 
        WHERE id IN (
            SELECT b.id FROM bugs b 
            LEFT JOIN users u ON b.created_by = u.id 
            WHERE b.created_by IS NOT NULL AND u.id IS NULL
        )
    """)
    creator_fixed = cursor.rowcount
    
    # 修复孤立分配者
    cursor.execute("""
        UPDATE bugs SET assigned_to = NULL 
        WHERE id IN (
            SELECT b.id FROM bugs b 
            LEFT JOIN users u ON b.assigned_to = u.id 
            WHERE b.assigned_to IS NOT NULL AND u.id IS NULL
        )
    """)
    assignee_fixed = cursor.rowcount
    
    # 修复孤立通知
    cursor.execute("""
        DELETE FROM notifications 
        WHERE id IN (
            SELECT n.id FROM notifications n 
            LEFT JOIN users u ON n.user_id = u.id 
            WHERE n.user_id IS NOT NULL AND u.id IS NULL
        )
    """)
    notification_fixed = cursor.rowcount
    
    sqlite_conn.commit()
    
    print(f"  ✅ 修复了 {creator_fixed} 个孤立创建者")
    print(f"  ✅ 修复了 {assignee_fixed} 个孤立分配者")
    print(f"  ✅ 删除了 {notification_fixed} 个孤立通知")
    
    total_fixed = creator_fixed + assignee_fixed + notification_fixed
    print(f"  🎉 总计修复 {total_fixed} 个孤立记录")
    
    return total_fixed > 0

def verify_fix(sqlite_conn):
    """验证修复结果"""
    print("\n🔍 验证修复结果...")
    
    cursor = sqlite_conn.cursor()
    
    # 检查孤立记录
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
    
    cursor.execute("""
        SELECT COUNT(*) FROM notifications n 
        LEFT JOIN users u ON n.user_id = u.id 
        WHERE n.user_id IS NOT NULL AND u.id IS NULL
    """)
    orphan_notification = cursor.fetchone()[0]
    
    total_orphans = orphan_creator + orphan_assignee + orphan_notification
    
    print(f"  孤立创建者: {orphan_creator}")
    print(f"  孤立分配者: {orphan_assignee}")
    print(f"  孤立通知: {orphan_notification}")
    
    if total_orphans == 0:
        print("  🎉 所有孤立记录已修复！")
        return True
    else:
        print(f"  ⚠️ 仍有 {total_orphans} 个孤立记录")
        return False

def main():
    """主函数"""
    print("🔧 SQLite数据库孤立记录修复工具")
    print("=" * 50)
    
    # 连接SQLite数据库
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
    
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite数据库文件不存在: {sqlite_path}")
        return False
    
    try:
        sqlite_conn = sqlite3.connect(sqlite_path)
        print(f"✅ 连接SQLite数据库: {sqlite_path}")
        
        # 检查是否需要修复
        orphan_creators, orphan_assignees = analyze_orphan_records(sqlite_conn)
        
        if not orphan_creators and not orphan_assignees:
            print("✅ 数据完整性良好，无需修复！")
            return True
        
        # 询问修复方式
        print(f"\n🤔 修复方式:")
        print("1. 交互式修复（推荐）")
        print("2. 自动修复（设为NULL）")
        
        mode = input("请选择修复方式 (1-2): ").strip()
        
        if mode == "1":
            success = fix_orphan_records_interactive(sqlite_conn)
        elif mode == "2":
            success = fix_orphan_records_auto(sqlite_conn)
        else:
            print("❌ 无效选择")
            return False
        
        if success:
            verify_fix(sqlite_conn)
        
        return success
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✅ 建议运行 verify_migration.py 验证修复结果")
    else:
        print("\n❌ 修复失败，请检查错误信息")
