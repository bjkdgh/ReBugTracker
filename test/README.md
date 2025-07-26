# ReBugTracker 测试脚本目录

本目录包含了ReBugTracker项目的各种测试和验证脚本，已按功能分类整理到不同子目录中。

## 📁 目录结构

### 📧 邮件通知测试 (`email_tests/`)
邮件通知系统的各种测试脚本
- 配置诊断和调试脚本
- SSL邮件功能测试
- 用户特定邮件测试

### 🔔 通知系统测试 (`notification_tests/`)
通知系统核心功能测试
- 应用内通知测试
- Gotify推送测试
- 通知界面测试
- 异步通知测试
- 通知流转规则测试

### 🎨 用户界面测试 (`ui_tests/`)
用户界面相关测试脚本
- 登录注册页面美化测试
- 主页布局优化测试
- 功能页面重设计测试

### 👑 管理员功能测试 (`admin_tests/`)
管理员相关功能测试
- 管理员问题管理测试
- 管理员界面样式测试
- 管理员页面JS修复测试

### 🧪 核心功能测试 (`core_tests/`)
应用核心功能测试
- 基础功能测试
- 问题管理测试
- 状态过滤测试
- 页面诊断测试

### 🧹 清理管理测试 (`cleanup_tests/`)
数据清理和管理功能测试
- 清理管理器测试
- 自动清理配置测试
- 清理统计测试
- 新功能演示

### ✅ 验证脚本 (`verification/`)
各种验证和检查脚本
- 管理员页面修改验证
- 背景一致性检查
- 透明背景修复验证

### 📦 归档目录 (`archive/`)
已完成使命的一次性脚本
- 历史配置更新脚本

## 🚀 使用方法

### 按类别运行测试
```bash
# 邮件通知测试
python test/email_tests/diagnose_email_config.py
python test/email_tests/test_fixed_ssl_email.py

# 通知系统测试
python test/notification_tests/test_notification_system.py
python test/notification_tests/simple_gotify_test.py

# 完整通知流转规则测试（三种通知方式）
python test_email_notification_real.py      # 邮件通知测试
python test_gotify_notification_real.py     # Gotify推送测试
python test_inapp_notification_real.py      # 应用内通知测试

# 界面测试
python test/ui_tests/test_beautiful_login.py
python test/ui_tests/test_index_layout.py

# 核心功能测试
python test/core_tests/test_simple.py
python test/core_tests/test_complete_bug.py

# 管理员功能测试
python test/admin_tests/test_admin_bugs.py

# 清理管理测试
python test/cleanup_tests/test_cleanup_manager.py

# 验证脚本
python test/verification/verify_admin_changes.py
```

## 📋 测试分类

### 🔧 功能测试
测试应用程序的核心功能，包括：
- 用户登录/注册
- 问题提交/管理
- 通知系统
- 状态过滤（包括驳回状态）
- 权限控制
- 问题状态转换（待处理→已分配→处理中→已解决→已完成）
- 驳回功能（负责人驳回待处理/已分配的问题）

### 🎯 界面测试
测试用户界面的视觉效果和交互，包括：
- 页面布局
- 样式一致性
- 响应式设计
- 用户体验

### 🔐 管理员测试
专门测试管理员功能，包括：
- 用户管理
- 问题管理
- 系统配置
- 数据统计

### 📢 通知测试
测试通知系统的各个方面，包括：
- 应用内通知
- 邮件通知
- Gotify通知
- 通知配置
- 通知流转规则验证

## 📋 测试环境要求

### 基础要求
- ReBugTracker应用正在运行（通常在localhost:5000）
- 数据库连接正常
- Python环境已安装所需依赖

### 特定测试要求
- **邮件测试**：需要配置邮件服务器
- **Gotify测试**：需要Gotify服务器配置
- **界面测试**：需要Web浏览器访问
- **管理员测试**：需要管理员用户账户

## ⚠️ 注意事项

- 建议在测试环境中运行，避免影响生产数据
- 某些测试需要特定用户存在于数据库中
- 测试脚本会输出详细的执行日志
- 注意查看错误信息和警告

## 🔧 故障排除

### 常见问题
1. **连接错误**：检查应用服务器是否运行
2. **认证失败**：确认测试用户账户存在
3. **邮件测试失败**：检查邮件服务器配置
4. **界面测试异常**：确认页面元素是否存在

## 🔔 通知流转规则完整测试

### 📋 测试脚本说明
项目根目录下有三个专门的通知测试脚本，用于验证完整的通知流转规则：

#### 📧 `test_email_notification_real.py`
**功能**: 测试邮件通知的实际发送
- 验证SMTP配置和连接
- 测试五个通知规则的邮件发送
- 支持多种邮箱服务商（163、QQ等）
- 验证邮件模板和优先级颜色

#### 🔔 `test_gotify_notification_real.py`
**功能**: 测试Gotify推送通知的实际发送
- 验证Gotify服务器连接
- 测试用户专属Token和全局Token
- 所有推送使用优先级10（最高）
- 支持个人Token回退到全局Token

#### 📱 `test_inapp_notification_real.py`
**功能**: 测试应用内通知的实际创建
- 验证数据库通知表操作
- 测试通知记录的创建和验证
- 提供通知统计信息
- 验证已读/未读状态

### 🎯 测试的五个通知规则

每个脚本都会测试以下完整的通知流转规则：

1. **规则1**: gh(实施组) 创建问题 → 通知 zjn(负责人)
2. **规则2**: zjn(负责人) 分配问题 → 通知 wbx(组内成员)
3. **规则3**: wbx(组内成员) 更新状态 → 通知 gh(创建者) + wbx(分配者)
4. **规则4**: wbx(组内成员) 解决问题 → 通知 gh(创建者) + zjn(负责人)
5. **规则5**: gh(实施组) 确认闭环 → 通知 gh(创建者) + wbx(分配者) + zjn(负责人)

### 📊 测试用户
- **gh(郭浩)**: 实施组用户，问题创建者和闭环确认者
- **zjn(张佳楠)**: 负责人，问题分配决策者
- **wbx(王柏翔)**: 组内成员，问题处理执行者

### 🚀 运行方法
```bash
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 分别测试三种通知方式
python test_email_notification_real.py      # 邮件通知
python test_gotify_notification_real.py     # Gotify推送
python test_inapp_notification_real.py      # 应用内通知
```

### ✅ 预期结果
- **邮件测试**: 9封邮件发送到3个不同邮箱
- **Gotify测试**: 9条推送通知（取决于Token配置）
- **应用内测试**: 9条通知记录写入数据库

### 💡 测试价值
- 验证通知系统的完整性和可靠性
- 确保所有通知渠道正常工作
- 验证通知流转规则的正确性
- 提供真实的端到端测试

---

**维护者**: ReBugTracker开发团队
**最后更新**: 2025-07-14
**版本**: 2.1（新增通知流转规则测试）
