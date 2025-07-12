#!/usr/bin/env python3
# SQLite配置检查工具
# 检查当前SQLite配置是否最优，并提供优化建议

import sys
import os
import sqlite3
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_sqlite_config():
    """检查SQLite配置"""
    try:
        print("🔍 检查SQLite数据库配置...")
        
        # 导入配置
        from config import DB_TYPE, DATABASE_CONFIG
        
        print(f"📊 当前数据库类型: {DB_TYPE}")
        
        if DB_TYPE != 'sqlite':
            print(f"⚠️ 当前配置使用的是 {DB_TYPE}，不是SQLite")
            return False
        
        print(f"📋 SQLite配置: {DATABASE_CONFIG['sqlite']}")
        
        # 连接数据库
        db_path = DATABASE_CONFIG['sqlite']['database']
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        print(f"✅ 数据库文件存在: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔧 检查SQLite PRAGMA设置...")
        
        # 检查各种PRAGMA设置
        pragma_checks = [
            ("journal_mode", "WAL", "日志模式"),
            ("synchronous", "1", "同步模式"),
            ("cache_size", "-2000", "缓存大小"),
            ("temp_store", "2", "临时存储"),
            ("mmap_size", "268435456", "内存映射大小"),
            ("page_size", "4096", "页面大小")
        ]
        
        recommendations = []
        
        for pragma, recommended, description in pragma_checks:
            cursor.execute(f"PRAGMA {pragma}")
            current = str(cursor.fetchone()[0])
            
            if pragma == "synchronous":
                # 同步模式的值映射
                sync_map = {"0": "OFF", "1": "NORMAL", "2": "FULL"}
                current_desc = sync_map.get(current, current)
                recommended_desc = sync_map.get(recommended, recommended)
                status = "✅" if current == recommended else "⚠️"
                print(f"   {description}: {current_desc} {status}")
                if current != recommended:
                    recommendations.append(f"设置 {pragma} = {recommended_desc}")
            elif pragma == "temp_store":
                # 临时存储模式映射
                temp_map = {"0": "DEFAULT", "1": "FILE", "2": "MEMORY"}
                current_desc = temp_map.get(current, current)
                recommended_desc = temp_map.get(recommended, recommended)
                status = "✅" if current == recommended else "⚠️"
                print(f"   {description}: {current_desc} {status}")
                if current != recommended:
                    recommendations.append(f"设置 {pragma} = {recommended_desc}")
            else:
                status = "✅" if current == recommended else "⚠️"
                print(f"   {description}: {current} {status}")
                if current != recommended:
                    recommendations.append(f"设置 {pragma} = {recommended}")
        
        print("\n📋 检查索引...")
        
        # 检查重要索引是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        existing_indexes = [row[0] for row in cursor.fetchall()]
        
        required_indexes = [
            "idx_bugs_assigned_to",
            "idx_bugs_created_by", 
            "idx_bugs_status",
            "idx_bugs_created_at",
            "idx_users_username",
            "idx_users_role_en"
        ]
        
        missing_indexes = []
        for index in required_indexes:
            if index in existing_indexes:
                print(f"   ✅ {index}")
            else:
                print(f"   ❌ {index} (缺失)")
                missing_indexes.append(index)
        
        print("\n📊 数据库统计...")
        
        # 表统计
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   用户数量: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM bugs")
        bug_count = cursor.fetchone()[0]
        print(f"   问题数量: {bug_count}")
        
        # 文件大小
        file_size = os.path.getsize(db_path)
        print(f"   数据库大小: {file_size / 1024:.2f} KB")
        
        conn.close()
        
        # 生成优化建议
        print("\n💡 优化建议:")
        
        if recommendations:
            print("   配置优化:")
            for rec in recommendations:
                print(f"     • {rec}")
        
        if missing_indexes:
            print("   索引优化:")
            for index in missing_indexes:
                print(f"     • 创建索引: {index}")
        
        if not recommendations and not missing_indexes:
            print("   ✅ 当前配置已优化，无需调整")
        else:
            print(f"\n🔧 运行以下命令进行优化:")
            print(f"   python database_tools/sqlite_optimizer.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入配置失败: {e}")
        print("请确保在项目根目录运行此脚本")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        traceback.print_exc()
        return False

def check_db_factory_config():
    """检查db_factory.py中的SQLite配置"""
    try:
        print("\n🔧 检查db_factory.py中的SQLite配置...")
        
        from db_factory import get_db_connection
        
        # 测试连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查连接配置
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA busy_timeout")
        busy_timeout = cursor.fetchone()[0]
        
        print(f"   日志模式: {journal_mode}")
        print(f"   锁等待时间: {busy_timeout} ms")
        
        # 检查row_factory
        if hasattr(conn, 'row_factory') and conn.row_factory == sqlite3.Row:
            print("   ✅ Row factory已启用（字典式访问）")
        else:
            print("   ⚠️ Row factory未启用")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ db_factory配置检查失败: {e}")
        return False

def check_sql_adapter():
    """检查sql_adapter.py的SQLite适配"""
    try:
        print("\n🔧 检查sql_adapter.py的SQLite适配...")
        
        from sql_adapter import adapt_sql
        
        # 测试常见的SQL适配
        test_cases = [
            ("SELECT * FROM users WHERE id = %s", ["PostgreSQL占位符转换"]),
            ("SELECT NOW()", ["时间函数适配"]),
            ("SELECT * FROM bugs WHERE title ILIKE %s", ["大小写不敏感搜索"]),
            ("SELECT id::text FROM users", ["类型转换处理"])
        ]
        
        all_passed = True
        for sql, description in test_cases:
            try:
                adapted_sql, adapted_params = adapt_sql(sql, [1])
                print(f"   ✅ {description[0]}")
                print(f"      原始: {sql}")
                print(f"      适配: {adapted_sql}")
            except Exception as e:
                print(f"   ❌ {description[0]}: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ sql_adapter检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 SQLite配置检查工具")
    print("=" * 50)
    
    # 1. 检查基本配置
    config_ok = check_sqlite_config()
    
    # 2. 检查db_factory配置
    factory_ok = check_db_factory_config()
    
    # 3. 检查SQL适配器
    adapter_ok = check_sql_adapter()
    
    print("\n" + "=" * 50)
    print("📊 检查结果总结:")
    print(f"   基本配置: {'✅ 正常' if config_ok else '❌ 有问题'}")
    print(f"   连接工厂: {'✅ 正常' if factory_ok else '❌ 有问题'}")
    print(f"   SQL适配器: {'✅ 正常' if adapter_ok else '❌ 有问题'}")
    
    if config_ok and factory_ok and adapter_ok:
        print("\n🎉 SQLite配置检查完成，系统配置正常!")
    else:
        print("\n⚠️ 发现配置问题，请根据上述建议进行调整")

if __name__ == '__main__':
    main()
