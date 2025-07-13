# ReBugTracker

🐛 **现代化的Bug跟踪系统** - 基于Flask构建，支持PostgreSQL和SQLite双数据库模式

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特性

### 🔐 用户角色管理
- **管理员(gly)**: 系统管理、用户管理、全局权限
- **负责人(fzr)**: 问题指派、团队管理、状态跟踪
- **实施组(ssz)**: 问题提交、状态确认、问题删除
- **组内成员(zncy)**: 问题处理、状态更新、解决确认

### 📋 问题管理
- **问题提交**: 支持标题、描述、项目关联、图片附件
- **状态跟踪**: 待处理 → 已分配 → 处理中 → 已解决 → 已完成
- **智能分配**: 负责人可将问题分配给团队成员
- **权限控制**: 基于角色的精细化权限管理

### 🎯 界面功能
- **响应式设计**: 基于Bootstrap 5，支持移动端
- **中文界面**: 完全本土化的用户体验
- **实时反馈**: Ajax交互，无刷新操作
- **图片支持**: 问题截图上传和预览

### 🔔 通知系统
- **多渠道通知**: 邮件 + Gotify + 应用内通知
- **流转通知**: 问题创建、分配、解决等关键节点自动通知
- **智能推送**: 只通知流转参与者，避免信息干扰
- **管理控制**: 服务器级别和用户级别的通知开关
- **权限管理**: 管理员可统一管理所有用户的通知设置

## 🚀 快速开始

### 方式一：Docker Compose (推荐)

#### 1. 使用启动脚本 (最简单)

**Linux/macOS:**
```bash
./start.sh
```

**Windows (Docker环境):**
```cmd
start-docker.bat
```

#### 2. 手动部署

**PostgreSQL模式:**
```bash
# 克隆项目
git clone <repository-url>
cd ReBugTracker

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 DB_TYPE=postgres

# 启动服务
docker-compose up -d

# 访问应用
open http://localhost:5000
```

**SQLite模式:**
```bash
# 使用SQLite配置启动
docker-compose -f docker-compose.sqlite.yml up -d
```

### 方式二：本地开发

#### 使用虚拟环境 (推荐)

**Windows:**
```cmd
# 自动设置虚拟环境和依赖
setup_venv.bat

# 或手动设置
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
# 自动设置虚拟环境和依赖
./setup_venv.sh

# 或手动设置
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 启动应用

```bash
# 激活虚拟环境后
python rebugtracker.py

# 访问应用
open http://localhost:5000
```

### 方式三：Windows 传统部署

**适用场景**: Windows生产服务器，不使用Docker

**使用启动脚本:**
```cmd
start-windows-traditional.bat
```

**手动部署**: 详见 `DEPLOYMENT_GUIDE_WINDOWS_POSTGRES.md`
- PostgreSQL + Python + Nginx + Waitress
- Windows服务注册 (NSSM)
- 生产环境优化配置

## 🔧 技术栈

- **后端**: Python 3.9+, Flask 2.3+
- **数据库**: PostgreSQL 15+ / SQLite 3+
- **前端**: Bootstrap 5, jQuery, HTML5
- **部署**: Docker, Gunicorn, Nginx
- **存储**: 本地文件系统 (上传文件)

## 📁 项目结构

```
ReBugTracker/
├── 📄 rebugtracker.py              # 主应用文件
├── ⚙️ config.py                    # 配置文件 (数据库类型选择)
├── 🔌 db_factory.py               # 数据库连接工厂
├── 🔄 sql_adapter.py              # SQL语句适配器
├── 📋 requirements.txt            # Python依赖列表
├── 🚀 start.sh                    # Linux/macOS Docker启动脚本
├── 🚀 start-docker.bat            # Windows Docker启动脚本
├── 🚀 start-windows-traditional.bat # Windows传统部署启动脚本
├── 🚀 setup_venv.sh               # Linux/macOS虚拟环境设置脚本
├── 🚀 setup_venv.bat              # Windows虚拟环境设置脚本
├── 🐳 Dockerfile                  # Docker镜像构建文件
├── 🐳 docker-compose.yml          # PostgreSQL模式编排文件
├── 🐳 docker-compose.sqlite.yml   # SQLite模式编排文件
├── 📝 .env.example               # 环境变量配置示例
├── 🎨 static/                     # 静态资源目录
│   ├── css/                      # 样式文件
│   ├── js/                       # JavaScript文件
│   └── images/                   # 图片资源
├── 📄 templates/                  # Jinja2模板文件
│   ├── base.html                 # 基础模板
│   ├── index.html                # 首页模板
│   ├── login.html                # 登录页面
│   ├── submit.html               # 问题提交页面
│   ├── bug_detail.html           # 问题详情页面
│   ├── assign.html               # 问题指派页面
│   └── admin.html                # 管理员页面
├── 📁 uploads/                    # 上传文件存储目录
├── 📁 logs/                       # 日志文件目录
├── 🛠️ database_tools/             # 数据库工具和测试脚本
├── 🔔 notification/              # 通知系统模块
│   ├── __init__.py               # 通知系统初始化
│   ├── simple_notifier.py        # 简化通知处理器
│   ├── notification_manager.py   # 通知管理器
│   ├── flow_rules.py             # 流转通知规则
│   └── channels/                 # 通知渠道
│       ├── base.py               # 通知器基类
│       ├── email_notifier.py     # 邮件通知器
│       ├── gotify_notifier.py    # Gotify通知器
│       └── inapp_notifier.py     # 应用内通知器
└── 📚 docs/                       # 文档目录
```

## 🔑 默认账号

| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 管理员 | admin | admin | 系统管理、用户管理 |
| 负责人 | zjn | 123456 | 问题指派、团队管理 |
| 实施组 | gh | 123456 | 问题提交、状态确认 |
| 组内成员 | wbx | 123456 | 问题处理、状态更新 |

## 🐳 Docker 部署

### 环境变量配置

创建 `.env` 文件：
```bash
# 数据库类型
DB_TYPE=postgres  # 或 sqlite

