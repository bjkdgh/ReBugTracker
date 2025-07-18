# ReBugTracker - 企业级缺陷跟踪系统

![ReBugTracker Logo](static/rbt_title.ico)

## 📋 项目简介

**ReBugTracker** 是一个基于 Flask 框架开发的现代化企业级缺陷跟踪系统，专为团队协作和问题管理而设计。系统采用模块化架构，支持多数据库部署，具备完整的用户权限管理、智能通知系统和数据分析功能。

### 🌟 核心特性

- 🔐 **多角色权限管理** - 管理员、负责人、组内成员、实施组四级权限体系
- 📊 **智能问题分配** - 基于产品线自动分配，支持手动调整
- 🔔 **多渠道通知系统** - 邮件、Gotify推送、应用内通知三重保障
- 📈 **数据可视化分析** - 交互式图表，支持多种导出格式
- 🗄️ **多数据库支持** - PostgreSQL/SQLite 可配置切换
- 📱 **响应式设计** - 完美适配桌面端和移动端

## 🚀 快速开始

### 一键部署（推荐）

#### Windows 用户
```cmd
# 以管理员身份运行命令提示符
deploy.bat
```

#### Linux/macOS 用户
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 智能选择器
```bash
python deploy.py
```

### 手动部署

#### 1. 环境准备
```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 克隆项目
git clone https://github.com/your-repo/ReBugTracker.git
cd ReBugTracker

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 启动应用
```bash
# 直接启动（使用 SQLite）
python rebugtracker.py

# 或使用 Docker
docker-compose up -d
```

### 访问应用
- **地址**: http://localhost:5000
- **管理员**: admin / admin

## 📖 详细文档

- **[完整部署指南](DEPLOYMENT_GUIDE.md)** - 包含所有部署方式的详细说明
- **[数据库工具](database_tools/README.md)** - 数据库管理和维护工具
- **[通知系统](docs/notification_priority_system_guide.md)** - 通知系统配置指南

## 🏗️ 技术栈

| 组件 | 技术选型 | 版本要求 |
|------|----------|----------|
| 后端框架 | Flask | >= 2.0 |
| 数据库 | PostgreSQL / SQLite | >= 12.0 / >= 3.35 |
| 前端框架 | Bootstrap | 5.x |
| 图表库 | Chart.js | >= 3.0 |
| Python | Python | >= 3.8 |

## 🛠️ 项目工具

- **数据库工具** (`database_tools/`) - 数据库管理和维护
- **部署工具** (`deployment_tools/`) - 跨平台部署支持
- **测试套件** (`test/`) - 完整的测试覆盖
- **跨平台打包** (`cross_platform_build/`) - Windows/macOS/Linux打包

## 👥 用户角色

| 角色 | 权限说明 |
|------|----------|
| 管理员 | 系统全权管理、用户管理、数据报表 |
| 负责人 | 问题分配、团队管理、状态监控 |
| 组内成员 | 问题处理、状态更新、解决方案提交 |
| 实施组 | 问题提交、进度跟踪、状态查询 |

## 🔔 通知系统

- **邮件通知** - SMTP邮件推送
- **Gotify推送** - 移动端实时通知
- **应用内通知** - 系统内置消息中心

## 📊 数据分析

- **交互式图表** - 折线图、柱状图、饼状图
- **多维度统计** - 按人员、产品线、时间分析
- **导出功能** - Excel数据导出、图表导出

## 🔧 环境要求

- **Python**: 3.8+
- **数据库**: PostgreSQL 12+ 或 SQLite 3.35+
- **内存**: 4GB+ RAM
- **存储**: 10GB+ 磁盘空间

## 📞 技术支持

- **项目地址**: https://github.com/bjkdgh/ReBugTracker
- **问题反馈**: 提交 GitHub Issue
- **详细文档**: 查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**ReBugTracker** - 让缺陷跟踪更简单、更高效！ 🚀


