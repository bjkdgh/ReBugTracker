#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from psycopg2.extras import DictCursor
import psycopg2

# 设置环境变量
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'rebugtracker.db')

def get_db_connection():
    """获取数据库连接"""
    if DB_TYPE == 'postgres':
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'rebugtracker'),
            user=os.getenv('POSTGRES_USER', 'rebugtracker'),
            password=os.getenv('POSTGRES_PASSWORD', 'rebugtracker123'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )
    else:
        return sqlite3.connect(SQLITE_DB_PATH)

def check_data():
    """检查数据库中的数据"""
    print(f"🔍 检查数据库数据 (DB_TYPE: {DB_TYPE})")
    print(f"📁 数据库路径: {SQLITE_DB_PATH}")
    print("=" * 60)

    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()

    try:
        # 首先检查所有表
        print("📋 数据库中的所有表:")
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        print()
        # 1. 检查product_lines表
        print("📋 Product Lines 表数据:")
        c.execute("SELECT id, name, description, status FROM product_lines ORDER BY id")
        product_lines = c.fetchall()
        
        if product_lines:
            for pl in product_lines:
                if isinstance(pl, dict):
                    print(f"  ID: {pl['id']}, Name: {pl['name']}, Status: {pl['status']}")
                else:
                    print(f"  ID: {pl[0]}, Name: {pl[1]}, Status: {pl[3]}")
        else:
            print("  ❌ 没有产品线数据")
        
        print()
        
        # 2. 检查bugs表
        print("📋 Bugs 表数据:")
        c.execute("""
            SELECT b.id, b.title, b.status, b.product_line_id, pl.name as product_line_name
            FROM bugs b
            LEFT JOIN product_lines pl ON b.product_line_id = pl.id
            ORDER BY b.id
            LIMIT 10
        """)
        bugs = c.fetchall()
        
        if bugs:
            for bug in bugs:
                if isinstance(bug, dict):
                    print(f"  ID: {bug['id']}, Title: {bug['title'][:30]}..., Status: {bug['status']}, Product Line: {bug['product_line_name']}")
                else:
                    print(f"  ID: {bug[0]}, Title: {bug[1][:30]}..., Status: {bug[2]}, Product Line: {bug[4]}")
        else:
            print("  ❌ 没有Bug数据")
        
        print()
        
        # 3. 检查用户李世杰的团队信息
        print("👤 用户李世杰的信息:")
        c.execute("SELECT id, username, chinese_name, team, role FROM users WHERE username = 'lsj'")
        user = c.fetchone()
        
        if user:
            if isinstance(user, dict):
                print(f"  ID: {user['id']}")
                print(f"  用户名: {user['username']}")
                print(f"  中文名: {user['chinese_name']}")
                print(f"  角色: {user['role']}")
                print(f"  团队: {user['team']}")
                user_teams = user['team'].split(',') if user['team'] else []
            else:
                print(f"  ID: {user[0]}")
                print(f"  用户名: {user[1]}")
                print(f"  中文名: {user[2]}")
                print(f"  角色: {user[4]}")
                print(f"  团队: {user[3]}")
                user_teams = user[3].split(',') if user[3] else []
        else:
            print("  ❌ 找不到用户lsj")
            user_teams = []
        
        print()
        
        # 4. 检查团队与产品线的匹配情况
        print("🔗 团队与产品线匹配情况:")
        if user_teams:
            for team in user_teams:
                team = team.strip()
                c.execute("SELECT id, name FROM product_lines WHERE name = ?", (team,))
                matching_pl = c.fetchone()
                if matching_pl:
                    if isinstance(matching_pl, dict):
                        print(f"  ✅ 团队 '{team}' 匹配产品线: {matching_pl['name']} (ID: {matching_pl['id']})")
                    else:
                        print(f"  ✅ 团队 '{team}' 匹配产品线: {matching_pl[1]} (ID: {matching_pl[0]})")
                else:
                    print(f"  ❌ 团队 '{team}' 没有匹配的产品线")
        
        print()
        
        # 5. 统计各状态的Bug数量
        print("📊 Bug状态统计:")
        c.execute("""
            SELECT status, COUNT(*) as count
            FROM bugs
            GROUP BY status
            ORDER BY count DESC
        """)
        status_stats = c.fetchall()
        
        for stat in status_stats:
            if isinstance(stat, dict):
                print(f"  {stat['status']}: {stat['count']} 个")
            else:
                print(f"  {stat[0]}: {stat[1]} 个")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_data()
