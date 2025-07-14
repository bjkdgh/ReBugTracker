# ReBugTracker 数据库工具集

本目录包含了用于管理和维护ReBugTracker数据库的核心工具脚本。经过优化整理，专注于数据库管理的核心功能。

## 🚀 快速开始

运行交互式工具选择界面：
```bash
python tool_index.py
```

## 📋 核心工具列表

### 1. 综合数据库检查
- **文件**: `comprehensive_db_check.py`
- **功能**: 全面检查数据库健康状态（推荐首选工具）
- **支持**: PostgreSQL + SQLite
- **用途**: 检查表结构、数据完整性、通知系统状态

**使用方法**：
```bash
python comprehensive_db_check.py
```

**功能特点**：
- 🔍 **全面检查**：表结构、数据完整性、通知系统状态
- 📊 **统计信息**：用户数、问题数、配置项统计
- 🔗 **关联验证**：检查外键关系和数据一致性
- ⚠️ **问题发现**：自动发现孤立记录和配置问题

### 2. 用户数据对比
- **文件**: `compare_users_table.py`
- **功能**: 比较PostgreSQL和SQLite的用户数据
- **支持**: 双数据库对比
- **用途**: 数据迁移验证、一致性检查

**使用方法**：
```bash
python compare_users_table.py
```

**功能特点**：
- 🔄 **双库对比**：同时连接PostgreSQL和SQLite进行对比
- 👥 **用户数据**：对比用户信息、角色、团队等字段
- 📊 **差异报告**：详细显示数据差异和不一致项
- ✅ **验证工具**：迁移后的数据一致性验证

### 3. 通用通知系统表创建
- **文件**: `create_notification_tables.py`
- **功能**: 为当前数据库创建通知系统表
- **支持**: PostgreSQL + SQLite（自动检测）
- **用途**: 初始化通知系统、添加通知功能

**使用方法**：
```bash
python create_notification_tables.py
```

**功能特点**：
- 🔧 **自动检测**：根据当前DB_TYPE自动选择SQL语法
- 📋 **完整表结构**：system_config、user_notification_preferences、notifications
- 🔗 **索引优化**：自动创建查询优化索引
- 🛡️ **安全操作**：使用IF NOT EXISTS避免重复创建

### 4. SQLite配置检查
- **文件**: `sqlite_config_checker.py`
- **功能**: 检查SQLite配置和优化建议
- **支持**: SQLite专用
- **用途**: 性能诊断、配置优化

**使用方法**：
```bash
python sqlite_config_checker.py
```

**功能特点**：
- 🔧 **配置检查**：全面检查SQLite配置参数
- 📊 **性能分析**：分析当前配置的性能影响
- 💡 **优化建议**：提供具体的优化建议
- ✅ **兼容性验证**：检查与应用代码的兼容性

### 5. SQLite优化工具
- **文件**: `sqlite_optimizer.py`
- **功能**: 优化SQLite数据库性能
- **支持**: SQLite专用
- **用途**: 数据库维护、性能提升

**使用方法**：
```bash
python sqlite_optimizer.py
```

**功能特点**：
- 🚀 **性能优化**：WAL模式、缓存优化、同步设置
- 📋 **索引管理**：自动创建常用查询索引
- 🔍 **完整性检查**：数据库和外键完整性验证
- 💾 **自动备份**：优化前自动创建备份

### 6. 交互式工具界面
- **文件**: `tool_index.py`
- **功能**: 提供友好的工具选择界面
- **支持**: 所有工具
- **用途**: 统一工具入口

**使用方法**：
```bash
python tool_index.py
```

**功能特点**：
- 🎯 **统一入口**：一个界面访问所有工具
- 📋 **工具菜单**：清晰的工具分类和描述
- 🔧 **交互执行**：选择工具后自动执行
- ✅ **结果反馈**：显示工具执行结果和状态

## 📁 归档工具

`archive/` 目录包含已完成使命的一次性数据修复脚本：
- `add_gotify_user_token.py` - 添加Gotify用户令牌
- `add_user_contact_fields.py` - 添加用户联系方式字段
- `clean_timestamp_precision.py` - 清理时间戳精度
- `create_db_temp.py` - 临时数据库结构更新
- `fix_admin_data.py` - 修复管理员数据
- `update_system_config_descriptions.py` - 更新系统配置描述

这些脚本已归档保存，通常不需要再次运行，但保留以供参考。

## 🔧 使用指南

### 日常维护
1. **健康检查**: 定期运行 `comprehensive_db_check.py`
2. **性能优化**: SQLite环境下运行 `sqlite_optimizer.py`
3. **数据验证**: 双数据库环境使用 `compare_users_table.py`

### 系统初始化
1. **通知系统**: 运行 `create_notification_tables.py`
2. **配置检查**: SQLite环境运行 `sqlite_config_checker.py`

### 故障排除
1. 运行 `comprehensive_db_check.py` 获取详细状态
2. 检查数据库连接配置
3. 查看具体错误信息进行针对性修复

## 🚀 使用场景

### 1. 日常维护
```bash
# 综合检查数据库状态（推荐）
python comprehensive_db_check.py

# SQLite性能优化
python sqlite_optimizer.py
```

### 2. 系统初始化
```bash
# 创建通知系统表
python create_notification_tables.py

# 检查SQLite配置
python sqlite_config_checker.py
```

### 3. 数据验证
```bash
# 双数据库用户数据对比
python compare_users_table.py
```

## 📊 数据库支持

### SQLite
- ✅ **文件数据库**：`rebugtracker.db`
- ✅ **开发环境**：适合开发和测试
- ✅ **轻量级**：无需额外服务器
- ✅ **便携性**：易于备份和迁移

### PostgreSQL
- ✅ **服务器数据库**：适合生产环境
- ✅ **高性能**：支持并发访问
- ✅ **功能丰富**：完整的SQL支持
- ✅ **可扩展**：适合大型应用

## ⚠️ 注意事项

- **数据安全**: 重要操作前请备份数据库
- **环境检查**: 确保数据库配置正确
- **权限要求**: 某些操作需要数据库管理员权限
- **版本兼容**: 工具支持项目当前使用的数据库版本

## 🔗 相关工具

- **数据迁移工具**: 参见 `database_migration_tools/` 目录
- **应用测试工具**: 参见 `test/` 目录
- **部署工具**: 参见 `deployment_tools/` 目录

## 🎯 推荐使用流程

```bash
# 1. 综合检查数据库状态（首选）
python comprehensive_db_check.py

# 2. 如果需要创建通知系统表
python create_notification_tables.py

# 3. SQLite环境性能优化
python sqlite_config_checker.py
python sqlite_optimizer.py

# 4. 双数据库环境数据对比
python compare_users_table.py
```

---

**维护者**: ReBugTracker开发团队
**最后更新**: 2025-07-14
**工具版本**: 2.0（优化版）
