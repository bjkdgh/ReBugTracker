# PostgreSQL到SQLite数据迁移工具集

这个文件夹包含了完整的PostgreSQL到SQLite数据迁移和维护工具。

## 🛠️ 工具列表

### 1. 数据迁移工具

#### `migrate_to_sqlite.py`
**主要迁移工具** - 将PostgreSQL数据迁移到SQLite
- 创建SQLite数据库和表结构
- 迁移users表和bugs表的所有数据
- 自动处理数据类型转换

**使用方法**：
```bash
python postgres_to_sqlite/migrate_to_sqlite.py
```

#### `fix_migration_data.py`
**数据修复工具** - 修复迁移后的关联关系问题
- 重新建立用户ID映射关系
- 修复bugs表的外键关联
- 更新用户的完整信息（中文姓名等）
- 验证修复结果

**使用方法**：
```bash
python postgres_to_sqlite/fix_migration_data.py
```

### 2. 验证和检查工具

#### `verify_migration.py`
**迁移结果验证工具** - 全面验证迁移和修复结果
- 检查表结构和数据完整性
- 验证用户信息和关联关系
- 统计用户问题数据
- 生成详细的验证报告

**使用方法**：
```bash
python postgres_to_sqlite/verify_migration.py
```

#### `inspect_postgres.py`
**PostgreSQL数据检查工具** - 查看源数据库内容
- 列出所有表和表结构
- 显示示例数据
- 用于迁移前的数据分析

**使用方法**：
```bash
python postgres_to_sqlite/inspect_postgres.py
```

#### `test_db_connection.py`
**SQLite连接测试工具** - 测试SQLite数据库连接
- 验证数据库文件是否存在
- 测试基本查询功能
- 显示用户数量统计

**使用方法**：
```bash
python postgres_to_sqlite/test_db_connection.py
```

#### `check_db_constraints.py`
**数据约束检查工具** - 检查和清理数据约束问题
- 检查表结构和约束
- 发现并清理重复用户名
- 维护数据完整性

**使用方法**：
```bash
python postgres_to_sqlite/check_db_constraints.py
```

### 3. 辅助工具

#### `create_db_temp.py`
**临时数据库创建工具** - 创建测试用的临时数据库
- 用于测试和开发
- 创建基本的表结构

## 🚀 完整迁移流程

### 第一步：数据迁移
```bash
# 1. 检查PostgreSQL源数据
python postgres_to_sqlite/inspect_postgres.py

# 2. 执行数据迁移
python postgres_to_sqlite/migrate_to_sqlite.py
```

### 第二步：数据修复
```bash
# 3. 修复关联关系
python postgres_to_sqlite/fix_migration_data.py
```

### 第三步：验证结果
```bash
# 4. 验证迁移结果
python postgres_to_sqlite/verify_migration.py

# 5. 测试数据库连接
python postgres_to_sqlite/test_db_connection.py
```

## 📊 迁移结果

经过完整的迁移和修复流程后：

- ✅ **用户数据**：14个用户，包含完整的中文姓名和角色信息
- ✅ **问题数据**：12个问题，所有关联关系正确
- ✅ **数据完整性**：0个孤立问题，100%数据完整性
- ✅ **功能验证**：所有用户可正常登录，问题分配正确

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
默认创建在项目根目录：`rebugtracker.db`

## ⚠️ 注意事项

1. **备份数据**：迁移前请备份原始PostgreSQL数据
2. **网络连接**：确保能连接到PostgreSQL服务器
3. **权限问题**：确保有读取PostgreSQL和写入SQLite的权限
4. **依赖包**：需要安装 `psycopg2` 和 `sqlite3`

## 🎯 故障排除

如果遇到问题，按以下顺序检查：
1. 运行 `inspect_postgres.py` 检查源数据
2. 运行 `test_db_connection.py` 检查SQLite连接
3. 运行 `verify_migration.py` 检查迁移结果
4. 如有关联问题，运行 `fix_migration_data.py` 修复
