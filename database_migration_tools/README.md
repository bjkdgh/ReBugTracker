# 数据库迁移工具集

本目录包含了ReBugTracker项目中PostgreSQL与SQLite数据库之间的迁移工具。这些工具支持双向数据同步，确保在不同数据库环境之间的无缝切换。

## 📁 工具概览

| 脚本名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `full_sync_postgres_to_sqlite.py` | 完整同步（表结构+数据） | 一键完成PostgreSQL到SQLite的完整迁移 |
| `sync_postgres_schema_to_sqlite.py` | 表结构同步 | 仅同步表结构，不包含数据 |
| `sync_postgres_data_to_sqlite.py` | 数据同步 | 在表结构已同步的基础上同步数据 |
| `sync_sqlite_to_postgres_data.py` | 反向数据同步 | 将SQLite数据同步回PostgreSQL |
| `verify_migration.py` | 迁移验证 | 验证数据迁移的完整性和正确性 |
| `inspect_postgres.py` | PostgreSQL检查 | 查看PostgreSQL数据库结构和数据 |
| `check_db_constraints.py` | 约束检查 | 检查并清理数据库约束问题 |
| `test_db_connection_new.py` | 连接测试 | 测试两个数据库的连接状态 |

## 🚀 快速开始

### 1. 环境准备

确保已安装必要的依赖：
```bash
pip install psycopg2-binary sqlite3
```

### 2. 配置检查

运行连接测试确保数据库配置正确：
```bash
python test_db_connection_new.py
```

### 3. 完整迁移（推荐）

如果是首次迁移或需要完全重建SQLite数据库：
```bash
python full_sync_postgres_to_sqlite.py
```

## 📋 详细工具说明

### 🔄 完整同步工具 (`full_sync_postgres_to_sqlite.py`)

**功能特点：**
- 自动备份现有SQLite数据库
- 重建表结构以匹配PostgreSQL
- 完整数据迁移
- 自动验证迁移结果

**执行流程：**
1. 备份现有SQLite数据库（格式：`rebugtracker.db.backup_YYYYMMDD_HHMMSS`）
2. 删除并重建所有表
3. 按依赖关系顺序同步数据：users → bugs → system_config → user_notification_preferences → notifications
4. 验证同步结果

**适用场景：**
- 首次从PostgreSQL迁移到SQLite
- 需要完全重建SQLite数据库
- 数据结构发生重大变化

### 🏗️ 表结构同步 (`sync_postgres_schema_to_sqlite.py`)

**功能特点：**
- 仅同步表结构，不涉及数据
- 删除现有表并重建
- 确保SQLite表结构与PostgreSQL完全一致

**支持的表：**
- `users` - 用户表
- `bugs` - 问题表  
- `system_config` - 系统配置表
- `user_notification_preferences` - 用户通知偏好表
- `notifications` - 通知表

**注意事项：**
⚠️ 此操作会删除SQLite中的所有现有数据！

### 📊 数据同步 (`sync_postgres_data_to_sqlite.py`)

**功能特点：**
- 要求表结构已同步
- 清空SQLite表数据后重新导入
- 保持数据关联关系完整性

**同步顺序：**
1. users（用户数据）
2. bugs（问题数据）
3. system_config（系统配置）
4. user_notification_preferences（通知偏好）
5. notifications（通知记录）

### 🔄 反向同步 (`sync_sqlite_to_postgres_data.py`)

**功能特点：**
- 将SQLite数据同步回PostgreSQL
- 保留PostgreSQL的system_config配置
- 自动更新PostgreSQL序列值
- 支持双数据库环境切换

**使用场景：**
- 从SQLite环境切换回PostgreSQL
- 将SQLite中的更新同步到PostgreSQL
- 双数据库环境的数据一致性维护

### ✅ 迁移验证 (`verify_migration.py`)

**验证内容：**
- 数据库文件存在性
- 表结构完整性
- 数据记录数量
- 关联关系正确性
- 用户数据完整性

**输出信息：**
- 各表记录统计
- 关键用户信息验证
- 数据关联关系检查
- 孤立记录检测

### 🔍 数据库检查工具

#### PostgreSQL检查 (`inspect_postgres.py`)
- 列出所有表
- 显示表结构（列名、数据类型、约束）
- 展示示例数据（每表最多5条）

#### 约束检查 (`check_db_constraints.py`)
- 检查SQLite表约束
- 发现并清理重复用户名
- 维护数据完整性

#### 连接测试 (`test_db_connection_new.py`)
- 测试PostgreSQL连接状态
- 测试SQLite连接状态
- 显示数据库基本信息
- 统计各表记录数量

## 🛠️ 使用最佳实践

### 迁移前准备
1. **备份数据**：确保重要数据已备份
2. **测试连接**：运行连接测试确保数据库可访问
3. **检查配置**：验证config.py中的数据库配置

### 迁移执行
1. **选择合适工具**：
   - 首次迁移：使用`full_sync_postgres_to_sqlite.py`
   - 仅更新结构：使用`sync_postgres_schema_to_sqlite.py`
   - 仅更新数据：使用`sync_postgres_data_to_sqlite.py`

2. **验证结果**：迁移完成后运行`verify_migration.py`

### 故障排除
- **连接失败**：检查数据库服务状态和网络连接
- **权限错误**：确保数据库用户有足够权限
- **数据不一致**：运行验证工具检查具体问题

## 📝 注意事项

1. **数据安全**：所有迁移操作都会自动创建备份
2. **依赖关系**：数据同步严格按照表依赖关系执行
3. **字符编码**：所有脚本使用UTF-8编码，支持中文数据
4. **事务处理**：每个表的迁移都在独立事务中执行
5. **错误处理**：提供详细的错误信息和堆栈跟踪

## 🔧 技术细节

### 数据类型映射
- PostgreSQL的SERIAL → SQLite的INTEGER PRIMARY KEY AUTOINCREMENT
- PostgreSQL的TIMESTAMP → SQLite的TIMESTAMP
- PostgreSQL的BOOLEAN → SQLite的BOOLEAN
- PostgreSQL的TEXT → SQLite的TEXT

### 主键处理
- 自增主键在SQLite中重新生成
- PostgreSQL序列值在反向同步时自动更新
- 保持数据关联关系的完整性

---

**维护者**: ReBugTracker开发团队  
**最后更新**: 2025-07-14  
**版本**: 1.0
