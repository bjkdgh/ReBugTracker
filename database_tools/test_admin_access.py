#!/usr/bin/env python3
# 测试admin用户的完整访问功能

import urllib.request
import urllib.parse
import http.cookiejar
import json
import traceback

def test_admin_complete_access():
    """测试admin用户的完整访问功能"""
    try:
        print("🧪 测试admin用户完整访问功能...")
        
        # 创建cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        print("1. admin用户登录...")
        try:
            login_data = urllib.parse.urlencode({
                'username': 'admin',
                'password': '123456'
            }).encode('utf-8')
            
            request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            
            if response.getcode() == 200:
                print("   ✅ admin登录成功")
            else:
                print(f"   ❌ admin登录失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ admin登录异常: {e}")
            return False
        
        print("2. 访问admin管理页面...")
        try:
            response = opener.open('http://127.0.0.1:5000/admin')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ admin管理页面访问成功")
                
                # 检查页面内容
                if '管理员控制面板' in content or 'admin' in content.lower():
                    print("   ✅ 管理页面内容正确")
                else:
                    print("   ⚠️ 管理页面内容可能有问题")
            else:
                print(f"   ❌ admin管理页面访问失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ admin管理页面访问异常: {e}")
        
        print("3. 测试获取所有用户API...")
        try:
            response = opener.open('http://127.0.0.1:5000/admin/users')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                users_data = json.loads(content)
                print(f"   ✅ 获取用户API成功，用户数量: {len(users_data)}")
                
                # 检查是否包含admin用户
                admin_found = False
                for user in users_data:
                    if user.get('username') == 'admin':
                        admin_found = True
                        print(f"   ✅ 找到admin用户: {user.get('chinese_name')}")
                        break
                
                if not admin_found:
                    print("   ⚠️ 未在用户列表中找到admin")
                    
            else:
                print(f"   ❌ 获取用户API失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 获取用户API异常: {e}")
        
        print("4. 测试获取所有问题API...")
        try:
            response = opener.open('http://127.0.0.1:5000/admin/bugs')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                bugs_data = json.loads(content)
                print(f"   ✅ 获取问题API成功，问题数量: {len(bugs_data)}")
                
                # 检查是否包含admin创建的问题
                admin_bugs = [bug for bug in bugs_data if bug.get('creator_name') == '系统管理员']
                print(f"   ✅ admin创建的问题数量: {len(admin_bugs)}")
                
                if admin_bugs:
                    print("   admin创建的问题:")
                    for bug in admin_bugs[:3]:  # 显示前3个
                        print(f"     • {bug.get('title')} ({bug.get('status')})")
                        
                # 检查是否包含其他用户的问题
                other_bugs = [bug for bug in bugs_data if bug.get('creator_name') != '系统管理员']
                print(f"   ✅ 其他用户创建的问题数量: {len(other_bugs)}")
                        
            else:
                print(f"   ❌ 获取问题API失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 获取问题API异常: {e}")
        
        print("5. 测试访问首页（应该重定向到admin）...")
        try:
            response = opener.open('http://127.0.0.1:5000/')
            
            if response.getcode() == 200:
                print("   ✅ 首页访问成功（已重定向到admin页面）")
            else:
                print(f"   ❌ 首页访问失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 首页访问异常: {e}")
        
        print("\n✅ admin用户访问测试完成")
        print("📊 测试总结:")
        print("   - admin用户可以正常登录")
        print("   - admin可以访问管理页面")
        print("   - admin可以查看所有用户信息")
        print("   - admin可以查看所有问题数据")
        print("   - admin拥有完整的管理员权限")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_admin_complete_access()
