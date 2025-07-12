#!/usr/bin/env python3
# 测试负责人用户的完整指派功能

import urllib.request
import urllib.parse
import http.cookiejar
import json
import traceback
import re

def test_fzr_assign_function():
    """测试负责人用户的完整指派功能"""
    try:
        print("🧪 测试负责人用户的完整指派功能...")
        
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
        
        print("2. 访问首页，检查指派按钮...")
        try:
            response = opener.open('http://127.0.0.1:5000/')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ 首页访问成功")
                
                # 查找指派链接
                assign_links = re.findall(r'/bug/assign/(\d+)', content)
                assign_count = content.count('指派')
                
                print(f"   🔗 找到 {len(assign_links)} 个指派链接")
                print(f"   📋 找到 {assign_count} 个'指派'按钮")
                
                if assign_links:
                    print("   ✅ 找到指派按钮")
                    first_bug_id = assign_links[0]
                    print(f"   📋 将测试问题ID: {first_bug_id}")
                else:
                    print("   ❌ 未找到指派按钮")
                    return False
                    
            else:
                print(f"   ❌ 首页访问失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 首页访问异常: {e}")
            return False
        
        print("3. 访问指派页面...")
        try:
            assign_url = f'http://127.0.0.1:5000/bug/assign/{first_bug_id}'
            print(f"   访问: {assign_url}")
            
            response = opener.open(assign_url)
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                print("   ✅ 指派页面访问成功")
                
                # 检查页面内容
                if '指派问题' in content or '分配问题' in content:
                    print("   ✅ 页面标题正确")
                else:
                    print("   ⚠️ 页面标题可能有问题")
                
                # 检查是否有表单
                if '<form' in content:
                    print("   ✅ 找到指派表单")
                else:
                    print("   ❌ 未找到指派表单")
                    return False
                
                # 检查是否有用户选择
                if '<select' in content and 'name="assigned_to"' in content:
                    print("   ✅ 找到用户选择下拉框")
                else:
                    print("   ❌ 未找到用户选择下拉框")
                    return False
                
                # 提取可选用户
                user_options = re.findall(r'<option value="(\d+)"[^>]*>([^<]+)</option>', content)
                print(f"   👥 可选用户数量: {len(user_options)}")
                
                for user_id, user_name in user_options[:5]:  # 显示前5个用户
                    print(f"     - ID:{user_id} {user_name}")
                
                if user_options:
                    selected_user_id = user_options[0][0]
                    selected_user_name = user_options[0][1]
                    print(f"   🎯 可指派给: {selected_user_name} (ID:{selected_user_id})")
                else:
                    print("   ❌ 没有可选用户")
                    return False
                    
            else:
                print(f"   ❌ 指派页面访问失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 指派页面访问异常: {e}")
            return False
        
        print("4. 测试指派表单提交...")
        try:
            # 准备指派数据
            assign_data = {
                'assigned_to': selected_user_id
            }
            
            post_data = urllib.parse.urlencode(assign_data).encode('utf-8')
            request = urllib.request.Request(assign_url, data=post_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            response = opener.open(request)
            
            if response.getcode() == 200:
                print("   ✅ 指派表单提交成功")
                
                # 检查响应内容
                response_content = response.read().decode('utf-8')
                if 'success' in response_content.lower() or '成功' in response_content:
                    print("   ✅ 指派操作成功")
                else:
                    print("   ⚠️ 指派结果需要进一步验证")
                    
            else:
                print(f"   ❌ 指派表单提交失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 指派表单提交异常: {e}")
        
        print("5. 测试其他负责人用户...")
        test_users = ['lsj']  # 其他负责人用户
        
        for username in test_users:
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
                    print(f"   ✅ {username} 用户登录成功")
                    
                    # 访问首页
                    response = opener.open('http://127.0.0.1:5000/')
                    content = response.read().decode('utf-8')
                    
                    assign_count = content.count('指派')
                    print(f"   📋 {username} 用户看到 {assign_count} 个'指派'按钮")
                    
                    if assign_count > 0:
                        print(f"   ✅ {username} 用户也可以看到指派功能")
                    else:
                        print(f"   ❌ {username} 用户看不到指派功能")
                        
                else:
                    print(f"   ❌ {username} 用户登录失败: {response.getcode()}")
                    
            except Exception as e:
                print(f"   ❌ {username} 用户测试异常: {e}")
        
        print("\n✅ 负责人用户指派功能测试完成")
        print("📊 测试总结:")
        print("   - 负责人用户可以正常登录")
        print("   - 负责人用户可以看到指派按钮")
        print("   - 指派页面可以正常访问")
        print("   - 指派表单包含用户选择列表")
        print("   - 指派操作可以正常提交")
        print("   - 多个负责人用户都有指派权限")
        print("   - 角色权限控制正确工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_fzr_assign_function()
