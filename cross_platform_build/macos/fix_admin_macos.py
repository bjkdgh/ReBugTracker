#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 macOS 版本中 admin 用户的中文名和团队信息
"""

import os
import sys
import sqlite3
from pathlib import Path

def fix_admin_user_data():
    """修复 admin 用户的中文名和团队信息"""
    try:
        print("🔧 修复 macOS 版本 admin 用户数据...")
        
        # 获取数据库路径
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        db_path = os.path.join(app_dir, 'rebugtracker.db')
        
        if not os.path.exists(db_path):
            print(f"   ❌ 数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 admin 用户
        print("1. 检查 admin 用户...")
        cursor.execute("SELECT id, username, chinese_name, team, role, role_en FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, username, chinese_name, team, role, role_en = admin_user
            print(f"   ✅ 找到 admin 用户 (ID: {user_id})")
            print(f"   📋 当前信息: 中文名='{chinese_name}', 团队='{team}', 角色='{role}', 角色英文='{role_en}'")
            
            # 检查是否需要更新
            needs_update = False
            updates = []
            params = []
            
            if not chinese_name:
                updates.append("chinese_name = ?")
                params.append("系统管理员")
                needs_update = True
                print("   🔄 需要设置中文名")
            
            if not team:
                updates.append("team = ?")
                params.append("管理员")
                needs_update = True
                print("   🔄 需要设置团队")
            
            if not role_en or role_en != 'gly':
                updates.append("role_en = ?")
                params.append("gly")
                needs_update = True
                print("   🔄 需要设置角色英文标识")
            
            # 确保有 team_en 字段
            try:
                cursor.execute("SELECT team_en FROM users WHERE username = 'admin'")
                team_en = cursor.fetchone()[0] if cursor.fetchone() else None
                if not team_en:
                    updates.append("team_en = ?")
                    params.append("gly")
                    needs_update = True
                    print("   🔄 需要设置团队英文标识")
            except sqlite3.OperationalError:
                # team_en 字段可能不存在，忽略
                pass
            
            if needs_update:
                # 执行更新
                params.append(user_id)
                update_sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(update_sql, params)
                print("   ✅ 已更新 admin 用户信息")
            else:
                print("   ℹ️ admin 用户信息已完整，无需更新")
                
        else:
            print("   ❌ 未找到 admin 用户")
            return False
        
        # 提交更改
        conn.commit()
        
        # 验证结果
        print("2. 验证修复结果...")
        cursor.execute("""
            SELECT username, chinese_name, team, role, role_en, 
                   CASE WHEN team_en IS NOT NULL THEN team_en ELSE 'N/A' END as team_en
            FROM users WHERE username = 'admin'
        """)
        result = cursor.fetchone()
        
        if result:
            username, chinese_name, team, role, role_en, team_en = result
            print(f"   ✅ 修复后的 admin 用户信息:")
            print(f"      用户名: {username}")
            print(f"      中文名: {chinese_name}")
            print(f"      团队: {team}")
            print(f"      角色: {role}")
            print(f"      角色英文: {role_en}")
            print(f"      团队英文: {team_en}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 ReBugTracker macOS Admin 用户修复工具")
    print("=" * 50)
    
    if fix_admin_user_data():
        print("\n🎉 admin 用户数据修复完成!")
        print("💡 现在 admin 用户应该有完整的中文名和团队信息了")
    else:
        print("\n❌ admin 用户数据修复失败!")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
