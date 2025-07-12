#!/usr/bin/env python3
# SQLite数据库优化工具
# 专门处理SQLite数据库的性能优化、维护和问题修复

import sys
import os
import sqlite3
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def optimize_sqlite_database():
    """优化SQLite数据库性能"""
    try:
        print("🔧 开始优化SQLite数据库...")
        
        # 连接数据库
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 当前数据库状态:")
        
        # 检查数据库大小
        file_size = os.path.getsize(db_path)
        print(f"   数据库文件大小: {file_size / 1024:.2f} KB")
        
        # 检查页面大小
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        print(f"   页面大小: {page_size} bytes")
        
        # 检查缓存大小
        cursor.execute("PRAGMA cache_size")
        cache_size = cursor.fetchone()[0]
        print(f"   缓存大小: {cache_size} pages")
        
        # 检查日志模式
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        print(f"   日志模式: {journal_mode}")
        
        print("\n🚀 应用性能优化...")
        
        # 1. 设置WAL模式（如果还不是）
        if journal_mode.upper() != 'WAL':
            cursor.execute("PRAGMA journal_mode=WAL")
            print("✅ 启用WAL模式（提升并发性能）")
        else:
            print("✅ WAL模式已启用")
        
        # 2. 优化缓存大小
        cursor.execute("PRAGMA cache_size = 10000")  # 约40MB缓存
        print("✅ 优化缓存大小为10000页")
        
        # 3. 设置同步模式
        cursor.execute("PRAGMA synchronous = NORMAL")
        print("✅ 设置同步模式为NORMAL（平衡性能和安全）")
        
        # 4. 设置临时存储
        cursor.execute("PRAGMA temp_store = MEMORY")
        print("✅ 设置临时存储为内存模式")
        
        # 5. 设置锁等待时间
        cursor.execute("PRAGMA busy_timeout = 10000")  # 10秒
        print("✅ 设置锁等待时间为10秒")
        
        print("\n📋 创建索引优化...")
        
        # 创建常用查询的索引
        indexes = [
            ("idx_bugs_assigned_to", "CREATE INDEX IF NOT EXISTS idx_bugs_assigned_to ON bugs(assigned_to)"),
            ("idx_bugs_created_by", "CREATE INDEX IF NOT EXISTS idx_bugs_created_by ON bugs(created_by)"),
            ("idx_bugs_status", "CREATE INDEX IF NOT EXISTS idx_bugs_status ON bugs(status)"),
            ("idx_bugs_created_at", "CREATE INDEX IF NOT EXISTS idx_bugs_created_at ON bugs(created_at)"),
            ("idx_users_username", "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"),
            ("idx_users_role_en", "CREATE INDEX IF NOT EXISTS idx_users_role_en ON users(role_en)"),
            ("idx_users_team", "CREATE INDEX IF NOT EXISTS idx_users_team ON users(team)")
        ]
        
        for index_name, index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ 创建索引: {index_name}")
            except sqlite3.Error as e:
                print(f"⚠️ 索引 {index_name} 可能已存在: {e}")
        
        print("\n🧹 数据库清理...")
        
        # 分析表统计信息
        cursor.execute("ANALYZE")
        print("✅ 更新表统计信息")
        
        # 清理数据库（回收空间）
        cursor.execute("VACUUM")
        print("✅ 清理数据库文件")
        
        # 提交更改
        conn.commit()
        
        # 检查优化后的状态
        print("\n📊 优化后状态:")
        new_file_size = os.path.getsize(db_path)
        print(f"   数据库文件大小: {new_file_size / 1024:.2f} KB")
        
        cursor.execute("PRAGMA cache_size")
        new_cache_size = cursor.fetchone()[0]
        print(f"   缓存大小: {new_cache_size} pages")
        
        cursor.execute("PRAGMA journal_mode")
        new_journal_mode = cursor.fetchone()[0]
        print(f"   日志模式: {new_journal_mode}")
        
        conn.close()
        
        print(f"\n✅ SQLite数据库优化完成!")
        print(f"   文件大小变化: {file_size / 1024:.2f} KB → {new_file_size / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 优化失败: {e}")
        traceback.print_exc()
        return False

def check_sqlite_integrity():
    """检查SQLite数据库完整性"""
    try:
        print("🔍 检查SQLite数据库完整性...")
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 完整性检查
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        if result == "ok":
            print("✅ 数据库完整性检查通过")
        else:
            print(f"❌ 数据库完整性问题: {result}")
            return False
        
        # 外键检查
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        
        if not fk_errors:
            print("✅ 外键约束检查通过")
        else:
            print(f"❌ 发现外键约束问题: {len(fk_errors)} 个")
            for error in fk_errors:
                print(f"   {error}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 完整性检查失败: {e}")
        return False

def backup_sqlite_database():
    """备份SQLite数据库"""
    try:
        print("💾 备份SQLite数据库...")
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"❌ 源数据库文件不存在: {db_path}")
            return False
        
        # 创建备份文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(os.path.dirname(db_path), f'rebugtracker_backup_{timestamp}.db')
        
        # 使用SQLite的备份API
        source_conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        source_conn.backup(backup_conn)
        
        source_conn.close()
        backup_conn.close()
        
        backup_size = os.path.getsize(backup_path)
        print(f"✅ 备份完成: {backup_path}")
        print(f"   备份文件大小: {backup_size / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False

def sqlite_maintenance():
    """SQLite数据库维护"""
    print("🛠️ SQLite数据库维护工具")
    print("=" * 50)
    
    # 1. 完整性检查
    integrity_ok = check_sqlite_integrity()
    
    # 2. 备份数据库
    backup_ok = backup_sqlite_database()
    
    # 3. 优化数据库
    if integrity_ok:
        optimize_ok = optimize_sqlite_database()
    else:
        print("⚠️ 由于完整性问题，跳过优化步骤")
        optimize_ok = False
    
    print("\n" + "=" * 50)
    print("📊 维护结果总结:")
    print(f"   完整性检查: {'✅ 通过' if integrity_ok else '❌ 失败'}")
    print(f"   数据库备份: {'✅ 成功' if backup_ok else '❌ 失败'}")
    print(f"   性能优化: {'✅ 完成' if optimize_ok else '❌ 跳过'}")
    
    if integrity_ok and backup_ok and optimize_ok:
        print("\n🎉 SQLite数据库维护完成!")
    else:
        print("\n⚠️ 部分维护任务未完成，请检查错误信息")

if __name__ == '__main__':
    sqlite_maintenance()