# PostgreSQL配置
POSTGRES_PASSWORD=ReBugTracker2024
POSTGRES_DB=rebugtracker

# 应用配置
FLASK_ENV=production
TZ=Asia/Shanghai
```

### PostgreSQL模式
```bash
docker-compose up -d
```

### SQLite模式
```bash
docker-compose -f docker-compose.sqlite.yml up -d
```

### 查看日志
```bash
docker-compose logs -f app
```

### 停止服务
```bash
docker-compose down
```

## 🔧 开发指南

### 本地开发环境

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置数据库**
编辑 `config.py`：
```python
DB_TYPE = 'sqlite'  # 或 'postgres'
```

3. **启动开发服务器**
```bash
python rebugtracker.py
```

### 数据库工具

项目提供了丰富的数据库测试工具：

```bash
# 测试数据库连接
python database_tools/test_db_connection.py

# 测试用户功能
python database_tools/test_user_management.py

# 测试实施组功能
python database_tools/test_ssz_functions.py

# 测试负责人指派功能
python database_tools/test_bug_detail_assign.py
```

## 🚀 生产部署

### Windows + Nginx + Waitress
详见: `DEPLOYMENT_GUIDE_WINDOWS_POSTGRES.md`

### Linux + Docker
详见: `DEPLOYMENT.md`

### 性能优化建议

1. **数据库优化**
   - PostgreSQL: 配置连接池、索引优化
   - SQLite: 定期VACUUM、WAL模式

2. **应用优化**
   - 使用Gunicorn多进程
   - 配置Nginx反向代理
   - 启用gzip压缩

3. **监控建议**
   - 配置健康检查
   - 监控日志文件
   - 设置磁盘空间告警

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](../../issues) 页面
2. 创建新的 Issue
3. 查看项目文档

---

**ReBugTracker** - 让Bug跟踪变得简单高效 🚀

### sqlite_to_postgres/ 目录
*   `migrate_to_postgres.py`: 数据迁移脚本，将SQLite数据导入到PostgreSQL
*   `check_db_constraints.py`: 检查并清理PostgreSQL数据库约束问题
*   `test_db_connection.py`: PostgreSQL数据库连接测试模块
*   `create_db_temp.py`: 创建数据库表结构更新脚本

### postgres_to_sqlite/ 目录
*   `migrate_to_sqlite.py`: 数据迁移脚本，将PostgreSQL数据导入到SQLite
*   `check_db_constraints.py`: 检查并清理SQLite数据库约束问题
*   `test_db_connection.py`: SQLite数据库连接测试模块
*   `create_db_temp.py`: 创建SQLite数据库表结构脚本
