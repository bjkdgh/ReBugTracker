#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间戳精度清理脚本
功能：清除数据库中created_at和resolved_at字段的微秒部分，只保留到秒的精度
"""

import sys
import os
from datetime import datetime
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_TYPE
from db_factory import get_db_connection
from sql_adapter import adapt_sql

def clean_timestamp_precision():
    """清理时间戳精度，去除微秒部分"""
    print("🧹 开始清理时间戳精度...")
    
    try:
        conn = get_db_connection()
        if DB_TYPE == 'postgres':
            from psycopg2.extras import DictCursor
            c = conn.cursor(cursor_factory=DictCursor)
        else:
            c = conn.cursor()
        
        # 获取所有需要处理的记录
        query, params = adapt_sql('SELECT id, created_at, resolved_at FROM bugs', ())
        c.execute(query, params)
        bugs = c.fetchall()
        
        print(f"📊 找到 {len(bugs)} 条记录需要检查")
        
        updated_count = 0
        
        for bug in bugs:
            bug_id = bug['id']
            created_at = bug['created_at']
            resolved_at = bug['resolved_at']
            
            # 处理created_at
            new_created_at = clean_timestamp_string(created_at)
            
            # 处理resolved_at
            new_resolved_at = None
            if resolved_at:
                new_resolved_at = clean_timestamp_string(resolved_at)
            
            # 检查是否需要更新
            need_update = False
            if created_at != new_created_at:
                need_update = True
                print(f"  📝 记录 {bug_id}: created_at {created_at} -> {new_created_at}")
            
            if resolved_at and resolved_at != new_resolved_at:
                need_update = True
                print(f"  📝 记录 {bug_id}: resolved_at {resolved_at} -> {new_resolved_at}")
            
            # 执行更新
            if need_update:
                if new_resolved_at:
                    query, params = adapt_sql('''
                        UPDATE bugs 
                        SET created_at = %s, resolved_at = %s 
                        WHERE id = %s
                    ''', (new_created_at, new_resolved_at, bug_id))
                else:
                    query, params = adapt_sql('''
                        UPDATE bugs 
                        SET created_at = %s 
                        WHERE id = %s
                    ''', (new_created_at, bug_id))
                
                c.execute(query, params)
                updated_count += 1
        
        # 提交更改
        conn.commit()
        print(f"✅ 成功更新了 {updated_count} 条记录")
        
    except Exception as e:
        print(f"❌ 清理过程中出现错误: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def clean_timestamp_string(timestamp_str):
    """清理时间戳字符串，去除微秒部分
    
    Args:
        timestamp_str: 时间戳字符串
        
    Returns:
        str: 清理后的时间戳字符串（精确到秒）
    """
    if not timestamp_str:
        return timestamp_str
    
    # 如果是字符串，尝试解析并重新格式化
    if isinstance(timestamp_str, str):
        # 处理各种可能的时间格式
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+',  # YYYY-MM-DD HH:MM:SS.microseconds
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.\d+',  # ISO format with microseconds
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',       # Already clean format
        ]
        
        for pattern in patterns:
            match = re.match(pattern, timestamp_str)
            if match:
                clean_part = match.group(1)
                # 标准化格式为 YYYY-MM-DD HH:MM:SS
                if 'T' in clean_part:
                    clean_part = clean_part.replace('T', ' ')
                return clean_part
        
        # 如果没有匹配到任何模式，尝试直接解析
        try:
            # 尝试解析各种格式
            for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f', 
                       '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
        except:
            pass
        
        # 如果都失败了，返回原始值
        return timestamp_str
    
    # 如果是datetime对象，直接格式化
    elif hasattr(timestamp_str, 'strftime'):
        return timestamp_str.strftime('%Y-%m-%d %H:%M:%S')
    
    # 其他情况返回原始值
    return timestamp_str

def main():
    """主函数"""
    print("🚀 ReBugTracker 时间戳精度清理工具")
    print("=" * 50)
    
    # 确认操作
    response = input("⚠️  此操作将修改数据库中的时间戳数据，是否继续？(y/N): ")
    if response.lower() != 'y':
        print("❌ 操作已取消")
        return
    
    try:
        clean_timestamp_precision()
        print("\n🎉 时间戳精度清理完成！")
        print("💡 提示：现在所有时间戳都精确到秒，不包含微秒部分")
        
    except Exception as e:
        print(f"\n💥 清理失败: {str(e)}")
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
