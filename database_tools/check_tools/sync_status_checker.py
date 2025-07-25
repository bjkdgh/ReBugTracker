#!/usr/bin/env python3
"""
数据库同步状态检查工具
检查PostgreSQL和SQLite之间的数据同步状态
"""

import os
import sys
import sqlite3
import traceback
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psycopg2
    from psycopg2.extras import DictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# PostgreSQL配置
POSTGRES_CONFIG = {
    'dbname': 'rebugtracker',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5',
    'port': 5432
}

def check_sqlite_status():
    """检查SQLite数据库状态"""
    print("🔍 检查SQLite数据库...")
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'rebugtracker.db')
    
    if not os.path.exists(db_path):
        print(f"❌ SQLite数据库文件不存在: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表统计
        tables = ['users', 'bugs', 'projects', 'notifications', 'system_config', 'user_notification_preferences', 'bug_images']
        stats = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        # 获取最新数据时间
        latest_times = {}
        try:
            cursor.execute("SELECT MAX(created_at) FROM bugs")
            latest_times['bugs'] = cursor.fetchone()[0]
        except:
            latest_times['bugs'] = None
            
        try:
            cursor.execute("SELECT MAX(created_at) FROM notifications")
            latest_times['notifications'] = cursor.fetchone()[0]
        except:
            latest_times['notifications'] = None
        
        conn.close()
        
        print("✅ SQLite连接成功")
        for table, count in stats.items():
            print(f"   {table}: {count} 条记录")
        
        return {'stats': stats, 'latest_times': latest_times}
        
    except Exception as e:
        print(f"❌ SQLite连接失败: {e}")
        return None

def check_postgres_status():
    """检查PostgreSQL数据库状态"""
    print("\n🔍 检查PostgreSQL数据库...")
    
    if not PSYCOPG2_AVAILABLE:
        print("❌ psycopg2未安装，无法连接PostgreSQL")
        return None
    
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        # 获取表统计
        tables = ['users', 'bugs', 'projects', 'notifications', 'system_config', 'user_notification_preferences', 'bug_images']
        stats = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        # 获取最新数据时间
        latest_times = {}
        try:
            cursor.execute("SELECT MAX(created_at) FROM bugs")
            latest_times['bugs'] = cursor.fetchone()[0]
        except:
            latest_times['bugs'] = None
            
        try:
            cursor.execute("SELECT MAX(created_at) FROM notifications")
            latest_times['notifications'] = cursor.fetchone()[0]
        except:
            latest_times['notifications'] = None
        
        conn.close()
        
        print("✅ PostgreSQL连接成功")
        for table, count in stats.items():
            print(f"   {table}: {count} 条记录")
        
        return {'stats': stats, 'latest_times': latest_times}
        
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return None

def compare_sync_status(sqlite_data, postgres_data):
    """对比同步状态"""
    print("\n📊 数据库同步状态对比:")
    print("=" * 60)
    
    if not sqlite_data or not postgres_data:
        if sqlite_data and not postgres_data:
            print("⚠️ 仅SQLite可用，PostgreSQL不可用")
            print("\n📋 SQLite数据状态:")
            for table, count in sqlite_data['stats'].items():
                print(f"   {table}: {count} 条记录")
        elif postgres_data and not sqlite_data:
            print("⚠️ 仅PostgreSQL可用，SQLite不可用")
            print("\n📋 PostgreSQL数据状态:")
            for table, count in postgres_data['stats'].items():
                print(f"   {table}: {count} 条记录")
        else:
            print("❌ 两个数据库都不可用")
        return
    
    # 数据量对比
    print("📈 数据量对比:")
    all_tables = set(sqlite_data['stats'].keys()) | set(postgres_data['stats'].keys())
    
    sync_issues = []
    for table in sorted(all_tables):
        sqlite_count = sqlite_data['stats'].get(table, 0)
        postgres_count = postgres_data['stats'].get(table, 0)
        
        if sqlite_count == postgres_count:
            print(f"   ✅ {table}: {sqlite_count} (同步)")
        else:
            print(f"   ⚠️ {table}: SQLite({sqlite_count}) ≠ PostgreSQL({postgres_count})")
            sync_issues.append(table)
    
    # 时间对比
    print("\n🕒 最新数据时间对比:")
    for data_type in ['bugs', 'notifications']:
        sqlite_time = sqlite_data['latest_times'].get(data_type)
        postgres_time = postgres_data['latest_times'].get(data_type)
        
        if sqlite_time == postgres_time:
            print(f"   ✅ {data_type}: {sqlite_time} (同步)")
        else:
            print(f"   ⚠️ {data_type}: SQLite({sqlite_time}) ≠ PostgreSQL({postgres_time})")
    
    # 同步建议
    print("\n💡 同步建议:")
    if not sync_issues:
        print("   🎉 数据完全同步，无需额外操作")
    else:
        print(f"   ⚠️ 发现 {len(sync_issues)} 个表存在同步差异: {', '.join(sync_issues)}")
        print("   📝 建议运行以下工具:")
        print("      - full_sync_postgres_to_sqlite.py (完整同步)")
        print("      - sync_postgres_to_sqlite_fixed.py (修复版同步)")

def main():
    """主函数"""
    print("🚀 ReBugTracker 数据库同步状态检查")
    print("=" * 60)
    print(f"🕒 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查两个数据库
    sqlite_data = check_sqlite_status()
    postgres_data = check_postgres_status()
    
    # 对比同步状态
    compare_sync_status(sqlite_data, postgres_data)
    
    print("\n✅ 同步状态检查完成")

if __name__ == "__main__":
    main()
