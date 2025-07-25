#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为bugs表添加type字段的数据库迁移脚本
用于区分"需求"和"bug"
支持强制指定数据库类型进行迁移
"""

import sys
import os
import traceback
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_bug_type_field(force_db_type=None):
    """为bugs表添加type字段

    功能：
    - 为bugs表添加type字段（需求/bug）
    - 设置默认值为'bug'
    - 更新现有数据

    Args:
        force_db_type: 强制指定数据库类型 ('postgres' 或 'sqlite')
    """
    try:
        print("🔧 开始为bugs表添加type字段...")

        # 导入数据库工厂
        from db_factory import get_db_connection
        from config import DB_TYPE

        # 如果指定了强制数据库类型，临时修改配置
        current_db_type = force_db_type if force_db_type else DB_TYPE
        print(f"📊 当前数据库类型: {current_db_type}")

        # 如果强制指定了PostgreSQL，需要临时修改配置
        if force_db_type == 'postgres':
            # 临时修改环境变量
            os.environ['DB_TYPE'] = 'postgres'
            # 重新导入配置以获取更新后的值
            import importlib
            import config
            importlib.reload(config)
            conn = get_db_connection()
        else:
            # 获取数据库连接
            conn = get_db_connection()

        if current_db_type == 'postgres':
            # PostgreSQL模式
            try:
                from psycopg2.extras import DictCursor
                cursor = conn.cursor(cursor_factory=DictCursor)
            except:
                # 如果不是真正的PostgreSQL连接，使用普通cursor
                cursor = conn.cursor()

            print("📋 添加type字段...")
            try:
                cursor.execute('ALTER TABLE bugs ADD COLUMN IF NOT EXISTS type TEXT DEFAULT \'bug\'')
                print("✅ 添加type字段成功")
            except Exception as e:
                print(f"⚠️ type字段可能已存在: {e}")

            # 更新现有数据的type字段
            print("📝 更新现有数据...")
            cursor.execute("UPDATE bugs SET type = 'bug' WHERE type IS NULL")
            affected_rows = cursor.rowcount
            print(f"✅ 更新了 {affected_rows} 条记录")

            conn.commit()

        else:
            # SQLite模式
            cursor = conn.cursor()

            print("📋 添加type字段...")
            try:
                cursor.execute('ALTER TABLE bugs ADD COLUMN type TEXT DEFAULT \'bug\'')
                print("✅ 添加type字段成功")
            except Exception as e:
                print(f"⚠️ type字段可能已存在: {e}")

            # 更新现有数据的type字段
            print("📝 更新现有数据...")
            cursor.execute("UPDATE bugs SET type = 'bug' WHERE type IS NULL")
            affected_rows = cursor.rowcount
            print(f"✅ 更新了 {affected_rows} 条记录")

            conn.commit()

        # 验证字段是否添加成功
        print("🔍 验证字段添加结果...")
        if current_db_type == 'postgres':
            cursor.execute("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'bugs' AND column_name = 'type'
            """)
        else:
            cursor.execute("PRAGMA table_info(bugs)")
            columns = cursor.fetchall()
            type_column = [col for col in columns if col[1] == 'type']
            if type_column:
                print(f"✅ type字段验证成功: {type_column[0]}")
            else:
                print("❌ type字段验证失败")
                return False

        if current_db_type == 'postgres':
            result = cursor.fetchone()
            if result:
                print(f"✅ type字段验证成功: {dict(result)}")
            else:
                print("❌ type字段验证失败")
                return False

        cursor.close()
        conn.close()

        print("🎉 bugs表type字段添加完成！")
        return True

    except Exception as e:
        print(f"❌ 添加type字段失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='为bugs表添加type字段')
    parser.add_argument('--db-type', choices=['postgres', 'sqlite'],
                       help='强制指定数据库类型')
    args = parser.parse_args()

    success = add_bug_type_field(force_db_type=args.db_type)
    if success:
        print("\n✅ 数据库迁移成功完成！")
        print("现在可以在提交问题时选择类型：需求 或 bug")
    else:
        print("\n❌ 数据库迁移失败！")
        sys.exit(1)
