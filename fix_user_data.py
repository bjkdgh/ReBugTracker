#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

# 设置环境变量
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'rebugtracker.db')

def fix_user_data():
    """修复用户数据"""
    print("🔧 修复用户数据...")
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    
    try:
        # 1. 更新李世杰的信息
        print("👤 更新李世杰的用户信息...")
        c.execute("""
            UPDATE users 
            SET role = '产品经理',
                role_en = 'pm',
                team = '实施组,实施组研发,新能源,网络分析,第三道防线,智能告警,操作票及防误,电量,消纳,自动发电控制'
            WHERE username = 'lsj'
        """)
        print("✅ 李世杰信息更新成功")
        
        # 2. 为现有Bug随机分配产品线
        print("🐛 为现有Bug分配产品线...")
        
        # 获取所有产品线ID
        c.execute("SELECT id, name FROM product_lines")
        product_lines = c.fetchall()
        
        # 获取所有没有产品线的Bug
        c.execute("SELECT id FROM bugs WHERE product_line_id IS NULL")
        bugs_without_pl = c.fetchall()
        
        import random
        for bug in bugs_without_pl:
            bug_id = bug[0]
            # 随机选择一个产品线
            pl = random.choice(product_lines)
            pl_id = pl[0]
            pl_name = pl[1]
            
            c.execute("UPDATE bugs SET product_line_id = ? WHERE id = ?", (pl_id, bug_id))
            print(f"  Bug {bug_id} 分配到产品线: {pl_name}")
        
        print(f"✅ 共为 {len(bugs_without_pl)} 个Bug分配了产品线")
        
        # 提交事务
        conn.commit()
        print("✅ 所有修复完成")
        
        # 验证修复结果
        print("\n📊 验证修复结果:")
        
        # 检查李世杰的信息
        c.execute("SELECT username, chinese_name, role, role_en, team FROM users WHERE username = 'lsj'")
        user = c.fetchone()
        if user:
            print(f"👤 李世杰信息:")
            print(f"  用户名: {user[0]}")
            print(f"  中文名: {user[1]}")
            print(f"  角色: {user[2]}")
            print(f"  角色英文: {user[3]}")
            print(f"  团队: {user[4]}")
        
        # 检查Bug产品线分配情况
        c.execute("""
            SELECT pl.name, COUNT(b.id) as bug_count
            FROM product_lines pl
            LEFT JOIN bugs b ON pl.id = b.product_line_id
            GROUP BY pl.id, pl.name
            ORDER BY bug_count DESC
        """)
        pl_stats = c.fetchall()
        
        print(f"\n📋 各产品线Bug分布:")
        for stat in pl_stats:
            print(f"  {stat[0]}: {stat[1]} 个Bug")
        
    except Exception as e:
        print(f"❌ 修复数据时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_user_data()
