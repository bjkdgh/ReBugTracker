#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较PostgreSQL和SQLite数据库中users表的数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_users_data(db_type):
    """获取指定数据库类型的用户数据"""
    try:
        # 设置数据库类型
        os.environ['DB_TYPE'] = db_type
        
        # 重新导入以使用新的数据库类型
        import importlib
        import db_factory
        importlib.reload(db_factory)
        
        from db_factory import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取用户数据
        cursor.execute("""
            SELECT id, username, chinese_name, role_en, email, phone
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        return users
        
    except Exception as e:
        print(f"❌ 获取{db_type}数据库用户数据失败: {e}")
        return []

def compare_users_tables():
    """比较两个数据库的users表"""
    print("🔍 比较PostgreSQL和SQLite数据库的users表")
    print("=" * 60)
    
    # 获取PostgreSQL用户数据
    print("📊 获取PostgreSQL用户数据...")
    pg_users = get_users_data('postgres')
    print(f"  PostgreSQL用户数: {len(pg_users)}")
    
    # 获取SQLite用户数据
    print("📊 获取SQLite用户数据...")
    sqlite_users = get_users_data('sqlite')
    print(f"  SQLite用户数: {len(sqlite_users)}")
    
    print("\n" + "=" * 60)
    
    # 详细比较
    print("📋 用户数据详细对比:")
    print("-" * 60)
    print(f"{'ID':<4} {'用户名':<12} {'中文名':<10} {'角色':<8} {'PostgreSQL':<12} {'SQLite':<12} {'状态'}")
    print("-" * 60)
    
    # 创建字典便于比较
    pg_dict = {user[0]: user for user in pg_users} if pg_users else {}
    sqlite_dict = {user[0]: user for user in sqlite_users} if sqlite_users else {}
    
    # 获取所有用户ID
    all_ids = set(pg_dict.keys()) | set(sqlite_dict.keys())
    
    consistent_count = 0
    inconsistent_count = 0
    
    for user_id in sorted(all_ids):
        pg_user = pg_dict.get(user_id)
        sqlite_user = sqlite_dict.get(user_id)
        
        if pg_user and sqlite_user:
            # 两个数据库都有这个用户
            pg_username = pg_user[1]
            sqlite_username = sqlite_user[1]
            
            pg_chinese = pg_user[2] or ""
            sqlite_chinese = sqlite_user[2] or ""
            
            pg_role = pg_user[3] or ""
            sqlite_role = sqlite_user[3] or ""
            
            # 检查是否一致
            if (pg_username == sqlite_username and 
                pg_chinese == sqlite_chinese and 
                pg_role == sqlite_role):
                status = "✅ 一致"
                consistent_count += 1
            else:
                status = "❌ 不一致"
                inconsistent_count += 1
            
            print(f"{user_id:<4} {pg_username:<12} {pg_chinese:<10} {pg_role:<8} {'存在':<12} {'存在':<12} {status}")
            
            # 如果不一致，显示详细差异
            if status == "❌ 不一致":
                print(f"     差异详情:")
                if pg_username != sqlite_username:
                    print(f"       用户名: PG='{pg_username}' vs SQLite='{sqlite_username}'")
                if pg_chinese != sqlite_chinese:
                    print(f"       中文名: PG='{pg_chinese}' vs SQLite='{sqlite_chinese}'")
                if pg_role != sqlite_role:
                    print(f"       角色: PG='{pg_role}' vs SQLite='{sqlite_role}'")
        
        elif pg_user:
            # 只有PostgreSQL有
            print(f"{user_id:<4} {pg_user[1]:<12} {pg_user[2] or '':<10} {pg_user[3] or '':<8} {'存在':<12} {'缺失':<12} ❌ PG独有")
            inconsistent_count += 1
        
        elif sqlite_user:
            # 只有SQLite有
            print(f"{user_id:<4} {sqlite_user[1]:<12} {sqlite_user[2] or '':<10} {sqlite_user[3] or '':<8} {'缺失':<12} {'存在':<12} ❌ SQLite独有")
            inconsistent_count += 1
    
    print("-" * 60)
    print(f"📊 统计结果:")
    print(f"  ✅ 一致的用户: {consistent_count}")
    print(f"  ❌ 不一致的用户: {inconsistent_count}")
    print(f"  📈 一致性比例: {consistent_count/(consistent_count+inconsistent_count)*100:.1f}%" if (consistent_count+inconsistent_count) > 0 else "  📈 一致性比例: 0%")
    
    # 检查email和phone字段
    print("\n📧 检查email和phone字段:")
    print("-" * 40)
    
    if pg_users and sqlite_users:
        # 检查几个用户的email和phone
        for user_id in sorted(list(all_ids)[:5]):  # 检查前5个用户
            pg_user = pg_dict.get(user_id)
            sqlite_user = sqlite_dict.get(user_id)
            
            if pg_user and sqlite_user:
                pg_email = pg_user[4] if len(pg_user) > 4 else "无"
                sqlite_email = sqlite_user[4] if len(sqlite_user) > 4 else "无"
                
                pg_phone = pg_user[5] if len(pg_user) > 5 else "无"
                sqlite_phone = sqlite_user[5] if len(sqlite_user) > 5 else "无"
                
                print(f"用户{user_id} ({pg_user[1]}):")
                print(f"  Email: PG='{pg_email}' vs SQLite='{sqlite_email}'")
                print(f"  Phone: PG='{pg_phone}' vs SQLite='{sqlite_phone}'")
    
    return consistent_count == len(all_ids) and inconsistent_count == 0

if __name__ == "__main__":
    print("🚀 ReBugTracker 用户表数据一致性检查工具")
    print("=" * 50)
    
    is_consistent = compare_users_tables()
    
    if is_consistent:
        print("\n🎉 两个数据库的用户表数据完全一致！")
    else:
        print("\n⚠️ 两个数据库的用户表数据存在差异，建议进行数据同步。")
    
    print("\n💡 提示: 如果需要同步数据，可以使用postgres_to_sqlite工具。")
