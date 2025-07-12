#!/usr/bin/env python3
# SQLite模式下的登录功能测试工具
# 用于验证SQLite数据库模式下的用户登录和页面访问功能

import urllib.request
import urllib.parse
import http.cookiejar
import sys
import traceback

def test_sqlite_login():
    """测试SQLite模式下的登录功能"""
    try:
        print("🧪 测试SQLite模式下的登录功能...")
        
        # 创建cookie jar来保持cookies
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        print("1. 测试admin用户登录...")
        try:
            login_data = urllib.parse.urlencode({
                'username': 'admin',
                'password': '123456'
            }).encode('utf-8')
            
            request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            content = response.read().decode('utf-8')
            print(f"   登录状态码: {response.getcode()}")
            
            if response.getcode() == 200:
                print("   ✅ admin登录成功")
            else:
                print(f"   ❌ admin登录失败: {response.getcode()}")
                
        except urllib.error.HTTPError as e:
            error_content = e.read().decode('utf-8')
            print(f"   ❌ admin登录HTTP错误: {e.code}")
            if e.code == 401:
                print("   ℹ️ admin用户可能不存在或密码错误（正常情况）")
            else:
                print(f"   错误内容: {error_content[:200]}")
        except Exception as e:
            print(f"   ❌ admin登录异常: {e}")
        
        print("\n2. 测试wbx用户登录...")
        try:
            # 清除之前的cookies
            cookie_jar.clear()
            
            login_data = urllib.parse.urlencode({
                'username': 'wbx',
                'password': '123456'
            }).encode('utf-8')
            
            request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            content = response.read().decode('utf-8')
            print(f"   登录状态码: {response.getcode()}")
            
            if response.getcode() == 200:
                print("   ✅ wbx登录成功")
                
                # 测试访问首页
                print("3. 测试访问首页...")
                try:
                    response = opener.open('http://127.0.0.1:5000/')
                    content = response.read().decode('utf-8')
                    print(f"   首页状态码: {response.getcode()}")
                    
                    if response.getcode() == 200:
                        print("   ✅ 首页访问成功")
                    else:
                        print(f"   ❌ 首页访问失败: {response.getcode()}")
                        
                except urllib.error.HTTPError as e:
                    error_content = e.read().decode('utf-8')
                    print(f"   ❌ 首页HTTP错误: {e.code}")
                    print(f"   错误内容: {error_content[:200]}")
                except Exception as e:
                    print(f"   ❌ 首页访问异常: {e}")
                    
                # 测试访问team-issues
                print("4. 测试访问team-issues...")
                try:
                    response = opener.open('http://127.0.0.1:5000/team-issues')
                    content = response.read().decode('utf-8')
                    print(f"   team-issues状态码: {response.getcode()}")
                    
                    if response.getcode() == 200:
                        print("   ✅ team-issues访问成功")
                        # 检查是否包含用户信息
                        if '王柏翔' in content:
                            print("   ✅ 用户中文姓名显示正确")
                        elif 'wbx' in content:
                            print("   ✅ 用户名显示正确")
                        else:
                            print("   ⚠️ 未找到用户信息")
                    else:
                        print(f"   ❌ team-issues访问失败: {response.getcode()}")
                        
                except urllib.error.HTTPError as e:
                    error_content = e.read().decode('utf-8')
                    print(f"   ❌ team-issues HTTP错误: {e.code}")
                    print(f"   错误内容: {error_content[:200]}")
                except Exception as e:
                    print(f"   ❌ team-issues访问异常: {e}")
                    
            else:
                print(f"   ❌ wbx登录失败: {response.getcode()}")
                
        except urllib.error.HTTPError as e:
            error_content = e.read().decode('utf-8')
            print(f"   ❌ wbx登录HTTP错误: {e.code}")
            print(f"   错误内容: {error_content[:200]}")
        except Exception as e:
            print(f"   ❌ wbx登录异常: {e}")
        
        # 测试其他用户
        test_users = ['zrq', 'lrz', 'fcl', 'wxw']
        print(f"\n5. 测试其他用户登录...")
        
        for username in test_users:
            try:
                cookie_jar.clear()
                
                login_data = urllib.parse.urlencode({
                    'username': username,
                    'password': '123456'
                }).encode('utf-8')
                
                request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
                request.add_header('Content-Type', 'application/x-www-form-urlencoded')
                
                response = opener.open(request)
                print(f"   ✅ {username} 登录成功")
                
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    print(f"   ❌ {username} 登录失败（用户名或密码错误）")
                else:
                    print(f"   ❌ {username} HTTP错误: {e.code}")
            except Exception as e:
                print(f"   ❌ {username} 登录异常: {e}")
        
        print("\n✅ SQLite登录测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_sqlite_login()
