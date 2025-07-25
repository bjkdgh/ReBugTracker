#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Bug类型功能的脚本
验证数据库中type字段是否正确添加和工作
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bug_type_feature():
    """测试Bug类型功能"""
    try:
        print("🧪 开始测试Bug类型功能...")
        
        # 导入数据库工厂
        from db_factory import get_db_connection
        from config import DB_TYPE
        
        print(f"📊 当前数据库类型: {DB_TYPE}")
        
        # 获取数据库连接
        conn = get_db_connection()
        
        if DB_TYPE == 'postgres':
            from psycopg2.extras import DictCursor
            cursor = conn.cursor(cursor_factory=DictCursor)
        else:
            cursor = conn.cursor()
        
        # 1. 验证type字段是否存在
        print("🔍 验证type字段是否存在...")
        if DB_TYPE == 'postgres':
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'bugs' AND column_name = 'type'
            """)
            result = cursor.fetchone()
            if result:
                print("✅ PostgreSQL: type字段存在")
            else:
                print("❌ PostgreSQL: type字段不存在")
                return False
        else:
            cursor.execute("PRAGMA table_info(bugs)")
            columns = cursor.fetchall()
            type_column = [col for col in columns if col[1] == 'type']
            if type_column:
                print("✅ SQLite: type字段存在")
            else:
                print("❌ SQLite: type字段不存在")
                return False
        
        # 2. 测试插入不同类型的问题
        print("📝 测试插入不同类型的问题...")
        
        # 插入一个Bug类型的问题
        if DB_TYPE == 'postgres':
            cursor.execute("""
                INSERT INTO bugs (title, description, type, status, created_by, project)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, ("测试Bug问题", "这是一个测试Bug", "bug", "待处理", 1, "测试项目"))
            bug_id = cursor.fetchone()['id']
        else:
            cursor.execute("""
                INSERT INTO bugs (title, description, type, status, created_by, project)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("测试Bug问题", "这是一个测试Bug", "bug", "待处理", 1, "测试项目"))
            bug_id = cursor.lastrowid
        
        print(f"✅ 成功插入Bug类型问题，ID: {bug_id}")
        
        # 插入一个需求类型的问题
        if DB_TYPE == 'postgres':
            cursor.execute("""
                INSERT INTO bugs (title, description, type, status, created_by, project)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, ("测试需求问题", "这是一个测试需求", "需求", "待处理", 1, "测试项目"))
            req_id = cursor.fetchone()['id']
        else:
            cursor.execute("""
                INSERT INTO bugs (title, description, type, status, created_by, project)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("测试需求问题", "这是一个测试需求", "需求", "待处理", 1, "测试项目"))
            req_id = cursor.lastrowid
        
        print(f"✅ 成功插入需求类型问题，ID: {req_id}")
        
        # 3. 查询验证
        print("🔍 查询验证插入的数据...")
        if DB_TYPE == 'postgres':
            cursor.execute("SELECT id, title, type FROM bugs WHERE id IN (%s, %s)", (bug_id, req_id))
        else:
            cursor.execute("SELECT id, title, type FROM bugs WHERE id IN (?, ?)", (bug_id, req_id))
        
        results = cursor.fetchall()
        for row in results:
            if DB_TYPE == 'postgres':
                print(f"✅ ID: {row['id']}, 标题: {row['title']}, 类型: {row['type']}")
            else:
                print(f"✅ ID: {row[0]}, 标题: {row[1]}, 类型: {row[2]}")
        
        # 4. 清理测试数据
        print("🧹 清理测试数据...")
        if DB_TYPE == 'postgres':
            cursor.execute("DELETE FROM bugs WHERE id IN (%s, %s)", (bug_id, req_id))
        else:
            cursor.execute("DELETE FROM bugs WHERE id IN (?, ?)", (bug_id, req_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Bug类型功能测试完成！所有测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bug_type_feature()
    if success:
        print("\n✅ 功能测试成功！")
        print("现在你可以：")
        print("1. 在提交问题页面选择'Bug'或'需求'类型")
        print("2. 在问题列表中看到类型标签")
        print("3. 在问题详情页面看到类型信息")
    else:
        print("\n❌ 功能测试失败！")
        sys.exit(1)
