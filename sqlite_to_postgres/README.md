# SQLite到PostgreSQL数据迁移工具集

这个文件夹包含了SQLite到PostgreSQL数据迁移和维护工具。

## 🛠️ 工具列表

### 1. 数据迁移工具

#### `migrate_to_postgres.py`
**主要迁移工具** - 将SQLite数据迁移到PostgreSQL
- 创建PostgreSQL数据库表结构
- 迁移users表和bugs表的所有数据
- 自动处理数据类型转换和序列重置

**使用方法**：
```bash
python sqlite_to_postgres/migrate_to_postgres.py
```

### 2. 验证和检查工具

#### `test_db_connection.py`
**PostgreSQL连接测试工具** - 测试PostgreSQL数据库连接
- 验证PostgreSQL服务器连接
- 测试基本查询功能
- 显示数据统计

**使用方法**：
```bash
python sqlite_to_postgres/test_db_connection.py
```

#### `check_db_constraints.py`
**数据约束检查工具** - 检查PostgreSQL数据约束
- 检查表结构和约束
- 验证数据完整性
- 发现并报告约束违规

**使用方法**：
```bash
python sqlite_to_postgres/check_db_constraints.py
```

### 3. 辅助工具

#### `create_db_temp.py`
**PostgreSQL表结构创建工具** - 创建或更新PostgreSQL表结构
- 创建标准的表结构
- 添加必要的约束和索引
- 用于初始化或重置数据库

**使用方法**：
```bash
python sqlite_to_postgres/create_db_temp.py
```

## 🚀 迁移流程

### 第一步：准备工作
```bash
# 1. 确保SQLite数据库存在
ls -la bugtracker.db

# 2. 测试PostgreSQL连接
python sqlite_to_postgres/test_db_connection.py
```

### 第二步：执行迁移
```bash
# 3. 执行数据迁移
python sqlite_to_postgres/migrate_to_postgres.py
```

### 第三步：验证结果
```bash
# 4. 检查数据约束
python sqlite_to_postgres/check_db_constraints.py
```

## 📊 迁移特点

**数据处理**：
- ✅ **自动类型转换**：SQLite到PostgreSQL的数据类型映射
- ✅ **序列重置**：正确设置PostgreSQL的SERIAL序列
- ✅ **约束保持**：保持原有的数据约束和关系

**错误处理**：
- ✅ **连接验证**：迁移前验证数据库连接
- ✅ **事务安全**：使用事务确保数据一致性
- ✅ **错误报告**：详细的错误信息和日志

## 🔧 配置说明

### PostgreSQL连接配置
在需要的文件中修改以下配置：
```python
PG_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '$RFV5tgb',
    'host': '192.168.1.5'
}
```

### SQLite数据库路径
默认查找：`bugtracker.db`（在工具目录中）

## ⚠️ 注意事项

1. **备份数据**：迁移前请备份原始SQLite数据
2. **网络连接**：确保能连接到PostgreSQL服务器
3. **权限问题**：确保有创建表和插入数据的权限
4. **依赖包**：需要安装 `psycopg2` 和 `sqlite3`

## 🎯 使用场景

**适用于**：
- 从SQLite开发环境迁移到PostgreSQL生产环境
- 数据库类型升级
- 数据备份和恢复
- 开发环境同步

**不适用于**：
- 大型数据库（建议使用专业迁移工具）
- 复杂的数据转换需求
- 实时数据同步

## 🔄 与postgres_to_sqlite的关系

这个工具集与 `postgres_to_sqlite` 工具集互补：
- `postgres_to_sqlite`：PostgreSQL → SQLite
- `sqlite_to_postgres`：SQLite → PostgreSQL

可以实现双向数据迁移和同步。
