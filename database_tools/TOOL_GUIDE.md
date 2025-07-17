# 🔧 新增工具快速使用指南

> 📖 完整的工具介绍和对比请查看 [README.md](README.md)

## 🚀 快速启动新工具

### 方式1: 通过工具索引（推荐）
```bash
python database_tools/tool_index.py
```
选择 "2. 🔍 数据库检查工具"，然后选择对应的新工具：
- 选项3: PostgreSQL详细检查 🆕
- 选项4: SQLite详细检查 🆕
- 选项5: 结构验证工具 🆕

### 方式2: 直接运行
```bash
# PostgreSQL详细结构分析
python database_tools/check_tools/postgres_structure_inspector.py

# SQLite详细结构分析
python database_tools/check_tools/sqlite_structure_inspector.py

# 数据库结构验证
python database_tools/check_tools/database_structure_validator.py
```

## 🎯 常用工作流程

### 📊 日常检查流程
```bash
# 1. 快速验证结构规范性
python database_tools/check_tools/database_structure_validator.py

# 2. 如果发现问题，进行详细分析
python database_tools/check_tools/postgres_structure_inspector.py
python database_tools/check_tools/sqlite_structure_inspector.py
```

### 🔍 深度分析流程
```bash
# 1. 先做基础对比
python database_tools/check_tools/table_structure_checker.py

# 2. 再做单库详细分析
python database_tools/check_tools/postgres_structure_inspector.py
python database_tools/check_tools/sqlite_structure_inspector.py
```

### 🚀 部署验证流程
```bash
# 1. 结构验证
python database_tools/check_tools/database_structure_validator.py

# 2. 状态检查
python database_tools/check_tools/sync_status_checker.py

# 3. 如有问题，详细分析
python database_tools/check_tools/postgres_structure_inspector.py
```

## 💡 使用技巧

### 输出重定向
```bash
# 保存检查结果到文件
python database_tools/check_tools/postgres_structure_inspector.py > pg_structure.txt
python database_tools/check_tools/sqlite_structure_inspector.py > sqlite_structure.txt
```

### 结合使用
```bash
# 先验证，再详细分析
python database_tools/check_tools/database_structure_validator.py && \
python database_tools/check_tools/postgres_structure_inspector.py
```

## ⚠️ 注意事项

1. **数据库连接**: 确保PostgreSQL服务正在运行且配置正确
2. **虚拟环境**: 建议在虚拟环境中运行工具
3. **权限**: 确保有足够的数据库访问权限
4. **路径**: 从项目根目录运行工具以确保路径正确

## 🆘 常见问题

**Q: PostgreSQL连接失败怎么办？**
A: 检查config.py中的连接配置，确认PostgreSQL服务状态

**Q: SQLite文件找不到怎么办？**
A: 确认rebugtracker.db文件在项目根目录

**Q: 工具输出太多信息怎么办？**
A: 使用输出重定向保存到文件，或者使用grep过滤关键信息
