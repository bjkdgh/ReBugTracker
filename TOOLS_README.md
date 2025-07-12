# ReBugTracker 工具集总览

这个文档提供了ReBugTracker项目中所有工具和实用程序的完整概览。

## 📁 工具文件夹结构

```
ReBugTracker/
├── database_tools/          # 🗃️ 通用数据库工具
├── postgres_to_sqlite/      # 🔄 PostgreSQL到SQLite迁移工具
├── sqlite_to_postgres/      # 🔄 SQLite到PostgreSQL迁移工具
├── deployment_tools/        # 🚀 部署和运维工具
├── data_exports/           # 📊 数据导出文件
├── docs/                   # 📖 文档目录
└── logs/                   # 📝 日志文件
```

## 🛠️ 工具分类

### 1. 数据库管理工具 (`database_tools/`)

**用途**：日常数据库维护和管理
- `check_sqlite_data.py` - SQLite数据检查
- `test_db_connection.py` - 数据库连接测试
- `create_db_temp.py` - 表结构更新

**适用场景**：
- 🔍 数据库状态检查
- 🧪 开发环境测试
- 🔧 表结构维护

### 2. 数据迁移工具

#### PostgreSQL → SQLite (`postgres_to_sqlite/`)
**用途**：从PostgreSQL迁移到SQLite
- `migrate_to_sqlite.py` - 主迁移工具
- `fix_migration_data.py` - 数据修复工具
- `verify_migration.py` - 迁移验证工具
- `inspect_postgres.py` - PostgreSQL检查工具

#### SQLite → PostgreSQL (`sqlite_to_postgres/`)
**用途**：从SQLite迁移到PostgreSQL
- `migrate_to_postgres.py` - 主迁移工具
- `test_db_connection.py` - 连接测试
- `check_db_constraints.py` - 约束检查

**适用场景**：
- 🔄 数据库类型切换
- 📦 环境迁移（开发→生产）
- 💾 数据备份和恢复

### 3. 部署工具 (`deployment_tools/`)

**用途**：应用部署和运维
- `run_waitress.py` - 生产环境WSGI服务器

**适用场景**：
- 🏭 生产环境部署
- 🔧 性能优化
- 📊 服务监控

## 🚀 快速开始指南

### 新项目设置
```bash
# 1. 测试数据库连接
python database_tools/test_db_connection.py

# 2. 初始化数据库结构
python database_tools/create_db_temp.py

# 3. 检查数据状态
python database_tools/check_sqlite_data.py
```

### 数据迁移
```bash
# PostgreSQL → SQLite
python postgres_to_sqlite/migrate_to_sqlite.py
python postgres_to_sqlite/fix_migration_data.py
python postgres_to_sqlite/verify_migration.py

# SQLite → PostgreSQL
python sqlite_to_postgres/migrate_to_postgres.py
python sqlite_to_postgres/check_db_constraints.py
```

### 生产部署
```bash
# 使用Waitress部署
python deployment_tools/run_waitress.py
```

## 📋 工具选择指南

### 根据需求选择工具

#### 🔍 **数据检查需求**
- 查看SQLite数据 → `database_tools/check_sqlite_data.py`
- 测试数据库连接 → `database_tools/test_db_connection.py`
- 检查PostgreSQL → `postgres_to_sqlite/inspect_postgres.py`

#### 🔄 **数据迁移需求**
- 开发→生产 → `sqlite_to_postgres/`
- 生产→开发 → `postgres_to_sqlite/`
- 数据备份 → 任一迁移工具

#### 🚀 **部署需求**
- 开发环境 → `python rebugtracker.py`
- 生产环境 → `deployment_tools/run_waitress.py`
- 容器部署 → `docker-compose up`

#### 🔧 **维护需求**
- 表结构更新 → `database_tools/create_db_temp.py`
- 数据完整性 → `postgres_to_sqlite/verify_migration.py`
- 约束检查 → `sqlite_to_postgres/check_db_constraints.py`

## 🎯 最佳实践

### 1. 开发流程
```bash
# 开发环境设置
python database_tools/test_db_connection.py
python database_tools/create_db_temp.py
python rebugtracker.py  # 开发服务器
```

### 2. 部署流程
```bash
# 数据迁移（如需要）
python sqlite_to_postgres/migrate_to_postgres.py

# 生产部署
python deployment_tools/run_waitress.py
```

### 3. 维护流程
```bash
# 定期检查
python database_tools/check_sqlite_data.py
python database_tools/test_db_connection.py

# 数据备份
python postgres_to_sqlite/migrate_to_sqlite.py
```

## ⚠️ 重要提醒

### 数据安全
- 🔒 **备份优先**：任何操作前先备份数据
- 🧪 **测试环境**：先在测试环境验证
- 📝 **操作记录**：记录重要操作和变更

### 环境管理
- 🔧 **配置检查**：确认数据库配置正确
- 🌐 **网络连接**：验证数据库服务器连接
- 🔑 **权限验证**：确保有足够的操作权限

### 性能考虑
- 📊 **数据量**：大数据量迁移需要更多时间
- 🔄 **并发控制**：避免同时运行多个迁移工具
- 💾 **资源监控**：注意内存和磁盘使用情况

## 📞 获取帮助

### 查看详细文档
- `database_tools/README.md` - 数据库工具详细说明
- `postgres_to_sqlite/README.md` - PostgreSQL迁移工具
- `sqlite_to_postgres/README.md` - SQLite迁移工具
- `deployment_tools/README.md` - 部署工具说明

### 故障排除
1. 查看相应工具的README文档
2. 检查错误日志和输出信息
3. 验证数据库连接和权限
4. 确认工具依赖包已安装

### 工具更新
- 定期检查工具更新
- 关注新功能和改进
- 反馈使用问题和建议

---

**注意**：使用任何工具前，请先阅读相应的README文档，了解具体的使用方法和注意事项。
