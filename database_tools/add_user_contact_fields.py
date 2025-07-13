#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为用户表添加联系方式字段（email, phone）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection
from sql_adapter import adapt_sql

def add_user_contact_fields():
    """为用户表添加email和phone字段"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔧 开始为用户表添加联系方式字段...")
        
        # 检查字段是否已存在
        print("📋 检查现有字段...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"   现有字段: {existing_columns}")
        
        # 添加email字段
        if 'email' not in existing_columns:
            print("📧 添加email字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
            print("   ✅ email字段添加成功")
        else:
            print("   ✅ email字段已存在")
        
        # 添加phone字段
        if 'phone' not in existing_columns:
            print("📱 添加phone字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
            print("   ✅ phone字段添加成功")
        else:
            print("   ✅ phone字段已存在")
        
        # 为现有用户添加默认邮箱（基于用户名）
        print("📧 为现有用户设置默认邮箱...")
        cursor.execute("""
            UPDATE users 
            SET email = username || '@example.com' 
            WHERE email IS NULL OR email = ''
        """)
        
        updated_count = cursor.rowcount
        print(f"   ✅ 为 {updated_count} 个用户设置了默认邮箱")
        
        # 提交更改
        conn.commit()
        
        # 验证更改
        print("🔍 验证字段添加结果...")
        cursor.execute("SELECT id, username, email, phone FROM users LIMIT 5")
        users = cursor.fetchall()
        
        print("   示例用户数据:")
        for user in users:
            print(f"     ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 电话: {user[3]}")
        
        conn.close()
        
        print("✅ 用户表联系方式字段添加完成！")
        return True
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def check_user_table_structure():
    """检查用户表结构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n📊 用户表结构信息:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({'可空' if col[2] == 'YES' else '非空'}) {f'默认值: {col[3]}' if col[3] else ''}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker 用户表字段更新工具")
    print("=" * 50)
    
    success = add_user_contact_fields()
    
    if success:
        check_user_table_structure()
        print("\n🎉 用户表字段更新完成！")
    else:
        print("\n💥 用户表字段更新失败！")
        sys.exit(1)
