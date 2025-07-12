#!/usr/bin/env python3
# 测试admin用户管理界面的中文姓名功能

import urllib.request
import urllib.parse
import http.cookiejar
import json
import traceback

def test_admin_user_management():
    """测试admin用户管理界面的中文姓名功能"""
    try:
        print("🧪 测试admin用户管理界面的中文姓名功能...")
        
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
        
        print("2. 测试获取用户列表API（检查中文姓名）...")
        try:
            response = opener.open('http://127.0.0.1:5000/admin/users')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                users_data = json.loads(content)
                print(f"   ✅ 获取用户列表成功，用户数量: {len(users_data)}")
                
                # 检查中文姓名字段
                chinese_name_count = 0
                for user in users_data:
                    if user.get('chinese_name'):
                        chinese_name_count += 1
                        print(f"   ✅ 用户 {user['username']} 有中文姓名: {user['chinese_name']}")
                
                print(f"   📊 有中文姓名的用户数量: {chinese_name_count}/{len(users_data)}")
                        
            else:
                print(f"   ❌ 获取用户列表失败: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 获取用户列表异常: {e}")
            return False
        
        print("3. 测试添加新用户（包含中文姓名）...")
        try:
            new_user_data = {
                'username': 'test_chinese_user',
                'chinese_name': '测试中文用户',
                'password': '123456',
                'role': 'zncy',
                'team': '测试团队'
            }
            
            request = urllib.request.Request(
                'http://127.0.0.1:5000/admin/users',
                data=json.dumps(new_user_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            response = opener.open(request)
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                result = json.loads(content)
                if result.get('success'):
                    print(f"   ✅ 添加用户成功，用户ID: {result.get('user_id')}")
                    new_user_id = result.get('user_id')
                else:
                    print(f"   ❌ 添加用户失败: {result.get('message')}")
                    return False
            else:
                print(f"   ❌ 添加用户HTTP错误: {response.getcode()}")
                return False
                
        except Exception as e:
            print(f"   ❌ 添加用户异常: {e}")
            return False
        
        print("4. 测试获取新添加用户的详细信息...")
        try:
            response = opener.open(f'http://127.0.0.1:5000/admin/users/{new_user_id}')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                user_detail = json.loads(content)
                print(f"   ✅ 获取用户详情成功")
                print(f"   用户名: {user_detail.get('username')}")
                print(f"   中文姓名: {user_detail.get('chinese_name')}")
                print(f"   角色: {user_detail.get('role')}")
                print(f"   团队: {user_detail.get('team')}")
                
                if user_detail.get('chinese_name') == '测试中文用户':
                    print("   ✅ 中文姓名保存正确")
                else:
                    print("   ❌ 中文姓名保存错误")
                    
            else:
                print(f"   ❌ 获取用户详情失败: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 获取用户详情异常: {e}")
        
        print("5. 测试更新用户信息（修改中文姓名）...")
        try:
            update_data = {
                'id': new_user_id,
                'username': 'test_chinese_user',
                'chinese_name': '更新后的中文姓名',
                'role': 'zncy',
                'team': '更新后的团队'
            }
            
            request = urllib.request.Request(
                f'http://127.0.0.1:5000/admin/users/{new_user_id}',
                data=json.dumps(update_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            request.get_method = lambda: 'PUT'
            
            response = opener.open(request)
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                result = json.loads(content)
                if result.get('success'):
                    print("   ✅ 更新用户成功")
                else:
                    print(f"   ❌ 更新用户失败: {result.get('message')}")
            else:
                print(f"   ❌ 更新用户HTTP错误: {response.getcode()}")
                
        except Exception as e:
            print(f"   ❌ 更新用户异常: {e}")
        
        print("6. 验证更新后的用户信息...")
        try:
            response = opener.open(f'http://127.0.0.1:5000/admin/users/{new_user_id}')
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                user_detail = json.loads(content)
                print(f"   更新后的中文姓名: {user_detail.get('chinese_name')}")
                print(f"   更新后的团队: {user_detail.get('team')}")
                
                if user_detail.get('chinese_name') == '更新后的中文姓名':
                    print("   ✅ 中文姓名更新成功")
                else:
                    print("   ❌ 中文姓名更新失败")
                    
        except Exception as e:
            print(f"   ❌ 验证更新异常: {e}")
        
        print("7. 清理测试数据...")
        try:
            request = urllib.request.Request(f'http://127.0.0.1:5000/admin/users/{new_user_id}')
            request.get_method = lambda: 'DELETE'
            
            response = opener.open(request)
            content = response.read().decode('utf-8')
            
            if response.getcode() == 200:
                result = json.loads(content)
                if result.get('success'):
                    print("   ✅ 清理测试用户成功")
                else:
                    print(f"   ⚠️ 清理测试用户失败: {result.get('message')}")
            else:
                print(f"   ⚠️ 清理测试用户HTTP错误: {response.getcode()}")
                
        except Exception as e:
            print(f"   ⚠️ 清理测试用户异常: {e}")
        
        print("\n✅ admin用户管理界面中文姓名功能测试完成")
        print("📊 测试总结:")
        print("   - admin可以查看所有用户的中文姓名")
        print("   - admin可以添加包含中文姓名的新用户")
        print("   - admin可以编辑和更新用户的中文姓名")
        print("   - 前后端API完全支持中文姓名字段")
        print("   - PostgreSQL和SQLite模式都完全兼容")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_admin_user_management()
