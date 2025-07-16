# ReBugTracker 一键部署指南

## 🚀 快速开始

### Linux/macOS 用户
```bash
# 运行一键部署脚本
chmod +x deploy.sh
./deploy.sh
```

### Windows 用户
```cmd
# 以管理员身份运行命令提示符，然后执行
deploy.bat
```

### 智能选择器 (推荐)
```bash
# 使用智能部署脚本选择器
python deploy.py
```

## 📋 脚本功能特性

| 功能特性 | 支持情况 |
|----------|----------|
| 部署方式选择 | ✅ Docker + 本地部署 |
| 数据库选择 | ✅ PostgreSQL + SQLite |
| 交互式配置 | ✅ 全程交互引导 |
| 虚拟环境隔离 | ✅ 完全隔离 |
| 自动依赖检查 | ✅ 智能检查 |
| 错误处理 | ✅ 详细错误提示 |
| 一键启动 | ✅ 自动生成启动脚本 |
| 跨平台支持 | ✅ Linux/macOS/Windows |

## 🎯 部署方式选择

### 1. Docker部署 (推荐)
**适用场景：**
- 生产环境部署
- 多环境管理
- 团队协作开发
- 避免环境依赖冲突

**优势：**
- ✅ 环境完全隔离
- ✅ 一键启动停止
- ✅ 跨平台一致性
- ✅ 易于扩展和维护

### 2. 本地部署
**适用场景：**
- 开发调试环境
- 性能要求高的场景
- 需要深度定制
- 资源受限环境

**优势：**
- ✅ 直接运行，性能最优
- ✅ 便于代码调试
- ✅ 使用虚拟环境隔离
- ✅ 资源占用更少

## 🗄️ 数据库选择

### SQLite (推荐新手)
```
适合场景：
• 团队规模 < 10人
• 并发用户 < 50
• 快速原型开发
• 简化运维需求

优势：
• 零配置，开箱即用
• 数据文件便于备份
• 无需额外数据库服务
```

### PostgreSQL (推荐生产)
```
适合场景：
• 团队规模 > 10人
• 并发用户 > 50
• 生产环境部署
• 需要高级数据库功能

优势：
• 高性能，支持大并发
• 企业级数据库功能
• 支持数据库集群
```

## 🔧 部署流程详解

### 增强版脚本部署流程

1. **环境检测**
   - 自动检测操作系统
   - 检查必要的系统依赖

2. **交互式选择**
   - 选择部署方式 (Docker/本地)
   - 选择数据库类型 (PostgreSQL/SQLite)

3. **环境准备**
   - Docker: 检查Docker环境
   - 本地: 安装系统依赖和Python环境

4. **配置生成**
   - 自动生成.env配置文件
   - 配置数据库连接参数
   - 生成安全密钥

5. **服务部署**
   - Docker: 启动容器服务
   - 本地: 创建虚拟环境，安装依赖

6. **数据库初始化**
   - 测试数据库连接
   - 创建数据库表结构

7. **启动脚本生成**
   - 生成便捷的启动脚本
   - 提供管理命令说明

## 📁 生成的文件说明

### 配置文件
- `.env` - 环境变量配置文件
- `start_rebugtracker.sh/.bat` - 启动脚本

### 目录结构
```
ReBugTracker/
├── .venv/                    # Python虚拟环境 (本地部署)
├── logs/                     # 日志目录
├── uploads/                  # 文件上传目录
├── data/                     # 数据目录 (SQLite)
├── .env                      # 环境配置文件
└── start_rebugtracker.*      # 启动脚本
```

## 🌐 访问应用

### 默认访问信息
- **访问地址**: http://localhost:5000
- **管理员账号**: admin
- **管理员密码**: admin

### 测试账号
| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin | 系统管理 |
| 负责人 | zjn | 123456 | 问题指派 |
| 实施组 | gh | 123456 | 问题提交 |
| 组内成员 | wbx | 123456 | 问题处理 |

## 🔧 服务管理

### Docker部署管理
```bash
# 启动服务
./start_rebugtracker.sh

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
./start_rebugtracker.sh

# 手动启动
source .venv/bin/activate
python rebugtracker.py

# Windows
start_rebugtracker.bat

# 手动启动
.venv\Scripts\activate.bat
python rebugtracker.py
```

## 🔍 故障排除

### 常见问题及解决方案

**1. Docker服务启动失败**
```bash
# 检查Docker状态
docker info

# Linux重启Docker
sudo systemctl restart docker

# Windows重启Docker Desktop
```

**2. 数据库连接失败**
```bash
# 检查PostgreSQL服务
sudo systemctl status postgresql  # Linux
net start postgresql-x64-15       # Windows

# 检查连接参数
cat .env | grep DATABASE_
```

**3. Python依赖安装失败**
```bash
# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

**4. 端口占用**
```bash
# 检查端口占用
lsof -i :5000                    # Linux/macOS
netstat -ano | findstr 5000      # Windows
```

## 📞 获取帮助

如果遇到问题：

1. 查看错误日志：`logs/rebugtracker.log`
2. 检查Docker日志：`docker-compose logs`
3. 参考故障排除指南
4. 联系技术支持

## 🎉 部署成功后

1. 访问 http://localhost:5000
2. 使用默认账号登录 (admin/admin)
3. 修改默认密码
4. 开始使用ReBugTracker！

---

**享受使用ReBugTracker！** 🚀
