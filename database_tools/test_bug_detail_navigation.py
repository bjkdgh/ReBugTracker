#!/usr/bin/env python3
# 测试问题详情页面跳转功能

import urllib.request
import urllib.parse
import http.cookiejar
import json
import traceback
import re

def test_bug_detail_navigation():
    """测试问题详情页面跳转功能"""
    try:
        print("🧪 测试问题详情页面跳转功能...")
        
        # 创建cookie jar
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        # 测试不同角色的用户
        test_users = [
            ('gh', '实施组用户', 'index页面'),
            ('wbx', '组内成员', 'team-issues页面'),
            ('admin', '管理员', 'admin页面')
        ]
        
        for username, role_desc, expected_page in test_users:
            print(f"\n{len(test_users) - test_users.index((username, role_desc, expected_page))}. 测试{role_desc} ({username})...")
            
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
                    print(f"   ✅ {username} 登录成功")
                else:
                    print(f"   ❌ {username} 登录失败: {response.getcode()}")
                    continue
                
                # 访问首页
                response = opener.open('http://127.0.0.1:5000/')
                content = response.read().decode('utf-8')
                
                if response.getcode() == 200:
                    print(f"   ✅ 首页访问成功 ({expected_page})")
                    
                    # 查找问题链接
                    bug_links = re.findall(r'/bug/(\d+)', content)
                    detail_count = content.count('查看详情')
                    
                    print(f"   📊 找到 {len(bug_links)} 个问题链接")
                    print(f"   📋 找到 {detail_count} 个'查看详情'按钮")
                    
                    if detail_count > 0:
                        print("   ✅ 找到'查看详情'按钮")
                        
                        # 测试点击第一个详情链接
                        if bug_links:
                            first_bug_id = bug_links[0]
                            detail_url = f'http://127.0.0.1:5000/bug/{first_bug_id}'
                            
                            try:
                                detail_response = opener.open(detail_url)
                                detail_content = detail_response.read().decode('utf-8')
                                
                                if detail_response.getcode() == 200:
                                    print(f"   ✅ 详情页面访问成功 (问题ID: {first_bug_id})")
                                    
                                    # 检查详情页面内容
                                    if '问题详情' in detail_content:
                                        print("   ✅ 详情页面内容正确")
                                    else:
                                        print("   ⚠️ 详情页面内容可能有问题")
                                        
                                else:
                                    print(f"   ❌ 详情页面访问失败: {detail_response.getcode()}")
                                    
                            except Exception as e:
                                print(f"   ❌ 详情页面访问异常: {e}")
                    else:
                        print("   ❌ 未找到'查看详情'按钮")
                        
                        # 检查是否有其他形式的详情链接
                        if bug_links:
                            print("   🔍 检查是否有其他形式的详情链接...")
                            if f'/bug/{bug_links[0]}' in content:
                                print("   ✅ 找到问题详情链接（可能是标题链接）")
                            else:
                                print("   ❌ 没有找到任何详情链接")
                else:
                    print(f"   ❌ 首页访问失败: {response.getcode()}")
                    
            except Exception as e:
                print(f"   ❌ {username} 测试异常: {e}")
        
        print("\n4. 测试直接访问详情页面...")
        try:
            # 使用最后一个登录的用户测试直接访问
            test_urls = [
                'http://127.0.0.1:5000/bug/1',
                'http://127.0.0.1:5000/bug/99999',  # 不存在的问题
            ]
            
            for url in test_urls:
                try:
                    response = opener.open(url)
                    if response.getcode() == 200:
                        print(f"   ✅ {url} 访问成功")
                    else:
                        print(f"   ⚠️ {url} 返回: {response.getcode()}")
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        print(f"   ✅ {url} 正确返回404（问题不存在）")
                    else:
                        print(f"   ❌ {url} 返回错误: {e.code}")
                except Exception as e:
                    print(f"   ❌ {url} 访问异常: {e}")
                    
        except Exception as e:
            print(f"   ❌ 直接访问测试异常: {e}")
        
        print("\n✅ 问题详情页面跳转功能测试完成")
        print("📊 测试总结:")
        print("   - 测试了不同角色用户的详情页面访问")
        print("   - 验证了'查看详情'按钮的显示和功能")
        print("   - 测试了详情页面的正常访问")
        print("   - 验证了错误处理（404等）")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_bug_detail_navigation()
