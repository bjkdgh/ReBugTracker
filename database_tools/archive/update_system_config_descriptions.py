#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新system_config表的描述信息
为所有配置项添加详细的中文描述
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection
from sql_adapter import adapt_sql

def update_system_config_descriptions():
    """更新system_config表的描述信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔧 开始更新system_config表的描述信息...")
        
        # 定义所有配置项的描述信息（根据实际数据库中的配置项名称）
        config_descriptions = {
            # 服务器通知设置
            'notification_enabled': '服务器通知功能总开关，控制整个系统的通知功能是否启用',
            'notification_server_enabled': '服务器级别通知开关，控制服务器端通知处理功能',
            'notification_retention_days': '通知记录保留天数，超过此天数的通知记录将被自动清理',

            # 应用内通知设置
            'notification_inapp_enabled': '应用内通知功能开关，控制是否在系统内显示通知消息',
            'notification_max_per_user': '每个用户最大通知数量限制，超过此数量将删除最旧的通知',

            # 邮件通知设置
            'notification_email_enabled': '邮件通知功能开关，控制是否发送邮件通知',
            'notification_email_smtp_server': 'SMTP邮件服务器地址，用于发送邮件通知',
            'notification_email_smtp_port': 'SMTP邮件服务器端口号，通常为25、465或587',
            'notification_email_smtp_username': 'SMTP邮件服务器登录用户名',
            'notification_email_smtp_password': 'SMTP邮件服务器登录密码',
            'notification_email_from_email': '发送邮件的发件人邮箱地址',
            'notification_email_from_name': '发送邮件的发件人显示名称',
            'notification_email_use_tls': 'SMTP连接是否使用TLS加密，提高邮件传输安全性',

            # Gotify通知设置
            'notification_gotify_enabled': 'Gotify推送通知功能开关，控制是否发送Gotify通知',
            'notification_gotify_server_url': 'Gotify服务器地址，用于发送推送通知',
            'notification_gotify_app_token': 'Gotify应用令牌，用于身份验证和发送通知',
            'notification_gotify_default_priority': 'Gotify通知默认优先级，数值越高优先级越高（1-10）',

            # 通知流程规则
            'notification_flow_bug_created': '问题创建时是否发送通知，通知相关负责人新问题已提交',
            'notification_flow_bug_assigned': '问题分配时是否发送通知，通知被分配人有新任务',
            'notification_flow_bug_status_changed': '问题状态变更时是否发送通知，通知相关人员状态更新',
            'notification_flow_bug_resolved': '问题解决时是否发送通知，通知提交人问题已解决',
            'notification_flow_bug_closed': '问题关闭时是否发送通知，通知相关人员问题已关闭',

            # 全局开关（兼容旧配置）
            'email_global_enabled': '全局邮件通知开关，控制整个系统的邮件通知功能',
            'gotify_global_enabled': '全局Gotify通知开关，控制整个系统的Gotify通知功能'
        }
        
        # 更新每个配置项的描述
        updated_count = 0
        for config_key, description in config_descriptions.items():
            # 检查配置项是否存在
            query, params = adapt_sql("SELECT COUNT(*) FROM system_config WHERE config_key = %s", (config_key,))
            cursor.execute(query, params)
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                # 更新描述
                query, params = adapt_sql("""
                    UPDATE system_config 
                    SET description = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE config_key = %s
                """, (description, config_key))
                cursor.execute(query, params)
                updated_count += 1
                print(f"  ✅ 更新配置项: {config_key}")
            else:
                print(f"  ⚠️  配置项不存在: {config_key}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ 成功更新了 {updated_count} 个配置项的描述信息！")
        return True
        
    except Exception as e:
        print(f"❌ 更新system_config描述失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def show_current_config():
    """显示当前的配置信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n🔍 当前system_config表数据:")
        print("-" * 80)
        
        query, params = adapt_sql("""
            SELECT config_key, config_value, description, updated_at 
            FROM system_config 
            ORDER BY config_key
        """, ())
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        for row in rows:
            config_key, config_value, description, updated_at = row
            print(f"配置项: {config_key}")
            print(f"  值: {config_value}")
            print(f"  描述: {description or '无描述'}")
            print(f"  更新时间: {updated_at}")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查询配置信息失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker System Config 描述更新工具")
    print("=" * 50)
    
    # 显示当前配置
    show_current_config()
    
    # 更新描述信息
    success = update_system_config_descriptions()
    
    if success:
        print("\n🎉 描述更新完成！")
        # 再次显示更新后的配置
        show_current_config()
    else:
        print("\n❌ 描述更新失败！")
