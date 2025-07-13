#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReBugTracker 综合数据库状态检查工具
检查数据库结构、数据完整性、通知系统状态等
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_factory import get_db_connection, DB_TYPE
from sql_adapter import adapt_sql

def check_database_structure():
    """检查数据库结构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"🗄️ 检查{DB_TYPE.upper()}数据库结构")
        print("=" * 50)
        
        # 检查核心表
        core_tables = ['users', 'bugs']
        notification_tables = ['system_config', 'user_notification_preferences', 'notifications']
        all_tables = core_tables + notification_tables
        
        existing_tables = []
        missing_tables = []
        
        for table in all_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                existing_tables.append((table, count))
                status = "✅ 存在" if table in core_tables else "🔔 存在"
                print(f"  {table}: {status} ({count} 条记录)")
            except Exception as e:
                missing_tables.append(table)
                status = "❌ 缺失" if table in core_tables else "⚠️ 缺失"
                print(f"  {table}: {status}")
        
        # 检查用户表字段
        print("\n📧 检查用户表扩展字段:")
        try:
            if DB_TYPE == 'postgres':
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name IN ('email', 'phone')
                    ORDER BY column_name
                """)
                extended_fields = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]
                extended_fields = [field for field in ['email', 'phone'] if field in columns]
            
            for field in ['email', 'phone']:
                status = "✅ 存在" if field in extended_fields else "❌ 缺失"
                print(f"  {field}: {status}")
        
        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
        
        conn.close()
        
        return {
            'existing_tables': existing_tables,
            'missing_tables': missing_tables,
            'extended_fields': extended_fields if 'extended_fields' in locals() else []
        }
        
    except Exception as e:
        print(f"❌ 检查数据库结构失败: {e}")
        return None

def check_notification_system():
    """检查通知系统状态"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n🔔 检查通知系统状态")
        print("=" * 50)
        
        # 检查系统配置
        try:
            cursor.execute("SELECT config_key, config_value FROM system_config WHERE config_key = 'notification_enabled'")
            result = cursor.fetchone()
            if result:
                enabled = result[1].lower() == 'true'
                status = "✅ 启用" if enabled else "❌ 禁用"
                print(f"  服务器通知开关: {status}")
            else:
                print("  服务器通知开关: ⚠️ 未配置")
        except Exception as e:
            print(f"  服务器通知开关: ❌ 检查失败 ({e})")
        
        # 检查用户通知偏好
        try:
            cursor.execute("SELECT COUNT(*) FROM user_notification_preferences")
            pref_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if pref_count == user_count:
                print(f"  用户通知偏好: ✅ 完整 ({pref_count}/{user_count})")
            else:
                print(f"  用户通知偏好: ⚠️ 不完整 ({pref_count}/{user_count})")
        except Exception as e:
            print(f"  用户通知偏好: ❌ 检查失败 ({e})")
        
        # 检查应用内通知
        try:
            cursor.execute("SELECT COUNT(*) FROM notifications")
            notif_count = cursor.fetchone()[0]

            # 根据数据库类型使用不同的查询
            if DB_TYPE == 'postgres':
                cursor.execute("SELECT COUNT(*) FROM notifications WHERE read_status = false")
            else:
                cursor.execute("SELECT COUNT(*) FROM notifications WHERE read_status = 0")
            unread_count = cursor.fetchone()[0]

            print(f"  应用内通知: ✅ 正常 (总计: {notif_count}, 未读: {unread_count})")
        except Exception as e:
            print(f"  应用内通知: ❌ 检查失败 ({e})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查通知系统失败: {e}")

def check_user_roles():
    """检查用户角色分布"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n👥 检查用户角色分布")
        print("=" * 50)
        
        cursor.execute("SELECT role_en, COUNT(*) FROM users GROUP BY role_en ORDER BY COUNT(*) DESC")
        roles = cursor.fetchall()
        
        role_names = {
            'gly': '管理员',
            'fzr': '负责人', 
            'ssz': '实施组',
            'zncy': '组内成员'
        }
        
        total_users = sum(count for _, count in roles)
        
        for role, count in roles:
            role_name = role_names.get(role, role)
            percentage = (count / total_users * 100) if total_users > 0 else 0
            print(f"  {role_name}({role}): {count} 人 ({percentage:.1f}%)")
        
        print(f"  总用户数: {total_users}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查用户角色失败: {e}")

def check_data_integrity():
    """检查数据完整性"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n🔍 检查数据完整性")
        print("=" * 50)
        
        # 检查孤儿数据
        try:
            # 检查bugs表中的created_by是否都存在于users表
            cursor.execute("""
                SELECT COUNT(*) FROM bugs 
                WHERE created_by IS NOT NULL 
                AND created_by NOT IN (SELECT id FROM users)
            """)
            orphan_bugs = cursor.fetchone()[0]
            
            if orphan_bugs == 0:
                print("  问题创建者引用: ✅ 完整")
            else:
                print(f"  问题创建者引用: ⚠️ 发现 {orphan_bugs} 个孤儿记录")
        except Exception as e:
            print(f"  问题创建者引用: ❌ 检查失败 ({e})")
        
        # 检查assigned_to引用
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM bugs 
                WHERE assigned_to IS NOT NULL 
                AND assigned_to NOT IN (SELECT id FROM users)
            """)
            orphan_assigned = cursor.fetchone()[0]
            
            if orphan_assigned == 0:
                print("  问题分配者引用: ✅ 完整")
            else:
                print(f"  问题分配者引用: ⚠️ 发现 {orphan_assigned} 个孤儿记录")
        except Exception as e:
            print(f"  问题分配者引用: ❌ 检查失败 ({e})")
        
        # 检查通知表引用
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM notifications 
                WHERE user_id NOT IN (SELECT id FROM users)
            """)
            orphan_notifications = cursor.fetchone()[0]
            
            if orphan_notifications == 0:
                print("  通知用户引用: ✅ 完整")
            else:
                print(f"  通知用户引用: ⚠️ 发现 {orphan_notifications} 个孤儿记录")
        except Exception as e:
            print(f"  通知用户引用: ❌ 检查失败 ({e})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据完整性失败: {e}")

def generate_summary():
    """生成检查总结"""
    print("\n📋 数据库状态总结")
    print("=" * 50)
    
    # 重新检查关键状态
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 统计信息
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bugs")
        bug_count = cursor.fetchone()[0]
        
        try:
            cursor.execute("SELECT COUNT(*) FROM notifications")
            notification_count = cursor.fetchone()[0]
        except:
            notification_count = 0
        
        print(f"📊 数据统计:")
        print(f"  用户总数: {user_count}")
        print(f"  问题总数: {bug_count}")
        print(f"  通知总数: {notification_count}")
        
        # 系统状态
        try:
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'notification_enabled'")
            result = cursor.fetchone()
            notification_enabled = result[0].lower() == 'true' if result else False
        except:
            notification_enabled = False
        
        print(f"\n🔔 系统状态:")
        print(f"  数据库类型: {DB_TYPE.upper()}")
        print(f"  通知系统: {'✅ 启用' if notification_enabled else '❌ 禁用'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 生成总结失败: {e}")

if __name__ == "__main__":
    print("🚀 ReBugTracker 综合数据库状态检查")
    print("=" * 60)
    
    # 执行各项检查
    structure_result = check_database_structure()
    check_notification_system()
    check_user_roles()
    check_data_integrity()
    generate_summary()
    
    print("\n🎉 数据库状态检查完成！")
