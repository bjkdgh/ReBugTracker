# 数据库工具集

这个文件夹包含了ReBugTracker应用的通用数据库管理和维护工具。

## 🛠️ 工具列表

### 1. 数据检查工具

#### `check_sqlite_data.py`
**SQLite数据检查工具** - 快速查看SQLite数据库内容
- 检查表结构和数据统计
- 显示示例数据记录
- 验证数据关联关系
- 发现数据完整性问题

**使用方法**：
```bash
python database_tools/check_sqlite_data.py
```

**功能特点**：
- 📊 **数据统计**：显示用户数、问题数等统计信息
- 🔍 **示例数据**：显示前几条记录供快速检查
- 🔗 **关联检查**：验证外键关系的完整性
- ⚠️ **问题发现**：自动发现孤立记录等问题

### 2. 连接测试工具

#### `test_db_connection.py`
**数据库连接测试工具** - 测试各种数据库连接
- 测试当前配置的数据库连接
- 支持PostgreSQL和SQLite
- 执行基本查询验证
- 提供详细的连接诊断

**使用方法**：
```bash
python database_tools/test_db_connection.py
```

**功能特点**：
- 🔗 **多数据库支持**：PostgreSQL、SQLite
- 📋 **配置检查**：显示当前数据库配置
- 🧪 **查询测试**：执行基本查询验证连接
- 🔍 **详细诊断**：提供连接失败的详细信息

### 3. 表结构管理工具

#### `create_db_temp.py`
**数据库表结构更新工具** - 管理数据库表结构
- 添加新字段到现有表
- 更新数据映射关系
- 创建测试数据库
- 支持PostgreSQL和SQLite

**使用方法**：
```bash
python database_tools/create_db_temp.py
```

**功能特点**：
- 🔧 **结构更新**：安全地添加新字段
- 🔄 **数据映射**：自动更新中英文字段映射
- 🧪 **测试环境**：创建独立的测试数据库
- 🛡️ **安全操作**：使用IF NOT EXISTS避免重复操作

### 4. SQLite专用工具

#### `sqlite_optimizer.py`
**SQLite性能优化工具** - 专门优化SQLite数据库
- 性能参数优化（WAL模式、缓存等）
- 自动创建查询索引
- 数据库完整性检查
- 自动备份功能

**使用方法**：
```bash
python database_tools/sqlite_optimizer.py
```

**功能特点**：
- 🚀 **性能优化**：WAL模式、缓存优化、同步设置
- 📋 **索引管理**：自动创建常用查询索引
- 🔍 **完整性检查**：数据库和外键完整性验证
- 💾 **自动备份**：优化前自动创建备份

#### `sqlite_config_checker.py`
**SQLite配置检查工具** - 检查SQLite配置是否最优
- 检查PRAGMA设置
- 验证索引配置
- 检查db_factory和sql_adapter配置
- 提供优化建议

**使用方法**：
```bash
python database_tools/sqlite_config_checker.py
```

**功能特点**：
- 🔧 **配置检查**：全面检查SQLite配置参数
- 📊 **性能分析**：分析当前配置的性能影响
- 💡 **优化建议**：提供具体的优化建议
- ✅ **兼容性验证**：检查与应用代码的兼容性

#### `test_sqlite_login.py`
**SQLite登录功能测试工具** - 测试SQLite模式下的用户登录
- 测试多个用户的登录功能
- 验证页面访问权限
- 检查用户信息显示
- 验证SQLite兼容性修复

**使用方法**：
```bash
python database_tools/test_sqlite_login.py
```

**功能特点**：
- 🧪 **登录测试**：测试多个用户账户的登录功能
- 🔍 **页面验证**：验证登录后的页面访问
- 📊 **信息检查**：检查用户信息是否正确显示
- 🛠️ **兼容性验证**：确保SQLite模式下功能正常

### 5. 管理员工具

#### `fix_admin_data.py`
**admin用户数据修复工具** - 修复和初始化admin用户数据
- 重置admin用户密码
- 创建管理员级别的测试问题
- 验证admin用户功能
- 确保管理员权限正常

**使用方法**：
```bash
python database_tools/fix_admin_data.py
```

**功能特点**：
- 🔑 **密码重置**：重置admin密码为123456
- 📋 **问题创建**：创建管理员级别的测试问题
- ✅ **功能验证**：自动测试admin登录功能
- 🛡️ **权限确认**：确保管理员权限正确配置

#### `test_admin_access.py`
**admin权限测试工具** - 全面测试admin用户权限
- 测试admin登录功能
- 验证管理页面访问
- 测试用户管理API
- 验证问题管理权限

**使用方法**：
```bash
python database_tools/test_admin_access.py
```

**功能特点**：
- 🔐 **登录测试**：验证admin用户登录
- 🏠 **页面测试**：测试管理页面访问
- 👥 **用户管理**：测试用户管理API权限
- 🐛 **问题管理**：验证问题查看和管理权限

#### `test_admin_user_management.py`
**admin用户管理功能测试工具** - 测试用户管理界面的完整功能
- 测试用户列表显示中文姓名
- 测试添加用户包含中文姓名
- 测试编辑用户中文姓名
- 验证前后端API完整性

**使用方法**：
```bash
python database_tools/test_admin_user_management.py
```

**功能特点**：
- 📋 **用户列表**：验证用户列表显示中文姓名
- ➕ **添加用户**：测试添加包含中文姓名的新用户
- ✏️ **编辑用户**：测试编辑和更新用户中文姓名
- 🔄 **API测试**：全面测试用户管理API
- 🗃️ **数据库兼容**：支持PostgreSQL和SQLite模式

