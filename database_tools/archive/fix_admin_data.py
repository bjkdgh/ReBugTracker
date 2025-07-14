#!/usr/bin/env python3
# 修复admin用户数据和创建管理员测试数据

import sys
import os
import sqlite3
import traceback
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_admin_data():
    """修复admin用户数据"""
    try:
        print("🔧 修复admin用户数据...")
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rebugtracker.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查admin用户的密码
        print("1. 检查admin用户密码...")
        cursor.execute("SELECT id, username, password FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f"   ✅ 找到admin用户 (ID: {admin_user[0]})")
            
            # 更新admin密码为123456
            new_password = generate_password_hash('123456')
            cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password,))
            print("   ✅ 更新admin密码为123456")
        else:
            print("   ❌ 未找到admin用户")
            return False
        
        # 检查是否已经有admin创建的问题
        cursor.execute("SELECT COUNT(*) FROM bugs WHERE created_by = ?", (admin_user[0],))
        existing_admin_bugs = cursor.fetchone()[0]
        
        if existing_admin_bugs > 0:
            print(f"   ℹ️ admin已有{existing_admin_bugs}个问题，跳过创建新问题")
        else:
            # 创建一些admin管理的问题数据
            print("2. 创建admin管理的问题数据...")
            
            admin_bugs = [
                {
                    'title': '系统性能优化',
                    'description': '优化系统整体性能，提升响应速度',
                    'status': '待处理',
                    'project': '系统优化',
                    'assigned_to': 22,  # wbx
                    'created_by': admin_user[0]
                },
                {
                    'title': '用户权限管理完善',
                    'description': '完善用户权限管理功能，增加细粒度控制',
                    'status': '进行中',
                    'project': '权限管理',
                    'assigned_to': 23,  # zrq
                    'created_by': admin_user[0]
                },
                {
                    'title': '数据库备份策略',
                    'description': '制定和实施数据库自动备份策略',
                    'status': '待处理',
                    'project': '数据管理',
                    'assigned_to': 24,  # lrz
                    'created_by': admin_user[0]
                },
                {
                    'title': '系统监控告警',
                    'description': '建立系统监控和告警机制',
                    'status': '已分配',
                    'project': '运维监控',
                    'assigned_to': 25,  # fcl
                    'created_by': admin_user[0]
                },
                {
                    'title': '安全漏洞扫描',
                    'description': '定期进行安全漏洞扫描和修复',
                    'status': '待处理',
                    'project': '安全管理',
                    'assigned_to': 26,  # wxw
                    'created_by': admin_user[0]
                }
            ]
            
            # 插入admin创建的问题
            for bug in admin_bugs:
                cursor.execute("""
                    INSERT INTO bugs (title, description, status, project, assigned_to, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    bug['title'],
                    bug['description'], 
                    bug['status'],
                    bug['project'],
                    bug['assigned_to'],
                    bug['created_by']
                ))
                print(f"   ✅ 创建问题: {bug['title']}")
        
        # 提交更改
        conn.commit()
        
        # 验证结果
        print("3. 验证修复结果...")
        
        # 检查admin创建的问题
        cursor.execute("SELECT COUNT(*) FROM bugs WHERE created_by = ?", (admin_user[0],))
        admin_bug_count = cursor.fetchone()[0]
        print(f"   admin创建的问题数: {admin_bug_count}")
        
        # 检查admin分配的问题
        cursor.execute("SELECT COUNT(*) FROM bugs WHERE assigned_to = ?", (admin_user[0],))
        admin_assigned_count = cursor.fetchone()[0]
        print(f"   分配给admin的问题数: {admin_assigned_count}")
        
        # 显示admin创建的问题列表
        cursor.execute("""
            SELECT b.id, b.title, b.status, u.username as assignee
            FROM bugs b
            LEFT JOIN users u ON b.assigned_to = u.id
            WHERE b.created_by = ?
            ORDER BY b.id DESC
        """, (admin_user[0],))
        admin_bugs_list = cursor.fetchall()
        
        print("   admin创建的问题列表:")
        for bug in admin_bugs_list:
            print(f"     ID:{bug[0]} | {bug[1]} | {bug[2]} | 分配给:{bug[3]}")
        
        conn.close()
        
        print(f"\n✅ admin用户数据修复完成!")
        print(f"   - 更新了admin密码")
        print(f"   - admin创建的问题数: {admin_bug_count}")
        print(f"   - admin现在可以正常登录和管理问题")
        
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        traceback.print_exc()
        return False

def test_admin_login():
    """测试admin登录"""
    try:
        print("\n🧪 测试admin登录...")
        
        import urllib.request
        import urllib.parse
        import http.cookiejar
        
        # 创建cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        # 尝试登录
        login_data = urllib.parse.urlencode({
            'username': 'admin',
            'password': '123456'
        }).encode('utf-8')
        
        request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        response = opener.open(request)
        
        if response.getcode() == 200:
            print("   ✅ admin登录成功")
            
            # 测试访问首页
            response = opener.open('http://127.0.0.1:5000/')
            if response.getcode() == 200:
                print("   ✅ admin首页访问成功")
            else:
                print(f"   ❌ admin首页访问失败: {response.getcode()}")
        else:
            print(f"   ❌ admin登录失败: {response.getcode()}")
            
    except Exception as e:
        print(f"   ❌ admin登录测试失败: {e}")

if __name__ == '__main__':
    success = fix_admin_data()
    if success:
        test_admin_login()
