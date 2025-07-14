#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的邮件测试 - 发送给t1用户
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_email():
    """简单邮件测试"""
    print("🧪 简单邮件测试 - 发送给t1用户")
    print("📧 目标邮箱: 237038603@qq.com")
    print("=" * 50)
    
    try:
        # 直接导入邮件通知器
        from notification.channels.email_notifier import EmailNotifier
        
        print("1. 创建邮件通知器...")
        email_notifier = EmailNotifier()
        
        print("2. 检查邮件通知器状态...")
        is_enabled = email_notifier.is_enabled()
        print(f"   状态: {'✅ 启用' if is_enabled else '❌ 禁用'}")
        
        if not is_enabled:
            print("   ❌ 邮件通知器未启用")
            return False
        
        print("3. 准备收件人信息...")
        recipient_info = {
            'id': '27',
            'name': 't1',
            'email': '237038603@qq.com'
        }
        
        print(f"   收件人: {recipient_info['name']}")
        print(f"   邮箱: {recipient_info['email']}")
        
        print("4. 发送测试邮件...")
        success = email_notifier.send(
            title="🧪 ReBugTracker测试邮件 - t1用户",
            content=f"""您好 t1！

这是一封发送给您的测试邮件。

📧 收件人信息：
- 用户ID: 27
- 用户名: t1
- 邮箱: 237038603@qq.com

如果您收到这封邮件，说明ReBugTracker邮件系统工作正常！

---
ReBugTracker 系统
测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
            recipient=recipient_info,
            priority=1
        )
        
        if success:
            print("   ✅ 邮件发送成功！")
            print("   📧 请检查邮箱: 237038603@qq.com")
            print("   📁 如果收件箱没有，请检查垃圾邮件文件夹")
            return True
        else:
            print("   ❌ 邮件发送失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_email()