#### `test_ssz_functions.py`
**实施组用户功能测试工具** - 测试实施组用户的完整功能
- 测试实施组用户登录
- 验证功能按钮显示
- 测试问题提交功能
- 验证权限控制

**使用方法**：
```bash
python database_tools/test_ssz_functions.py
```

**功能特点**：
- 🔐 **登录测试**：测试实施组用户登录功能
- 🔘 **按钮验证**：验证"提交新问题"、"删除"、"确认闭环"按钮
- 📝 **提交测试**：测试问题提交完整流程
- 🛡️ **权限验证**：确保角色权限控制正确
- 👥 **多用户测试**：测试多个实施组用户账户

#### `test_bug_detail_navigation.py`
**问题详情页面跳转测试工具** - 测试详情页面的跳转功能
- 测试不同角色用户的详情页面访问
- 验证"查看详情"按钮显示和功能
- 测试详情页面内容正确性
- 验证错误处理机制

**使用方法**：
```bash
python database_tools/test_bug_detail_navigation.py
```

**功能特点**：
- 👥 **多角色测试**：测试实施组、组内成员、管理员的详情访问
- 🔘 **按钮验证**：验证"查看详情"按钮的显示和点击
- 📄 **页面验证**：检查详情页面内容的正确性
- 🛡️ **错误处理**：测试404等错误情况的处理
- 🔗 **链接测试**：验证详情页面链接的正确性

#### `test_bug_detail_assign.py`
**问题详情页面指派功能测试工具** - 测试详情页面中的指派功能
- 测试负责人在详情页面的指派按钮
- 验证指派页面跳转功能
- 测试权限控制的正确性
- 验证不同角色的访问权限

**使用方法**：
```bash
python database_tools/test_bug_detail_assign.py
```

**功能特点**：
- 🔘 **指派按钮**：验证负责人在详情页面可以看到指派按钮
- 🔗 **页面跳转**：测试从详情页面到指派页面的跳转
- 🛡️ **权限控制**：验证不同角色的指派权限控制
- 👥 **多角色测试**：测试负责人、实施组、组内成员的权限
- 📄 **页面验证**：检查详情页面和指派页面的内容正确性

## 🚀 使用场景

### 1. 日常维护
```bash
# 检查数据库状态
python database_tools/test_db_connection.py

# 查看数据内容
python database_tools/check_sqlite_data.py
```

### 2. 开发调试
```bash
# 创建测试环境
python database_tools/create_db_temp.py

# 验证数据完整性
python database_tools/check_sqlite_data.py
```

### 3. SQLite优化（推荐）
```bash
# 检查SQLite配置
python database_tools/sqlite_config_checker.py

# 优化SQLite性能
python database_tools/sqlite_optimizer.py
```

### 4. 部署前检查
```bash
# 测试数据库连接
python database_tools/test_db_connection.py

# 更新表结构
python database_tools/create_db_temp.py
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

## 🔧 配置说明

### 数据库配置
工具会自动读取项目的数据库配置：
```python
# 从config.py读取
DB_TYPE = 'sqlite'  # 或 'postgres'
DATABASE_CONFIG = {...}
```

### PostgreSQL连接
```python
PG_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5'
}
```

### SQLite路径
```python
# 默认路径：项目根目录/rebugtracker.db
db_path = '../rebugtracker.db'
```

## 📋 字段映射规则

### 角色映射（role -> role_en）
- 管理员 → gly
- 负责人 → fzr
- 组内成员 → zncy
- 实施组 → ssz

### 团队映射（team -> team_en）
- 网络分析 → wlfx
- 实施组 → ssz
- 第三道防线 → dsdfx
- 新能源 → xny
- 管理员 → gly
- 开发组 → dev

## ⚠️ 注意事项

1. **备份数据**：修改表结构前请备份数据
2. **权限检查**：确保有数据库读写权限
3. **连接测试**：操作前先测试数据库连接
4. **环境隔离**：使用测试数据库进行实验

## 🔄 与迁移工具的关系

这些工具与迁移工具配合使用：
- **迁移前**：使用连接测试和数据检查
- **迁移后**：使用数据验证和结构更新
- **日常维护**：使用数据检查和连接测试

## 🎯 故障排除

### 连接问题
1. 检查数据库服务是否运行
2. 验证连接参数是否正确
3. 确认网络连接是否正常
4. 检查防火墙设置

### 数据问题
1. 使用数据检查工具诊断
2. 检查外键关系完整性
3. 验证数据类型匹配
4. 查看错误日志详情

### 权限问题
1. 确认数据库用户权限
2. 检查文件系统权限
3. 验证目录访问权限
4. 查看系统日志

## 🔔 新增通知系统工具

### `create_notification_tables.py`
**PostgreSQL通知系统表创建工具** - 为PostgreSQL创建通知相关表

### `create_notification_tables_sqlite.py`
**SQLite通知系统表创建工具** - 为SQLite创建通知相关表

### `add_user_contact_fields.py`
**用户联系方式字段添加工具** - 为用户表添加联系方式字段

### `show_table_structure.py`
**数据库表结构查看工具** - 详细显示数据库表结构

### `compare_users_table.py`
**用户表数据对比工具** - 比较两个数据库的用户数据

### `comprehensive_db_check.py`
**综合数据库状态检查工具** - 全面检查数据库健康状态

## 🚀 推荐使用流程

```bash
# 1. 综合检查数据库状态
python database_tools/comprehensive_db_check.py

# 2. 如果需要创建通知系统表
python database_tools/create_notification_tables_sqlite.py

# 3. 检查数据一致性
python database_tools/compare_users_table.py
```

---

**这些工具帮助确保ReBugTracker数据库的稳定性和可靠性，特别支持新的通知系统功能。** 🎯
