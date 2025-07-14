#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动清理配置功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_auto_cleanup_config():
    """测试自动清理配置的保存和读取"""
    print("🧪 测试自动清理配置功能...")
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 测试1: 启用自动清理
        print("\n📝 测试1: 启用自动清理...")
        
        # 更新配置
        query, params = adapt_sql("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = %s
        """, ('true', 'notification_auto_cleanup_enabled'))
        
        cursor.execute(query, params)
        conn.commit()
        
        # 验证配置
        from notification.cleanup_manager import cleanup_manager
        is_enabled = cleanup_manager._is_auto_cleanup_enabled()
        print(f"✅ 自动清理状态: {'启用' if is_enabled else '禁用'}")
        
        if is_enabled:
            print("✅ 启用自动清理测试通过")
        else:
            print("❌ 启用自动清理测试失败")
        
        # 测试2: 禁用自动清理
        print("\n📝 测试2: 禁用自动清理...")
        
        # 更新配置
        query, params = adapt_sql("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = %s
        """, ('false', 'notification_auto_cleanup_enabled'))
        
        cursor.execute(query, params)
        conn.commit()
        
        # 验证配置
        is_enabled = cleanup_manager._is_auto_cleanup_enabled()
        print(f"✅ 自动清理状态: {'启用' if is_enabled else '禁用'}")
        
        if not is_enabled:
            print("✅ 禁用自动清理测试通过")
        else:
            print("❌ 禁用自动清理测试失败")
        
        # 测试3: 测试配置API格式
        print("\n📝 测试3: 测试配置API格式...")
        
        # 模拟API返回的配置格式
        query, params = adapt_sql("""
            SELECT config_key, config_value FROM system_config 
            WHERE config_key LIKE %s
        """, ('notification_%',))
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        config_dict = {}
        for config in configs:
            config_dict[config[0]] = config[1]
        
        # 构建server配置
        server_config = {
            'enabled': config_dict.get('notification_server_enabled', 'true') == 'true',
            'retention_days': int(config_dict.get('notification_retention_days', '30')),
            'auto_cleanup_enabled': config_dict.get('notification_auto_cleanup_enabled', 'false') == 'true'
        }
        
        print(f"📊 Server配置: {server_config}")
        
        if 'auto_cleanup_enabled' in server_config:
            print("✅ auto_cleanup_enabled字段存在于配置中")
        else:
            print("❌ auto_cleanup_enabled字段缺失")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_cleanup_stats_with_data():
    """测试有数据时的清理统计"""
    print("\n🧪 测试清理统计功能...")
    
    try:
        from notification.cleanup_manager import cleanup_manager
        from datetime import datetime, timedelta
        
        # 获取统计信息
        stats = cleanup_manager.get_cleanup_stats()
        
        if 'error' in stats:
            print(f"❌ 获取统计失败: {stats['error']}")
            return
        
        print("📊 当前统计信息:")
        print(f"  总通知数: {stats.get('total_notifications', 0)}")
        print(f"  用户数: {stats.get('user_count', 0)}")
        print(f"  保留天数: {stats.get('retention_days', 0)}")
        print(f"  每用户上限: {stats.get('max_per_user', 0)}")
        print(f"  过期记录数: {stats.get('expired_count', 0)}")
        print(f"  过量记录数: {stats.get('excess_count', 0)}")
        
        # 验证新字段
        if 'expired_count' in stats and 'excess_count' in stats:
            print("✅ 新增统计字段正常")
        else:
            print("❌ 新增统计字段缺失")
        
        # 验证数据类型
        if isinstance(stats.get('expired_count'), int) and isinstance(stats.get('excess_count'), int):
            print("✅ 统计字段数据类型正确")
        else:
            print("❌ 统计字段数据类型错误")
        
    except Exception as e:
        print(f"❌ 统计测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试自动清理配置功能...")
    test_auto_cleanup_config()
    test_cleanup_stats_with_data()
    print("\n✨ 测试完成！")
