#!/usr/bin/env python3
# 数据库表结构更新工具
# 主要功能：为users表添加新的字段，并根据现有字段值生成对应的英文标识

import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_database_structure():
    """更新数据库表结构
    
    功能：
    - 为users表添加role_en、team_en和chinese_name新字段
    - 根据中文角色名称生成对应的角色英文标识
    - 根据中文团队名称生成对应的团队英文标识
    """
    try:
        print("🔧 开始更新数据库表结构...")
        
        # 导入数据库工厂
        from db_factory import get_db_connection
        from config import DB_TYPE
        
        print(f"📊 当前数据库类型: {DB_TYPE}")
        
        # 获取数据库连接
        conn = get_db_connection()
        
        if DB_TYPE == 'postgres':
            # PostgreSQL模式
            conn.autocommit = True
            cursor = conn.cursor()
            
            print("📋 添加新字段...")
            # 添加role_en和team_en列
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS role_en TEXT')
                print("✅ 添加role_en字段")
            except Exception as e:
                print(f"⚠️ role_en字段可能已存在: {e}")
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS team_en TEXT')
                print("✅ 添加team_en字段")
            except Exception as e:
                print(f"⚠️ team_en字段可能已存在: {e}")
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS chinese_name TEXT')
                print("✅ 添加chinese_name字段")
            except Exception as e:
                print(f"⚠️ chinese_name字段可能已存在: {e}")
            
            print("🔄 更新现有数据...")
            # 更新现有数据
            cursor.execute('''UPDATE users SET 
                           role_en = CASE 
                             WHEN role = '管理员' THEN 'gly' 
                             WHEN role = '负责人' THEN 'fzr' 
                             WHEN role = '组内成员' THEN 'zncy' 
                             WHEN role = '实施组' THEN 'ssz' 
                             ELSE role 
                           END,
                           team_en = CASE
                             WHEN team = '网络分析' THEN 'wlfx'
                             WHEN team = '实施组' THEN 'ssz'
                             WHEN team = '第三道防线' THEN 'dsdfx'
                             WHEN team = '新能源' THEN 'xny'
                             WHEN team = '管理员' THEN 'gly'
                             WHEN team = '开发组' THEN 'dev'
                             ELSE team
                           END
                           WHERE role_en IS NULL OR team_en IS NULL''')
            
        else:
            # SQLite模式
            cursor = conn.cursor()
            
            print("📋 添加新字段...")
            # SQLite的ALTER TABLE ADD COLUMN语法
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN role_en TEXT')
                print("✅ 添加role_en字段")
            except Exception as e:
                print(f"⚠️ role_en字段可能已存在: {e}")
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN team_en TEXT')
                print("✅ 添加team_en字段")
            except Exception as e:
                print(f"⚠️ team_en字段可能已存在: {e}")
            
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN chinese_name TEXT')
                print("✅ 添加chinese_name字段")
            except Exception as e:
                print(f"⚠️ chinese_name字段可能已存在: {e}")
            
            print("🔄 更新现有数据...")
            # 更新现有数据
            cursor.execute('''UPDATE users SET 
                           role_en = CASE 
                             WHEN role = '管理员' THEN 'gly' 
                             WHEN role = '负责人' THEN 'fzr' 
                             WHEN role = '组内成员' THEN 'zncy' 
                             WHEN role = '实施组' THEN 'ssz' 
                             ELSE role 
                           END,
                           team_en = CASE
                             WHEN team = '网络分析' THEN 'wlfx'
                             WHEN team = '实施组' THEN 'ssz'
                             WHEN team = '第三道防线' THEN 'dsdfx'
                             WHEN team = '新能源' THEN 'xny'
                             WHEN team = '管理员' THEN 'gly'
                             WHEN team = '开发组' THEN 'dev'
                             ELSE team
                           END
                           WHERE role_en IS NULL OR team_en IS NULL''')
            
            conn.commit()
        
        # 验证更新结果
        print("🔍 验证更新结果...")
        cursor.execute("SELECT username, role, role_en, team, team_en FROM users LIMIT 5")
        results = cursor.fetchall()
        
        print("前5个用户的更新结果:")
        for row in results:
            print(f"  {row[0]}: {row[1]} -> {row[2]}, {row[3]} -> {row[4]}")
        
        # 关闭数据库连接
        conn.close()
        
        print("✅ 数据库表结构更新成功!")
        return True
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保在项目根目录运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        traceback.print_exc()
        return False

def create_test_database():
    """创建测试数据库（仅SQLite）"""
    try:
        print("🛠️ 创建测试SQLite数据库...")
        
        import sqlite3
        
        # 创建测试数据库
        test_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_rebugtracker.db')
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # 创建users表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                chinese_name TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                role_en TEXT,
                team TEXT,
                team_en TEXT
            )
        ''')
        
        # 创建bugs表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT '待处理',
                assigned_to INTEGER,
                created_by INTEGER,
                project TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution TEXT,
                image_path TEXT
            )
        ''')
        
        # 插入测试数据
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, chinese_name, role, role_en, team, team_en)
            VALUES ('testuser', 'test123', '测试用户', '组内成员', 'zncy', '开发组', 'dev')
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ 测试数据库创建成功: {test_db_path}")
        return True
        
    except Exception as e:
        print(f"❌ 创建测试数据库失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 数据库表结构更新工具")
    print("=" * 40)
    
    # 更新数据库结构
    success = update_database_structure()
    
    # 可选：创建测试数据库
    print("\n" + "-" * 40)
    create_test_database()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ 数据库更新完成")
    else:
        print("❌ 数据库更新失败")
