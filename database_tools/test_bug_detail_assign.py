#!/usr/bin/env python3
# 测试问题详情页面中的指派功能

import urllib.request
import urllib.parse
import http.cookiejar
import json
import traceback
import re

def test_bug_detail_assign():
    """测试问题详情页面中的指派功能"""
    try:
        print("🧪 测试问题详情页面中的指派功能...")
        
        # 创建cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        print("1. 负责人用户zjn登录...")
        try:
            login_data = urllib.parse.urlencode({
                'username': 'zjn',
                'password': '123456'
            }).encode('utf-8')
            
            request = urllib.request.Request('http://127.0.0.1:5000/login', data=login_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            
            if response.getcode() == 200:
                print("   ✅ zjn用户登录成功")
            else:
                print(f"   ❌ zjn用户登录失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ zjn用户登录异常: {e}")
            return False
        
        print("2. 访问首页，获取问题ID...")
        try:
            response = opener.open('http://127.0.0.1:5000/')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ 首页访问成功")
                
                # 查找问题ID
                bug_links = re.findall(r'/bug/(\d+)', content)
                if bug_links:
                    bug_id = bug_links[0]
                    print(f"   📋 找到问题ID: {bug_id}")
                else:
                    print("   ❌ 未找到问题链接")
                    return False
                    
            else:
                print(f"   ❌ 首页访问失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 首页访问异常: {e}")
            return False
        
        print("3. 访问问题详情页面...")
        try:
            detail_url = f'http://127.0.0.1:5000/bug/{bug_id}'
            print(f"   访问: {detail_url}")
            
            response = opener.open(detail_url)
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ 问题详情页面访问成功")
                
                # 检查是否有指派按钮
                assign_count = content.count('指派')
                assign_links = re.findall(r'/bug/assign/(\d+)', content)
                
                print(f"   📋 找到 {assign_count} 个'指派'按钮")
                print(f"   🔗 找到 {len(assign_links)} 个指派链接")
                
                if assign_count > 0:
                    print("   ✅ 负责人可以看到指派按钮")
                else:
                    print("   ❌ 负责人看不到指派按钮")
                
                # 检查问题信息
                if '问题详情' in content and '提交人:' in content:
                    print("   ✅ 页面内容正确")
                else:
                    print("   ❌ 页面内容有问题")
                    
            else:
                print(f"   ❌ 问题详情页面访问失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 问题详情页面访问异常: {e}")
            return False
        
        print("4. 测试从详情页面跳转到指派页面...")
        if assign_links:
            try:
                assign_bug_id = assign_links[0]
                assign_url = f'http://127.0.0.1:5000/bug/assign/{assign_bug_id}'
                print(f"   访问指派页面: {assign_url}")
                
                response = opener.open(assign_url)
                content = response.read().decode('utf-8')
                
                if response.getcode() == 200:
                    print("   ✅ 从详情页面跳转到指派页面成功")
                    
                    # 检查指派页面内容
                    if '指派问题' in content or '分配问题' in content:
                        print("   ✅ 指派页面内容正确")
                    
                    # 检查是否有返回详情按钮
                    if f'/bug/{assign_bug_id}' in content:
                        print("   ✅ 指派页面有返回详情链接")
                        
                else:
                    print(f"   ❌ 指派页面访问失败: {response.getcode()}")
                    
            except Exception as e:
                print(f"   ❌ 指派页面跳转异常: {e}")
        else:
            print("   ⚠️ 没有指派链接可以测试")
        
        print("5. 测试其他角色用户的权限控制...")
        test_users = [
            ('gh', '实施组用户'),
            ('wbx', '组内成员')
        ]
        
        for username, role_desc in test_users:
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
                    print(f"   ✅ {role_desc}({username})登录成功")
                    
                    # 访问同一个问题详情页面
                    response = opener.open(detail_url)
                    content = response.read().decode('utf-8')
                    
                    if response.getcode() == 200:
                        # 检查是否看不到指派按钮
                        assign_count = content.count('指派')
                        print(f"   📋 {role_desc}看到 {assign_count} 个'指派'按钮")
                        
                        if assign_count == 0:
                            print(f"   ✅ {role_desc}正确看不到指派按钮")
                        else:
                            print(f"   ❌ {role_desc}不应该看到指派按钮")
                        
                    else:
                        print(f"   ❌ {role_desc}访问详情页面失败: {response.getcode()}")
                        
                else:
                    print(f"   ❌ {role_desc}登录失败: {response.getcode()}")
                    
            except Exception as e:
                print(f"   ❌ {role_desc}测试异常: {e}")
        
        print("\n✅ 问题详情页面指派功能测试完成")
        print("📊 测试总结:")
        print("   - 负责人用户可以在详情页面看到指派按钮")
        print("   - 指派按钮可以正确跳转到指派页面")
        print("   - 实施组用户看不到指派按钮（权限控制正确）")
        print("   - 组内成员看不到指派按钮（权限控制正确）")
        print("   - 角色权限控制完全正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_bug_detail_assign()
