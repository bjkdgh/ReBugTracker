#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复打包exe版本的数据库问题
解决 "no such table: product_lines" 错误

使用方法：
1. 将此脚本放在exe文件同目录下
2. 运行: python fix_exe_database.py
3. 重新启动ReBugTracker.exe

作者: ReBugTracker Team
日期: 2025-08-12
"""

import sqlite3
import os
import sys
from datetime import datetime

def fix_database():
    """修复数据库，添加缺失的product_lines表"""
    
    # 查找数据库文件
    db_files = ['rebugtracker.db', 'data/rebugtracker.db', './rebugtracker.db']
    db_path = None
    
    for path in db_files:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ 错误: 找不到数据库文件 rebugtracker.db")
        print("请确保此脚本与ReBugTracker.exe在同一目录下")
        return False
    
    print(f"📁 找到数据库文件: {db_path}")
    
    try:
        # 备份数据库
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ 数据库已备份到: {backup_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 检查是否已存在product_lines表
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_lines'")
        if c.fetchone():
            print("✅ product_lines表已存在，无需修复")
            conn.close()
            return True
        
        print("🔧 开始修复数据库...")
        
        # 创建product_lines表
        c.execute('''
            CREATE TABLE IF NOT EXISTS product_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        print("✅ product_lines表创建成功")
        
        # 插入示例产品线数据
        sample_products = [
            ('实施组', '实施组产品线'),
            ('实施组研发', '实施组研发产品线'),
            ('新能源', '新能源产品线'),
            ('网络分析', '网络分析产品线'),
            ('第三道防线', '第三道防线产品线'),
            ('智能告警', '智能告警产品线'),
            ('操作票及防误', '操作票及防误产品线'),
            ('电量', '电量产品线'),
            ('消纳', '消纳产品线'),
            ('自动发电控制', '自动发电控制产品线')
        ]
        
        for name, description in sample_products:
            c.execute("INSERT OR IGNORE INTO product_lines (name, description) VALUES (?, ?)", 
                     (name, description))
        
        print("✅ 产品线数据插入成功")
        
        # 为bugs表添加product_line_id字段（如果不存在）
        c.execute("PRAGMA table_info(bugs)")
        columns = [info[1] for info in c.fetchall()]
        if 'product_line_id' not in columns:
            c.execute('ALTER TABLE bugs ADD COLUMN product_line_id INTEGER')
            print("✅ bugs表添加product_line_id字段成功")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("🎉 数据库修复完成！")
        print("现在可以正常启动ReBugTracker.exe了")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        return False

def verify_fix():
    """验证修复结果"""
    db_files = ['rebugtracker.db', 'data/rebugtracker.db', './rebugtracker.db']
    db_path = None
    
    for path in db_files:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 检查表是否存在
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_lines'")
        table_exists = c.fetchone() is not None
        
        if table_exists:
            # 检查数据
            c.execute("SELECT COUNT(*) FROM product_lines")
            count = c.fetchone()[0]
            print(f"✅ 验证成功: product_lines表存在，包含 {count} 条记录")
        else:
            print("❌ 验证失败: product_lines表不存在")
        
        conn.close()
        return table_exists
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ReBugTracker 数据库修复工具")
    print("=" * 50)
    
    if fix_database():
        print("\n🔍 验证修复结果...")
        if verify_fix():
            print("\n✅ 修复成功！现在可以启动ReBugTracker.exe了")
        else:
            print("\n❌ 修复验证失败，请检查错误信息")
    else:
        print("\n❌ 修复失败，请检查错误信息")
    
    input("\n按回车键退出...")
