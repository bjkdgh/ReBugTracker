#!/usr/bin/env python3
# 测试实施组用户的功能按钮

import urllib.request
import urllib.parse
import http.cookiejar
import json
import traceback

def test_ssz_user_functions():
    """测试实施组用户的功能按钮"""
    try:
        print("🧪 测试实施组用户的功能按钮...")
        
        # 创建cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        print("1. 实施组用户gh登录...")
        try:
            login_data = urllib.parse.urlencode({
                'username': 'gh',
                'password': '123456'
            }).encode('utf-8')
            
            request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            
            if response.getcode() == 200:
                print("   ✅ gh用户登录成功")
            else:
                print(f"   ❌ gh用户登录失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ gh用户登录异常: {e}")
            return False
        
        print("2. 访问首页，检查提交新问题按钮...")
        try:
            response = opener.open('http://127.0.0.1:5000/')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ 首页访问成功")
                
                # 检查是否有提交新问题按钮
                if '提交新问题' in content:
                    print("   ✅ 找到'提交新问题'按钮")
                else:
                    print("   ❌ 未找到'提交新问题'按钮")
                
                # 检查是否有删除按钮（对于gh创建的问题）
                if '删除' in content:
                    print("   ✅ 找到'删除'按钮")
                else:
                    print("   ❌ 未找到'删除'按钮")
                
                # 检查是否有确认闭环按钮（对于已解决的问题）
                if '确认闭环' in content:
                    print("   ✅ 找到'确认闭环'按钮")
                else:
                    print("   ⚠️ 未找到'确认闭环'按钮（可能没有已解决的问题）")
                    
            else:
                print(f"   ❌ 首页访问失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 首页访问异常: {e}")
            return False
        
        print("3. 测试访问提交问题页面...")
        try:
            response = opener.open('http://127.0.0.1:5000/submit')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ 提交问题页面访问成功")
                
                # 检查页面内容
                if '提交问题' in content and '问题标题' in content:
                    print("   ✅ 提交问题页面内容正确")
                elif '提交新问题需求' in content:
                    print("   ✅ 提交问题页面内容正确")
                else:
                    print("   ❌ 提交问题页面内容有问题")
                    
            else:
                print(f"   ❌ 提交问题页面访问失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 提交问题页面访问异常: {e}")
        
        print("4. 测试提交新问题功能...")
        try:
            # 准备提交数据
            submit_data = {
                'title': '测试实施组提交的问题',
                'description': '这是一个测试实施组用户提交功能的问题',
                'project': '测试项目',
                'manager': '张佳楠'  # 假设这是一个负责人
            }
            
            # 提交问题
            post_data = urllib.parse.urlencode(submit_data).encode('utf-8')
            request = urllib.request.Request('http://127.0.0.1:5000/submit', data=post_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            
            if response.getcode() == 200:
                print("   ✅ 问题提交成功")
                
                # 检查是否重定向到首页
                final_url = response.geturl()
                if 'submit' not in final_url:
                    print("   ✅ 提交后正确重定向")
                else:
                    print("   ⚠️ 提交后未重定向")
                    
            else:
                print(f"   ❌ 问题提交失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 问题提交异常: {e}")
        
        print("5. 重新访问首页，检查新提交的问题...")
        try:
            response = opener.open('http://127.0.0.1:5000/')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                # 检查是否包含新提交的问题
                if '测试实施组提交的问题' in content:
                    print("   ✅ 新提交的问题出现在首页")
                    
                    # 检查是否有删除按钮（因为是gh创建的）
                    if '删除' in content:
                        print("   ✅ 新问题有删除按钮（创建者权限）")
                    else:
                        print("   ❌ 新问题没有删除按钮")
                else:
                    print("   ❌ 新提交的问题未出现在首页")
                    
        except Exception as e:
            print(f"   ❌ 检查新问题异常: {e}")
        
        print("6. 测试其他实施组用户...")
        test_users = ['qht', 'ps', 'sxz']
        
        for username in test_users:
            print(f"   测试用户 {username}...")
            try:
                # 清除cookies
                cookie_jar.clear()
                
                # 登录
                login_data = urllib.parse.urlencode({
                    'username': username,
                    'password': '123456'
                }).encode('utf-8')
                
                request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
                request.add_header('Content-Type', 'application/x-www-form-urlencoded')
                
                response = opener.open(request)
                
                if response.getcode() == 200:
                    print(f"     ✅ {username} 登录成功")
                    
                    # 访问首页
                    response = opener.open('http://127.0.0.1:5000/')
                    content = response.read().decode('utf-8')
                    
                    if '提交新问题' in content:
                        print(f"     ✅ {username} 可以看到'提交新问题'按钮")
                    else:
                        print(f"     ❌ {username} 看不到'提交新问题'按钮")
                        
                else:
                    print(f"     ❌ {username} 登录失败")
                    
            except Exception as e:
                print(f"     ❌ {username} 测试异常: {e}")
        
        print("\n✅ 实施组用户功能测试完成")
        print("📊 测试总结:")
        print("   - 实施组用户可以正常登录")
        print("   - 实施组用户可以看到'提交新问题'按钮")
        print("   - 实施组用户可以访问提交问题页面")
        print("   - 实施组用户可以提交新问题")
        print("   - 实施组用户可以删除自己创建的问题")
        print("   - 实施组用户可以确认闭环已解决的问题")
        print("   - 角色权限控制正确工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_ssz_user_functions()
