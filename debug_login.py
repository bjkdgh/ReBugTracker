#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试登录逻辑
"""

import sys
import os
import sqlite3
from urllib.parse import quote, unquote

def safe_get(obj, key, default=None):
    """安全获取对象属性，兼容字典和sqlite3.Row对象"""
    if obj is None:
        return default
    try:
        # 尝试字典方式访问
        if hasattr(obj, 'get'):
            return obj.get(key, default)
        # 尝试属性方式访问
        elif hasattr(obj, key):
            return getattr(obj, key, default)
        # 尝试索引方式访问（sqlite3.Row支持）
        elif hasattr(obj, '__getitem__'):
            try:
                return obj[key]
            except (KeyError, IndexError):
                return default
        else:
            return default
    except:
        return default

def test_login_data():
    """测试登录时读取的数据"""
    print("🔍 测试登录数据读取...")
    
    # 连接数据库
    conn = sqlite3.connect('rebugtracker.db')
    conn.row_factory = sqlite3.Row  # 使用 Row 对象
    cursor = conn.cursor()
    
    # 执行与登录相同的查询
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    user = cursor.fetchone()
    
    if user:
        print(f"📋 数据库查询结果:")
        print(f"   类型: {type(user)}")
        print(f"   ID: {user['id']}")
        print(f"   用户名: {user['username']}")
        print(f"   中文名: {repr(user['chinese_name'])}")
        print(f"   团队: {repr(user['team'])}")
        print(f"   角色: {user['role']}")
        print(f"   角色英文: {user['role_en']}")
        
        print(f"\n🔧 safe_get 测试:")
        chinese_name_safe = safe_get(user, 'chinese_name')
        team_safe = safe_get(user, 'team')
        print(f"   safe_get(user, 'chinese_name'): {repr(chinese_name_safe)}")
        print(f"   safe_get(user, 'team'): {repr(team_safe)}")
        
        print(f"\n🍪 Cookie 设置逻辑测试:")
        # 模拟登录时的 cookie 设置逻辑
        chinese_name = safe_get(user, 'chinese_name') or user['username'] or 'Unknown'
        team_name = safe_get(user, 'team') or 'Unknown'
        
        print(f"   chinese_name 计算结果: {repr(chinese_name)}")
        print(f"   team_name 计算结果: {repr(team_name)}")
        
        # 测试 URL 编码
        chinese_name_encoded = quote(str(chinese_name))
        team_name_encoded = quote(str(team_name))
        
        print(f"   chinese_name URL编码: {repr(chinese_name_encoded)}")
        print(f"   team_name URL编码: {repr(team_name_encoded)}")
        
        # 测试解码
        chinese_name_decoded = unquote(chinese_name_encoded)
        team_name_decoded = unquote(team_name_encoded)
        
        print(f"   chinese_name 解码: {repr(chinese_name_decoded)}")
        print(f"   team_name 解码: {repr(team_name_decoded)}")
        
    else:
        print("❌ 未找到 admin 用户")
    
    conn.close()

def test_direct_access():
    """直接测试字段访问"""
    print("\n🔍 直接字段访问测试...")
    
    conn = sqlite3.connect('rebugtracker.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT chinese_name, team FROM users WHERE username = ?', ('admin',))
    result = cursor.fetchone()
    
    if result:
        print(f"   chinese_name 直接访问: {repr(result['chinese_name'])}")
        print(f"   team 直接访问: {repr(result['team'])}")
        print(f"   chinese_name 是否为空: {not result['chinese_name']}")
        print(f"   team 是否为空: {not result['team']}")
        print(f"   chinese_name 类型: {type(result['chinese_name'])}")
        print(f"   team 类型: {type(result['team'])}")
    
    conn.close()

if __name__ == '__main__':
    test_login_data()
    test_direct_access()
