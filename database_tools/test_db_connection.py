#!/usr/bin/env python3
# 数据库连接测试工具
# 用于验证数据库配置是否正确，能否成功建立数据库连接

import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_connection():
    """测试数据库连接"""
    try:
        print("🔗 测试数据库连接...")
        
        # 导入配置和数据库工厂
        from config import DB_TYPE, DATABASE_CONFIG
        from db_factory import get_db_connection
        
        print(f"📊 当前数据库类型: {DB_TYPE}")
        print(f"📋 数据库配置: {DATABASE_CONFIG}")
        
        # 获取数据库连接
        conn = get_db_connection()
        
        if conn:
            print("✅ 数据库连接成功!")
            
            # 执行简单查询测试
            if DB_TYPE == 'postgres':
                from psycopg2.extras import DictCursor
                cursor = conn.cursor(cursor_factory=DictCursor)
            else:
                cursor = conn.cursor()
            
            # 测试查询users表
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"📊 用户表记录数: {user_count}")
            except Exception as e:
                print(f"⚠️ 查询用户表失败: {e}")
            
            # 测试查询bugs表
            try:
                cursor.execute("SELECT COUNT(*) FROM bugs")
                bug_count = cursor.fetchone()[0]
                print(f"📊 问题表记录数: {bug_count}")
            except Exception as e:
                print(f"⚠️ 查询问题表失败: {e}")

            # 检查通知系统表
            notification_tables = ['system_config', 'user_notification_preferences', 'notifications']
            for table in notification_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"📊 {table}表记录数: {count}")
                except Exception as e:
                    print(f"⚠️ {table}表不存在或查询失败: {e}")

            # 检查用户表扩展字段
            try:
                if DB_TYPE == 'postgres':
                    cursor.execute("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'users' AND column_name IN ('email', 'phone')
                    """)
                else:
                    cursor.execute("PRAGMA table_info(users)")
                    columns = [col[1] for col in cursor.fetchall()]
                    extended_fields = [field for field in ['email', 'phone'] if field in columns]
                    print(f"📧 用户表扩展字段: {extended_fields}")

                if DB_TYPE == 'postgres':
                    extended_fields = [row[0] for row in cursor.fetchall()]
                    print(f"📧 用户表扩展字段: {extended_fields}")
            except Exception as e:
                print(f"⚠️ 检查用户表扩展字段失败: {e}")

            # 关闭连接
            conn.close()
            print("🔒 数据库连接已关闭")
            return True
        else:
            print("❌ 无法获取数据库连接")
            return False
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保在项目根目录运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        traceback.print_exc()
        return False

def test_specific_database():
    """测试特定数据库类型的连接"""
    try:
        # 测试PostgreSQL连接
        print("\n🐘 测试PostgreSQL连接...")
        try:
            import psycopg2
            from psycopg2.extras import DictCursor
            
            pg_config = {
                'dbname': 'postgres',
                'user': 'postgres',
                'password': '$RFV5tgb',
                'host': '192.168.1.5'
            }
            
            pg_conn = psycopg2.connect(**pg_config)
            print("✅ PostgreSQL连接成功")
            pg_conn.close()
        except Exception as e:
            print(f"❌ PostgreSQL连接失败: {e}")
        
        # 测试SQLite连接
        print("\n🗃️ 测试SQLite连接...")
        try:
            import sqlite3
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
            
            if os.path.exists(db_path):
                sqlite_conn = sqlite3.connect(db_path)
                print(f"✅ SQLite连接成功: {db_path}")
                sqlite_conn.close()
            else:
                print(f"❌ SQLite文件不存在: {db_path}")
        except Exception as e:
            print(f"❌ SQLite连接失败: {e}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 数据库连接测试工具")
    print("=" * 40)
    
    # 测试当前配置的数据库
    success = test_database_connection()
    
    # 测试所有可用的数据库类型
    test_specific_database()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ 数据库连接测试完成")
    else:
        print("❌ 数据库连接测试失败")
