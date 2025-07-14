#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为用户表添加Gotify个人Token字段
解决Gotify通知精准推送问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection
from sql_adapter import adapt_sql
from config import DB_TYPE

def add_gotify_user_token_field():
    """为用户表添加Gotify个人Token字段"""
    
    print("🔧 为用户表添加Gotify个人Token字段...")
    
    try:
        conn = get_db_connection()
        if DB_TYPE == 'postgres':
            from psycopg2.extras import DictCursor
            cursor = conn.cursor(cursor_factory=DictCursor)
        else:
            cursor = conn.cursor()
        
        # 检查字段是否已存在
        if DB_TYPE == 'postgres':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'gotify_app_token'
            """)
        else:
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            existing = 'gotify_app_token' in columns
            
        if DB_TYPE == 'postgres':
            existing = cursor.fetchone() is not None
        
        if existing:
            print("   ⚠️ gotify_app_token字段已存在，跳过添加")
        else:
            # 添加字段
            if DB_TYPE == 'postgres':
                cursor.execute("ALTER TABLE users ADD COLUMN gotify_app_token VARCHAR(255)")
            else:
                cursor.execute("ALTER TABLE users ADD COLUMN gotify_app_token TEXT")
            
            print("   ✅ 成功添加gotify_app_token字段")
        
        # 检查并添加gotify_user_id字段（用于存储Gotify用户ID）
        if DB_TYPE == 'postgres':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'gotify_user_id'
            """)
            existing_user_id = cursor.fetchone() is not None
        else:
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            existing_user_id = 'gotify_user_id' in columns
        
        if existing_user_id:
            print("   ⚠️ gotify_user_id字段已存在，跳过添加")
        else:
            # 添加字段
            if DB_TYPE == 'postgres':
                cursor.execute("ALTER TABLE users ADD COLUMN gotify_user_id VARCHAR(255)")
            else:
                cursor.execute("ALTER TABLE users ADD COLUMN gotify_user_id TEXT")
            
            print("   ✅ 成功添加gotify_user_id字段")
        
        conn.commit()
        conn.close()
        
        print("\n📋 字段添加完成！")
        print("\n📝 使用说明：")
        print("1. 用户需要在Gotify服务器上注册账号")
        print("2. 用户创建个人应用，获取App Token")
        print("3. 在ReBugTracker个人设置中配置Token")
        print("4. 配置后将实现精准推送，只有相关用户收到通知")
        
        return True
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
        return False

if __name__ == "__main__":
    success = add_gotify_user_token_field()
    if success:
        print("\n🎉 数据库更新成功！")
    else:
        print("\n💥 数据库更新失败！")
        sys.exit(1)
