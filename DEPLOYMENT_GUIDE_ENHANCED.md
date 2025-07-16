# ReBugTracker 增强版一键部署指南

## 🚀 概述

本项目提供了两个增强版一键部署脚本，支持多种部署方式和数据库选择，真正做到0基础无需额外配置的交互式安装。

## 📦 部署脚本对比

| 特性 | Linux/macOS (deploy_enhanced.sh) | Windows (deploy_windows.bat) |
|------|----------------------------------|-------------------------------|
| 部署方式选择 | ✅ Docker / 本地部署 | ✅ Docker / 本地部署 |
| 数据库选择 | ✅ PostgreSQL / SQLite | ✅ PostgreSQL / SQLite |
| 自动依赖安装 | ✅ 完全自动化 | ✅ 检查并引导安装 |
| 虚拟环境隔离 | ✅ Python venv | ✅ Python venv |
| 交互式配置 | ✅ 全程引导 | ✅ 全程引导 |
| 错误处理 | ✅ 详细提示 | ✅ 详细提示 |
| 一键启动 | ✅ 自动生成启动脚本 | ✅ 自动生成启动脚本 |

## 🐧 Linux/macOS 部署

### 快速开始

```bash
# 1. 下载并运行部署脚本
chmod +x deploy_enhanced.sh
./deploy_enhanced.sh
```

### 支持的系统
- Ubuntu 18.04+
- CentOS 7+
- macOS 10.15+

### 部署流程
1. **选择部署方式**
   - Docker部署 (推荐)
   - 本地部署

2. **选择数据库类型**
   - SQLite (适合小团队)
   - PostgreSQL (适合生产环境)

3. **自动化安装**
   - 系统依赖自动安装
   - Python环境自动配置
   - 数据库自动配置

4. **一键启动**
   - 自动生成启动脚本
   - 支持后台运行

## 🪟 Windows 部署

### 快速开始

```cmd
# 1. 以管理员身份运行命令提示符
# 2. 运行部署脚本
deploy_windows.bat
```

### 支持的系统
- Windows 10 1903+
- Windows 11
- Windows Server 2019+

### 前置要求检查
脚本会自动检查并引导安装：
- Python 3.8+ (如未安装会提供下载链接)
- Docker Desktop (如选择Docker部署)
- PostgreSQL (如选择PostgreSQL本地部署)

### 部署流程
1. **环境检查**
   - 自动检查Python环境
   - 检查Docker环境(如选择)
   - 检查PostgreSQL环境(如选择)

2. **交互式配置**
   - 部署方式选择
   - 数据库类型选择
   - 数据库连接配置

3. **自动化部署**
   - 虚拟环境创建
   - 依赖包安装
   - 配置文件生成

## 🗄️ 数据库选择指南

### SQLite (推荐新手)
**适用场景：**
- 团队规模 < 10人
- 并发用户 < 50
- 快速原型开发
- 简化运维需求

**优势：**
- ✅ 零配置，开箱即用
- ✅ 数据文件便于备份
- ✅ 无需额外数据库服务

### PostgreSQL (推荐生产)
**适用场景：**
- 团队规模 > 10人
- 并发用户 > 50
- 生产环境部署
- 需要高级数据库功能

**优势：**
- ✅ 高性能，支持大并发
- ✅ 企业级数据库功能
- ✅ 支持数据库集群

## 🐳 Docker vs 本地部署

### Docker部署 (推荐)
**优势：**
- ✅ 环境隔离，避免依赖冲突
- ✅ 一键启动，易于管理
- ✅ 支持快速扩展
- ✅ 跨平台一致性

**适用场景：**
- 生产环境部署
- 多环境管理
- 团队协作开发

### 本地部署
**优势：**
- ✅ 直接运行，性能最优
- ✅ 便于开发调试
- ✅ 使用虚拟环境隔离
- ✅ 资源占用更少

**适用场景：**
- 开发环境
- 性能要求高的场景
- 需要深度定制

## 🔧 部署后管理

### 启动服务
```bash
# Linux/macOS
./start_rebugtracker.sh

# Windows
start_rebugtracker.bat
```

### Docker管理命令
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

### 本地部署管理
```bash
# Linux/macOS
source .venv/bin/activate
python rebugtracker.py

# Windows
.venv\Scripts\activate.bat
python rebugtracker.py
```

## 🌐 访问应用

### 默认访问信息
- **访问地址**: http://localhost:5000
- **管理员账号**: admin
- **管理员密码**: admin

### 默认测试账号
| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 管理员 | admin | admin | 系统管理、用户管理 |
| 负责人 | zjn | 123456 | 问题指派、团队管理 |
| 实施组 | gh | 123456 | 问题提交、状态确认 |
| 组内成员 | wbx | 123456 | 问题处理、状态更新 |

## 🔍 故障排除

### 常见问题

**1. Docker服务启动失败**
```bash
# 检查Docker状态
docker info

# 重启Docker服务 (Linux)
sudo systemctl restart docker

# Windows: 重启Docker Desktop
```

**2. 数据库连接失败**
```bash
# PostgreSQL服务检查 (Linux)
sudo systemctl status postgresql

# Windows服务检查
net start postgresql-x64-15
```

**3. Python依赖安装失败**
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt
```

**4. 端口占用问题**
```bash
# Linux/macOS
lsof -i :5000

# Windows
netstat -ano | findstr 5000
```

### 日志查看
```bash
# 应用日志
tail -f logs/rebugtracker.log

# Docker日志
docker-compose logs -f app
```

## 📞 技术支持

如果遇到问题，请按以下步骤排查：

1. 检查系统要求是否满足
2. 确认网络连接正常
3. 查看错误日志信息
4. 参考故障排除指南
5. 联系技术支持

---

**🎉 享受使用 ReBugTracker！**
