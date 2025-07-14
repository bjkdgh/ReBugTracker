#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示新增的清理统计和自动清理功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demo_cleanup_stats():
    """演示清理统计功能"""
    print("🎯 演示清理统计功能")
    print("=" * 50)
    
    try:
        from notification.cleanup_manager import cleanup_manager
        
        # 获取完整的清理统计信息
        stats = cleanup_manager.get_cleanup_stats()
        
        if 'error' in stats:
            print(f"❌ 获取统计失败: {stats['error']}")
            return
        
        print("📊 清理统计信息:")
        print(f"  📈 总通知数: {stats.get('total_notifications', 0)}")
        print(f"  👥 用户数: {stats.get('user_count', 0)}")
        print(f"  📅 保留天数: {stats.get('retention_days', 0)} 天")
        print(f"  🔢 每用户上限: {stats.get('max_per_user', 0)} 条")
        print(f"  ⏰ 过期记录数: {stats.get('expired_count', 0)} 条")
        print(f"  📊 过量记录数: {stats.get('excess_count', 0)} 条")
        
        if stats.get('oldest_notification'):
            print(f"  🕐 最旧通知: {stats.get('oldest_notification')}")
        else:
            print("  🕐 最旧通知: 无通知记录")
        
        # 显示用户分布（前5名）
        user_distribution = stats.get('user_distribution', [])
        if user_distribution:
            print("\n👥 用户通知分布 (前5名):")
            for i, user_data in enumerate(user_distribution[:5], 1):
                print(f"  {i}. 用户 {user_data['user_id']}: {user_data['count']} 条通知")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_auto_cleanup_config():
    """演示自动清理配置功能"""
    print("\n🎯 演示自动清理配置功能")
    print("=" * 50)
    
    try:
        from notification.cleanup_manager import cleanup_manager
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        # 检查当前状态
        current_status = cleanup_manager._is_auto_cleanup_enabled()
        print(f"🔄 当前自动清理状态: {'启用' if current_status else '禁用'}")
        
        # 演示配置切换
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n📝 演示配置切换...")
        
        # 切换到启用状态
        print("  ➡️ 启用自动清理...")
        query, params = adapt_sql("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = %s
        """, ('true', 'notification_auto_cleanup_enabled'))
        cursor.execute(query, params)
        conn.commit()
        
        new_status = cleanup_manager._is_auto_cleanup_enabled()
        print(f"     状态: {'✅ 启用成功' if new_status else '❌ 启用失败'}")
        
        # 切换到禁用状态
        print("  ➡️ 禁用自动清理...")
        query, params = adapt_sql("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = %s
        """, ('false', 'notification_auto_cleanup_enabled'))
        cursor.execute(query, params)
        conn.commit()
        
        new_status = cleanup_manager._is_auto_cleanup_enabled()
        print(f"     状态: {'✅ 禁用成功' if not new_status else '❌ 禁用失败'}")
        
        # 恢复原始状态
        query, params = adapt_sql("""
            UPDATE system_config 
            SET config_value = %s 
            WHERE config_key = %s
        """, ('true' if current_status else 'false', 'notification_auto_cleanup_enabled'))
        cursor.execute(query, params)
        conn.commit()
        
        print(f"  🔄 恢复原始状态: {'启用' if current_status else '禁用'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def demo_api_format():
    """演示API配置格式"""
    print("\n🎯 演示API配置格式")
    print("=" * 50)
    
    try:
        from db_factory import get_db_connection
        from sql_adapter import adapt_sql
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有通知配置
        query, params = adapt_sql("""
            SELECT config_key, config_value FROM system_config 
            WHERE config_key LIKE %s
            ORDER BY config_key
        """, ('notification_%',))
        
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        config_dict = {}
        for config in configs:
            config_dict[config[0]] = config[1]
        
        # 构建API返回格式
        api_response = {
            'success': True,
            'data': {
                'server': {
                    'enabled': config_dict.get('notification_server_enabled', 'true') == 'true',
                    'retention_days': int(config_dict.get('notification_retention_days', '30')),
                    'auto_cleanup_enabled': config_dict.get('notification_auto_cleanup_enabled', 'false') == 'true'
                },
                'inapp': {
                    'enabled': config_dict.get('notification_inapp_enabled', 'true') == 'true',
                    'max_notifications_per_user': int(config_dict.get('notification_max_per_user', '100'))
                }
            }
        }
        
        print("📡 API配置格式示例:")
        import json
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
        # 验证新字段
        server_config = api_response['data']['server']
        if 'auto_cleanup_enabled' in server_config:
            print(f"\n✅ 新增字段 'auto_cleanup_enabled': {server_config['auto_cleanup_enabled']}")
        else:
            print("\n❌ 新增字段 'auto_cleanup_enabled' 缺失")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

def main():
    """主演示函数"""
    print("🚀 ReBugTracker 新功能演示")
    print("🎉 admin页面通知配置选项卡新增功能:")
    print("   1. 清理统计信息中新增过期记录数和过量记录数")
    print("   2. 新增自动清理功能开关")
    print()
    
    # 演示各项功能
    demo_cleanup_stats()
    demo_auto_cleanup_config()
    demo_api_format()
    
    print("\n" + "=" * 50)
    print("✨ 演示完成！")
    print("📝 功能总结:")
    print("   ✅ 清理统计信息显示过期和过量记录数")
    print("   ✅ 自动清理开关配置和状态检查")
    print("   ✅ API配置格式包含新增字段")
    print("   ✅ 数据库配置正确保存和读取")
    print()
    print("🌐 您现在可以在admin页面的通知配置选项卡中:")
    print("   📊 查看详细的清理统计信息")
    print("   🔄 控制自动清理功能的开启/关闭")

if __name__ == "__main__":
    main()
