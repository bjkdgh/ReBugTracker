#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

# 设置环境变量
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'rebugtracker.db')

def check_bug_status():
    """检查Bug状态的实际值"""
    print("🔍 检查Bug状态值...")
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    
    try:
        # 查看所有不同的状态值
        print("📊 数据库中的所有Bug状态:")
        c.execute("SELECT DISTINCT status, COUNT(*) as count FROM bugs GROUP BY status ORDER BY count DESC")
        statuses = c.fetchall()
        
        for status, count in statuses:
            print(f"  '{status}': {count} 个")
        
        print("\n🔍 API查询的状态映射:")
        api_statuses = ['待处理', '处理中', '已解决', '闭环']
        for status in api_statuses:
            c.execute("SELECT COUNT(*) FROM bugs WHERE status = ?", (status,))
            count = c.fetchone()[0]
            print(f"  '{status}': {count} 个")
        
        print("\n📋 前10个Bug的详细状态:")
        c.execute("SELECT id, title, status, product_line_id FROM bugs LIMIT 10")
        bugs = c.fetchall()
        
        for bug in bugs:
            print(f"  ID: {bug[0]}, Status: '{bug[2]}', Title: {bug[1][:20]}...")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_bug_status()
