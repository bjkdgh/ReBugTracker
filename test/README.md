# ReBugTracker 测试脚本目录

本目录包含了ReBugTracker项目的各种测试和验证脚本。这些脚本用于测试功能、验证界面、检查数据一致性等。

## 📁 目录结构

### 🧪 功能测试脚本
- `test_simple.py` - 基础功能测试
- `test_simple_check.py` - 简单检查测试
- `test_simple_index.py` - 首页功能测试
- `test_notification_system.py` - 通知系统测试
- `test_targeted_notification.py` - 定向通知测试
- `test_global_notification_switches.py` - 全局通知开关测试
- `test_status_filter.py` - 状态过滤功能测试

### 🎨 界面测试脚本
- `test_beautiful_login.py` - 登录页面美化测试
- `test_beautiful_registration.py` - 注册页面美化测试
- `test_enhanced_registration.py` - 增强注册页面测试
- `test_index_layout.py` - 首页布局测试
- `test_index_optimization.py` - 首页优化测试
- `test_navbar_removal.py` - 导航栏移除测试

### 👑 管理员界面测试
- `test_admin_bugs.py` - 管理员问题管理测试
- `test_admin_js_fix.py` - 管理员页面JS修复测试
- `test_admin_notification_ui.py` - 管理员通知界面测试
- `test_admin_style_consistency.py` - 管理员样式一致性测试
- `test_admin_visual_check.py` - 管理员视觉检查测试

### 🔔 通知界面测试
- `test_inapp_notification_ui.py` - 应用内通知界面测试

### ✅ 验证脚本
- `verify_admin_changes.py` - 验证管理员页面修改
- `verify_transparent_background.py` - 验证透明背景修复

### 🔍 检查脚本
- `check_background_consistency.py` - 检查背景一致性

## 🚀 使用方法

### 运行单个测试脚本
```bash
# 进入项目根目录
cd D:\app_data\repository\ReBugTracker

# 运行特定测试脚本
python test\test_simple.py
```

### 运行验证脚本
```bash
# 验证管理员页面修改
python test\verify_admin_changes.py

# 验证透明背景修复
python test\verify_transparent_background.py
```

### 运行检查脚本
```bash
# 检查背景一致性
python test\check_background_consistency.py
```

## 📋 测试分类

### 🔧 功能测试
测试应用程序的核心功能，包括：
- 用户登录/注册
- 问题提交/管理
- 通知系统
- 状态过滤
- 权限控制

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

## 📝 注意事项

1. **运行环境**：确保在项目根目录运行测试脚本
2. **依赖检查**：运行前确保所有依赖已安装
3. **数据库状态**：某些测试可能需要特定的数据库状态
4. **服务运行**：部分测试需要ReBugTracker服务正在运行

## 🛠️ 维护说明

- 新增测试脚本时，请遵循命名规范：`test_功能名称.py`
- 验证脚本使用：`verify_验证内容.py`
- 检查脚本使用：`check_检查内容.py`
- 更新此README文件以包含新脚本的说明

## 📊 测试覆盖范围

- ✅ 用户认证和授权
- ✅ 问题管理功能
- ✅ 通知系统
- ✅ 管理员功能
- ✅ 界面一致性
- ✅ 响应式设计
- ✅ 数据验证

---

**最后更新**: 2025年7月13日
**维护者**: ReBugTracker开发团队
