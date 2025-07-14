#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试清理管理器功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_cleanup_manager():
    """测试清理管理器的统计功能"""
    print("🧪 测试清理管理器功能...")
    
    try:
        from notification.cleanup_manager import cleanup_manager
        
        # 测试获取清理统计信息
        print("📊 获取清理统计信息...")
        stats = cleanup_manager.get_cleanup_stats()
        
        if 'error' in stats:
            print(f"❌ 获取统计信息失败: {stats['error']}")
            return
        
        print("✅ 获取统计信息成功")
        print(f"📈 总通知数: {stats.get('total_notifications', 0)}")
        print(f"👥 用户数: {stats.get('user_count', 0)}")
        print(f"📅 保留天数: {stats.get('retention_days', 0)}")
        print(f"🔢 每用户上限: {stats.get('max_per_user', 0)}")
        print(f"⏰ 过期记录数: {stats.get('expired_count', 0)}")
        print(f"📊 过量记录数: {stats.get('excess_count', 0)}")
        
        # 检查新增字段是否存在
        required_fields = ['expired_count', 'excess_count']
        missing_fields = []
        
        for field in required_fields:
            if field not in stats:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 缺少新增字段: {missing_fields}")
        else:
            print("✅ 所有新增字段都存在")
        
        # 测试自动清理配置检查
        print("\n🔧 测试自动清理配置...")
        is_auto_cleanup_enabled = cleanup_manager._is_auto_cleanup_enabled()
        print(f"🔄 自动清理状态: {'启用' if is_auto_cleanup_enabled else '禁用'}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_config_operations():
    """测试配置操作"""
    print("\n🧪 测试配置操作...")
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否存在自动清理配置
        query, params = adapt_sql("""
            SELECT config_value FROM system_config 
            WHERE config_key = %s
        """, ('notification_auto_cleanup_enabled',))
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if result:
            print(f"✅ 自动清理配置存在: {result[0]}")
        else:
            print("⚠️ 自动清理配置不存在，插入默认配置...")
            
            # 插入默认配置
            query, params = adapt_sql("""
                INSERT INTO system_config (config_key, config_value, description)
                VALUES (%s, %s, %s)
            """, ('notification_auto_cleanup_enabled', 'false', '自动清理功能开关'))
            
            cursor.execute(query, params)
            conn.commit()
            print("✅ 默认配置插入成功")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 配置操作失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试清理管理器功能...")
    test_config_operations()
    test_cleanup_manager()
    print("\n✨ 测试完成！")
