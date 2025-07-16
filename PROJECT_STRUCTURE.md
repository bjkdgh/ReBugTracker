# ReBugTracker 项目结构说明

## 📁 项目目录结构

```
ReBugTracker/
├── 📋 部署相关
│   ├── deploy.sh                    # Linux/macOS 一键部署脚本
│   ├── deploy.bat                   # Windows 一键部署脚本
│   ├── deploy.py                    # 智能部署脚本选择器
│   ├── docker-compose.yml          # PostgreSQL Docker配置
│   ├── docker-compose.sqlite.yml   # SQLite Docker配置
│   └── Dockerfile                  # Docker镜像构建文件
│
├── 📚 文档
│   ├── README.md                    # 项目主文档
│   ├── README_DEPLOYMENT.md        # 部署使用指南
│   ├── DEPLOYMENT_GUIDE_ENHANCED.md # 详细部署指南
│   └── WORKFLOW_ROLES.md           # 工作流程和角色说明
│
├── 🔧 核心应用
│   ├── rebugtracker.py             # 主应用入口
│   ├── config.py                   # 配置文件
│   ├── db_factory.py               # 数据库工厂
│   ├── sql_adapter.py              # SQL适配器
│   └── requirements.txt            # Python依赖包
│
├── 🗄️ 数据库工具
│   ├── database_tools/             # 数据库管理工具
│   │   ├── sqlite_optimizer.py     # SQLite优化工具
│   │   ├── comprehensive_db_check.py # 数据库检查工具
│   │   └── create_notification_tables.py # 通知表创建
│   └── database_migration_tools/   # 数据库迁移工具
│       ├── sync_postgres_to_sqlite.py # PG到SQLite同步
│       └── sync_sqlite_to_postgres_data.py # SQLite到PG同步
│
├── 🔔 通知系统
│   └── notification/               # 通知模块
│       ├── notification_manager.py # 通知管理器
│       ├── simple_notifier.py      # 简单通知器
│       └── channels/               # 通知渠道
│
├── 🎨 前端资源
│   ├── templates/                  # HTML模板
│   │   ├── base.html              # 基础模板
│   │   ├── index.html             # 首页
│   │   ├── bug_detail.html        # 问题详情
│   │   └── admin.html             # 管理页面
│   └── static/                     # 静态资源
│       ├── css/                   # 样式文件
│       ├── js/                    # JavaScript文件
│       └── RBT.ico               # 网站图标
│
├── 🧪 测试套件
│   └── test/                      # 测试文件
│       ├── core_tests/            # 核心功能测试
│       ├── notification_tests/    # 通知系统测试
│       └── ui_tests/              # 界面测试
│
├── 🚀 部署工具
│   └── deployment_tools/          # 部署辅助工具
│       └── run_waitress.py        # Waitress服务器启动
│
├── 📊 数据目录
│   ├── logs/                      # 日志文件
│   ├── uploads/                   # 文件上传目录
│   └── data_exports/              # 数据导出目录
│
└── 🔧 配置文件
    ├── .env                       # 环境变量配置 (部署时生成)
    ├── nginx.conf                 # Nginx配置示例
    └── package.json               # 前端依赖配置
```

## 📋 核心文件说明

### 部署脚本
- **deploy.sh/deploy.bat** - 主要的一键部署脚本，支持交互式选择
- **deploy.py** - 智能部署脚本选择器，帮助用户选择合适的部署方式

### 核心应用文件
- **rebugtracker.py** - Flask应用主入口，包含路由和业务逻辑
- **config.py** - 数据库和应用配置管理
- **db_factory.py** - 数据库连接工厂，支持PostgreSQL和SQLite

### 配置文件
- **.env** - 环境变量配置文件（部署脚本自动生成）
- **requirements.txt** - Python依赖包列表
- **docker-compose.yml** - Docker容器编排配置

### 数据库工具
- **database_tools/** - 数据库管理和优化工具集
- **database_migration_tools/** - 数据库迁移和同步工具

### 通知系统
- **notification/** - 多渠道通知系统模块
- 支持邮件、Gotify推送、应用内通知

## 🎯 使用建议

### 新用户
1. 直接运行 `deploy.sh` (Linux/macOS) 或 `deploy.bat` (Windows)
2. 按提示选择部署方式和数据库类型
3. 等待自动部署完成

### 开发者
1. 查看 `test/` 目录了解测试结构
2. 使用 `database_tools/` 中的工具进行数据库管理
3. 参考 `templates/` 和 `static/` 进行前端开发

### 运维人员
1. 使用 `deployment_tools/` 中的工具进行生产部署
2. 参考 `nginx.conf` 配置反向代理
3. 使用 `database_migration_tools/` 进行数据迁移

## 📞 获取帮助

- 部署问题：查看 `README_DEPLOYMENT.md`
- 详细配置：查看 `DEPLOYMENT_GUIDE_ENHANCED.md`
- 工作流程：查看 `WORKFLOW_ROLES.md`
- 技术问题：查看 `test/` 目录中的测试用例

---

**项目结构清晰，文档完整，开箱即用！** 🚀
