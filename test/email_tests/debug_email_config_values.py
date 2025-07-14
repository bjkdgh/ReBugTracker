#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试邮件配置值类型问题
"""

import sys
import os
sys.path.append('.')
from db_factory import get_db_connection
from sql_adapter import adapt_sql

def main():
    print("🔍 调试邮件配置值类型问题")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查看邮件配置
    query, params = adapt_sql('''
        SELECT config_key, config_value FROM system_config 
        WHERE config_key IN (%s, %s, %s)
        ORDER BY config_key
    ''', ('notification_email_smtp_port', 'notification_email_use_tls', 'notification_email_enabled'))

    cursor.execute(query, params)
    configs = cursor.fetchall()

    print('📧 关键邮件配置:')
    for config in configs:
        key = config[0]
        value = config[1]
        print(f'   {key}: {value} (类型: {type(value)})')

    # 测试条件判断
    port = None
    use_tls = None
    for config in configs:
        if config[0] == 'notification_email_smtp_port':
            port = config[1]
        elif config[0] == 'notification_email_use_tls':
            use_tls = config[1]

    print(f'\n🧪 条件判断测试:')
    print(f'   port: {port} (类型: {type(port)})')
    print(f'   use_tls: {use_tls} (类型: {type(use_tls)})')
    print(f'   port == 465: {port == 465}')
    print(f'   port == "465": {port == "465"}')
    if port:
        print(f'   int(port) == 465: {int(port) == 465}')
    print(f'   use_tls == "false": {use_tls == "false"}')
    if use_tls:
        print(f'   use_tls.lower() == "false": {use_tls.lower() == "false"}')
        print(f'   not (use_tls.lower() == "true"): {not (use_tls.lower() == "true")}')

    # 测试邮件通知器的配置读取
    print(f'\n📧 测试邮件通知器配置读取:')
    from notification.channels.email_notifier import EmailNotifier
    
    notifier = EmailNotifier()
    print(f'   notifier.config["smtp_port"]: {notifier.config["smtp_port"]} (类型: {type(notifier.config["smtp_port"])})')
    print(f'   notifier.config["use_tls"]: {notifier.config["use_tls"]} (类型: {type(notifier.config["use_tls"])})')
    
    # 测试条件判断
    port_condition = notifier.config['smtp_port'] == 465
    tls_condition = not notifier.config['use_tls']
    ssl_condition = port_condition and tls_condition
    
    print(f'   smtp_port == 465: {port_condition}')
    print(f'   not use_tls: {tls_condition}')
    print(f'   SSL条件 (465端口 且 不使用TLS): {ssl_condition}')
    
    if ssl_condition:
        print('   ✅ 应该使用 SMTP_SSL')
    else:
        print('   ❌ 应该使用 SMTP (TLS模式)')

    conn.close()

if __name__ == '__main__':
    main()
