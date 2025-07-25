#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库结构验证工具
验证数据库结构是否符合预期的规范，检查关键字段的类型、约束和默认值
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from config import POSTGRES_CONFIG, DB_TYPE

def validate_sqlite_structure():
    """验证SQLite数据库结构"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 验证SQLite数据库结构规范")
        print("=" * 60)
        
        validation_results = []
        
        # 验证必需的表是否存在
        expected_tables = ['users', 'bugs', 'bug_images', 'projects', 'system_config', 'user_notification_preferences', 'notifications']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("📋 表存在性检查:")
        for table in expected_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
                validation_results.append(True)
            else:
                print(f"  ❌ {table} - 缺失")
                validation_results.append(False)
        
        # 验证关键字段
        print("\n📋 关键字段验证:")
        
        # 验证bugs表的status字段默认值
        cursor.execute('PRAGMA table_info(bugs)')
        bugs_columns = cursor.fetchall()
        status_default = None
        for col in bugs_columns:
            if col[1] == 'status':
                status_default = col[4]
                break
        
        if status_default == '待处理' or status_default == "'待处理'":
            print("  ✅ bugs.status默认值正确")
            validation_results.append(True)
        else:
            print(f"  ❌ bugs.status默认值错误: {status_default}")
            validation_results.append(False)
        
        # 验证system_config表的updated_by字段类型
        cursor.execute('PRAGMA table_info(system_config)')
        config_columns = cursor.fetchall()
        updated_by_type = None
        for col in config_columns:
            if col[1] == 'updated_by':
                updated_by_type = col[2]
                break
        
        if updated_by_type == 'INTEGER':
            print("  ✅ system_config.updated_by类型正确")
            validation_results.append(True)
        else:
            print(f"  ❌ system_config.updated_by类型错误: {updated_by_type}")
            validation_results.append(False)
        
        # 验证notifications表的content字段约束
        cursor.execute('PRAGMA table_info(notifications)')
        notifications_columns = cursor.fetchall()
        content_not_null = None
        for col in notifications_columns:
            if col[1] == 'content':
                content_not_null = col[3]
                break
        
        if content_not_null:
            print("  ✅ notifications.content约束正确")
            validation_results.append(True)
        else:
            print("  ❌ notifications.content约束错误: 应为NOT NULL")
            validation_results.append(False)
        
        # 验证users表的必需字段
        cursor.execute('PRAGMA table_info(users)')
        users_columns = cursor.fetchall()
        user_fields = [col[1] for col in users_columns]
        
        required_user_fields = ['id', 'username', 'password', 'role', 'email', 'phone', 'gotify_app_token', 'gotify_user_id']
        print("\n📋 users表字段检查:")
        for field in required_user_fields:
            if field in user_fields:
                print(f"  ✅ {field}")
                validation_results.append(True)
            else:
                print(f"  ❌ {field} - 缺失")
                validation_results.append(False)
        
        conn.close()
        
        # 总结验证结果
        passed = sum(validation_results)
        total = len(validation_results)
        success_rate = (passed / total) * 100
        
        print(f"\n📊 验证结果: {passed}/{total} 项通过 ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("✅ SQLite数据库结构验证通过")
            return True
        else:
            print("❌ SQLite数据库结构验证失败")
            return False
        
    except Exception as e:
        print(f"❌ SQLite结构验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_postgres_structure():
    """验证PostgreSQL数据库结构"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        print("🔍 验证PostgreSQL数据库结构规范")
        print("=" * 60)
        
        validation_results = []
        
        # 验证必需的表是否存在
        expected_tables = ['users', 'bugs', 'bug_images', 'projects', 'system_config', 'user_notification_preferences', 'notifications']
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE '%_bak'
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("📋 表存在性检查:")
        for table in expected_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
                validation_results.append(True)
            else:
                print(f"  ❌ {table} - 缺失")
                validation_results.append(False)
        
        # 验证关键字段
        print("\n📋 关键字段验证:")
        
        # 验证bugs表的status字段默认值
        cursor.execute("""
            SELECT column_default 
            FROM information_schema.columns 
            WHERE table_name = 'bugs' AND column_name = 'status'
        """)
        result = cursor.fetchone()
        status_default = result[0] if result else None
        
        if status_default and '待处理' in status_default:
            print("  ✅ bugs.status默认值正确")
            validation_results.append(True)
        else:
            print(f"  ❌ bugs.status默认值错误: {status_default}")
            validation_results.append(False)
        
        # 验证system_config表的updated_by字段类型
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'system_config' AND column_name = 'updated_by'
        """)
        result = cursor.fetchone()
        updated_by_type = result[0] if result else None
        
        if updated_by_type == 'integer':
            print("  ✅ system_config.updated_by类型正确")
            validation_results.append(True)
        else:
            print(f"  ❌ system_config.updated_by类型错误: {updated_by_type}")
            validation_results.append(False)
        
        conn.close()
        
        # 总结验证结果
        passed = sum(validation_results)
        total = len(validation_results)
        success_rate = (passed / total) * 100
        
        print(f"\n📊 验证结果: {passed}/{total} 项通过 ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("✅ PostgreSQL数据库结构验证通过")
            return True
        else:
            print("❌ PostgreSQL数据库结构验证失败")
            return False
        
    except Exception as e:
        print(f"❌ PostgreSQL结构验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        print("🔧 数据库结构验证工具")
        print("=" * 80)
        
        sqlite_success = validate_sqlite_structure()
        print()
        
        try:
            postgres_success = validate_postgres_structure()
        except Exception as e:
            print(f"⚠️ PostgreSQL验证跳过: {e}")
            postgres_success = True  # 如果PostgreSQL不可用，不影响整体结果
        
        overall_success = sqlite_success and postgres_success
        
        print("\n" + "=" * 80)
        if overall_success:
            print("🎉 所有数据库结构验证通过")
        else:
            print("❌ 数据库结构验证失败")
        
        return overall_success
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        return False
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
