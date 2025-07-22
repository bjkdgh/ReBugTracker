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
- 🐳 **Docker 支持** - 一键容器化部署，支持多架构
- 🔧 **智能诊断** - 内置 Docker 环境诊断工具
- ⚡ **现代包管理** - 支持 uv 超快速依赖管理
- 📦 **离线部署** - 完整的离线环境部署方案
- ⚡ **现代包管理** - 支持 uv 超快速依赖管理
- 📦 **离线部署** - 完整的离线环境部署方案

## 🚀 快速开始

### ⚡ 现代化部署（推荐）- 使用 uv 包管理器
```bash
# 1. 自动设置 uv 环境（一键完成所有配置）
python uv_setup.py

# 2. 运行应用
uv run python rebugtracker.py

# 3. 创建离线部署包
python create_offline_package.py
```

### 🎯 智能部署选择器（推荐新手）
```bash
# 自动检测系统并推荐最佳部署方式
# Windows 用户特别推荐，因为主目录没有 deploy.bat
python deploy.py
```

### 📦 一键部署脚本

#### Linux/macOS 用户
```bash
# 方式1: 使用主目录的一键部署
chmod +x deploy.sh
./deploy.sh

# 方式2: 🔧 Docker 环境诊断
./deploy.sh --diagnose  # 诊断 Docker 环境问题
./deploy.sh --help      # 查看帮助信息

# 方式3: 快速 Docker 启动
chmod +x start_rebugtracker.sh
./start_rebugtracker.sh
```

#### Windows 用户
```cmd
# ⚠️ 注意：主目录没有 deploy.bat，需要使用以下方式：

# 方式1: 使用专业构建系统（推荐）
cd cross_platform_build\windows
deploy.bat

# 方式2: VBS 后台启动（需要先配置路径）
# 编辑 start_rebugtracker.vbs 中的项目路径
wscript.exe start_rebugtracker.vbs

# 方式3: 使用 Waitress 生产服务器
python deployment_tools\run_waitress.py
```

### 🏗️ 跨平台构建部署

#### Windows 构建部署
```cmd
# 进入 Windows 构建目录
cd cross_platform_build\windows

# 🔨 构建可执行文件（生成 dist 目录）
# 方式1: 新构建系统（推荐）
python build_windows.py

# 方式2: 传统构建系统
python build_exe.py

# 🚀 部署运行（不生成 dist 目录）
# 方式3: 一键部署脚本（Docker/本地/VBS 三种模式）
deploy.bat
```

#### macOS 构建部署
```bash
# 方式1: 使用修复版构建脚本（推荐）
cd cross_platform_build/macos
python build_macos_fixed.py

# 方式2: 使用调用脚本
cd cross_platform_build
python build_macos.py

# 方式3: 通用构建脚本
cd cross_platform_build
python build_universal.py
```

#### Linux 构建部署
```bash
# 方式1: Linux 专用构建
cd cross_platform_build
python build_linux.py

# 方式2: 通用构建脚本
python build_universal.py
```

### 手动部署

#### 方式1：使用 uv 包管理器（推荐）
```bash
# 1. 安装 uv
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone https://github.com/bjkdgh/ReBugTracker.git
cd ReBugTracker

# 3. 自动设置环境（推荐）
python uv_setup.py

# 或手动设置
uv sync
```

#### 方式2：传统 pip 方式
```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 克隆项目
git clone https://github.com/bjkdgh/ReBugTracker.git
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
# 使用 uv 启动（推荐）
uv run python rebugtracker.py

# 传统方式启动
python rebugtracker.py

# 或使用 Docker (SQLite 模式)
docker-compose -f docker-compose.sqlite.yml up -d

# 或使用 Docker (PostgreSQL 模式)
docker-compose up -d
```

### 🌐 访问应用

#### 默认访问地址
- **Docker 部署**: http://localhost:10001
- **本地部署**: http://localhost:5000
- **Windows EXE**: http://localhost:5000 (可配置)
- **macOS APP**: http://localhost:10001 (可配置)

#### 默认管理员账户
- **用户名**: admin
- **密码**: admin

### ⚙️ 配置修改方法

#### 🐳 Docker 部署配置
```bash
# 修改端口映射
# 编辑 docker-compose.sqlite.yml 或 docker-compose.yml
ports:
  - "新端口:5000"  # 例如 "8080:5000"

# 修改环境变量
# 在 docker-compose 文件中添加：
environment:
  - SERVER_HOST=0.0.0.0
  - SERVER_PORT=5000
  - DATABASE_URL=sqlite:///rebugtracker.db

# 重启服务应用配置
docker-compose -f docker-compose.sqlite.yml down
docker-compose -f docker-compose.sqlite.yml up -d
```

#### 💻 本地部署配置
```bash
# 方式1: 修改 .env 文件（推荐）
# 创建或编辑项目根目录的 .env 文件
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
DATABASE_URL=sqlite:///rebugtracker.db

# 方式2: 修改 config.py 文件
# 编辑 config.py 中的配置项
class Config:
    HOST = '0.0.0.0'
    PORT = 8080
    # ... 其他配置

# 方式3: 环境变量
export SERVER_HOST=0.0.0.0
export SERVER_PORT=8080
python rebugtracker.py
```

#### 🖥️ Windows EXE 配置
```cmd
# 方式1: 修改 app_config.ini 文件（构建后在 dist 目录）
[server]
host = 0.0.0.0
port = 8080

[database]
type = sqlite
path = rebugtracker.db

# 方式2: 修改 .env 文件（构建后在 dist 目录）
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# 方式3: VBS 脚本配置
# 编辑 start_rebugtracker.vbs 中的环境变量
Set env = shell.Environment("Process")
env("SERVER_PORT") = "8080"
env("SERVER_HOST") = "0.0.0.0"
```

#### 🍎 macOS APP 配置
```bash
# 方式1: 修改 .env 文件（构建后在 dist_mac 目录）
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
DATABASE_URL=sqlite:///rebugtracker.db

# 方式2: 修改启动脚本
# 编辑 dist_mac/start_rebugtracker.sh
export SERVER_HOST=0.0.0.0
export SERVER_PORT=8080
./ReBugTracker

# 方式3: 直接设置环境变量
cd dist_mac
SERVER_HOST=0.0.0.0 SERVER_PORT=8080 ./ReBugTracker
```

#### 🔧 高级配置选项

**数据库配置**
```bash
# SQLite（默认）
DATABASE_URL=sqlite:///rebugtracker.db

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/rebugtracker
# 或分别设置
DB_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=rebugtracker
DATABASE_USER=username
DATABASE_PASSWORD=password
```

**安全配置**
```bash
# 密钥配置
SECRET_KEY=your-secret-key-here

# HTTPS 配置（需要证书文件）
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

**日志配置**
```bash
# 日志级别
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# 日志文件路径
LOG_FILE=logs/rebugtracker.log
```

**上传配置**
```bash
# 上传文件大小限制（MB）
MAX_CONTENT_LENGTH=16

# 上传目录
UPLOAD_FOLDER=uploads
```

### 🐳 Docker 管理命令
```bash
# 查看容器状态
docker ps

# 查看应用日志
docker logs rebugtracker_app_sqlite

# 停止服务
docker-compose -f docker-compose.sqlite.yml down

# 重启服务
docker-compose -f docker-compose.sqlite.yml restart

# 查看所有容器（包括停止的）
docker ps -a

# 清理未使用的容器和镜像
docker system prune
```

### 💻 本地服务管理

#### Windows 服务管理
```cmd
# ⚠️ 注意：dist 目录只有在构建后才存在

# 1. 先进行构建（生成 dist 目录）
cd cross_platform_build\windows
python build_windows.py

# 2. 然后安装为 Windows 服务
cd dist
install_service.bat

# 3. 管理 Windows 服务
manage_service.bat

# 4. 或者使用 VBS 后台运行（主目录）
cd ..\..
wscript.exe start_rebugtracker.vbs
```

#### macOS/Linux 服务管理
```bash
# 后台运行
cd dist_mac  # 或 dist
nohup ./ReBugTracker > app.log 2>&1 &

# 查看进程
ps aux | grep ReBugTracker

# 停止服务
pkill -f ReBugTracker
```

## 📖 详细文档

### 📚 核心文档
- **[完整部署指南](DEPLOYMENT_GUIDE.md)** - 包含所有部署方式的详细说明
- **[uv 使用指南](UV_GUIDE.md)** - 现代化包管理和离线部署指南
- **[数据库工具](database_tools/README.md)** - 数据库管理和维护工具
- **[通知系统](docs/notification_priority_system_guide.md)** - 通知系统配置指南

### 🔧 构建系统文档
- **[跨平台构建总览](cross_platform_build/README.md)** - 所有平台构建方式概览
- **[Windows 构建系统](cross_platform_build/windows/README.md)** - Windows 专用构建和部署
- **[macOS 构建系统](cross_platform_build/macos/README.md)** - macOS 专用构建和部署
- **[Linux 构建系统](cross_platform_build/README.md)** - Linux 构建说明

### 📋 部署方式对比

| 部署方式 | 适用平台 | 优势 | 适用场景 |
|---------|---------|------|---------|
| **Docker 部署** | 全平台 | 环境隔离、易迁移、一致性好 | 生产环境、团队协作 |
| **本地部署** | 全平台 | 性能好、调试方便、资源占用少 | 开发环境、个人使用 |
| **Windows EXE** | Windows | 免安装、双击运行、服务化 | Windows 桌面环境 |
| **macOS APP** | macOS | 原生体验、系统集成好 | macOS 桌面环境 |
| **Linux 二进制** | Linux | 性能优化、系统集成 | Linux 服务器环境 |

### 📋 平台部署脚本对比

| 平台 | 主目录脚本 | 构建目录脚本 | 智能选择器 | 说明 |
|------|-----------|-------------|-----------|------|
| **Linux/macOS** | ✅ `deploy.sh` | ✅ `build_*.py` | ✅ `deploy.py` | 主目录有完整的一键部署 |
| **Windows** | ❌ 无 `deploy.bat` | ✅ `deploy.bat` | ✅ `deploy.py` | 需要进入构建目录或使用智能选择器 |
| **通用** | ✅ `start_rebugtracker.*` | ✅ `build_universal.py` | ✅ `deploy.py` | 提供跨平台启动脚本 |

**推荐使用顺序：**
1. **新手用户**: `python deploy.py` (智能选择器)
2. **Linux/macOS**: `./deploy.sh` (主目录一键部署)
3. **Windows**: `cd cross_platform_build\windows && deploy.bat`
4. **高级用户**: 直接使用对应平台的构建脚本

## 🏗️ 技术栈

| 组件 | 技术选型 | 版本要求 |
|------|----------|----------|
| 后端框架 | Flask | >= 2.0 |
| 数据库 | PostgreSQL / SQLite | >= 12.0 / >= 3.35 |
| 前端框架 | Bootstrap | 5.x |
| 图表库 | Chart.js | >= 3.0 |
| Python | Python | >= 3.8 |
| 包管理器 | uv / pip | 最新版 / >= 20.0 |
| 容器化 | Docker / Docker Compose | >= 20.0 |
| Web服务器 | Gunicorn / Waitress | >= 20.0 / >= 3.0 |

## 🛠️ 项目工具

### 📁 目录结构说明
```
ReBugTracker/
├── 📄 deploy.py                    # 智能部署选择器
├── 📄 deploy.sh                    # Linux/macOS 一键部署脚本
├── 📄 rebugtracker.py              # 主程序入口
├── 📄 pyproject.toml               # uv 项目配置文件
├── 📄 uv_setup.py                  # uv 环境自动设置脚本
├── 📄 create_offline_package.py    # 离线部署包创建工具
├── 📄 UV_GUIDE.md                  # uv 使用和离线部署指南
├── 📁 cross_platform_build/        # 跨平台构建系统
│   ├── 📄 build_universal.py       # 通用构建脚本
│   ├── 📁 windows/                 # Windows 构建系统
│   │   ├── 📄 build_windows.py     # Windows 主构建脚本
│   │   ├── 📄 deploy.bat           # Windows 一键部署
│   │   └── 📁 dist/                # Windows 构建输出（构建后生成）
│   ├── 📁 macos/                   # macOS 构建系统
│   │   ├── 📄 build_macos_fixed.py # macOS 主构建脚本
│   │   └── 📁 dist_mac/            # macOS 构建输出（构建后生成）
│   └── 📁 linux/                   # Linux 构建系统
├── 📁 database_tools/              # 数据库管理工具
├── 📁 test/                        # 测试套件
├── 📁 docs/                        # 文档目录
└── 📁 static/                      # 静态资源
```

### 🔧 工具功能
- **现代包管理** (`uv_setup.py`, `pyproject.toml`) - uv 超快速依赖管理
- **离线部署** (`create_offline_package.py`) - 完整离线环境打包
- **数据库工具** (`database_tools/`) - 数据库管理和维护
- **跨平台构建** (`cross_platform_build/`) - Windows/macOS/Linux 打包
- **测试套件** (`test/`) - 完整的测试覆盖
- **部署脚本** - 多种部署方式支持

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

### 📋 基础要求

#### 本地部署
- **Python**: 3.8+ (推荐 3.9+)
- **数据库**: PostgreSQL 12+ 或 SQLite 3.35+
- **内存**: 4GB+ RAM
- **存储**: 10GB+ 磁盘空间

#### Docker 部署
- **Docker**: 20.0+
- **Docker Compose**: 2.0+
- **内存**: 2GB+ RAM
- **存储**: 5GB+ 磁盘空间
- **支持平台**: Linux (amd64/arm64), macOS (Intel/Apple Silicon), Windows

#### 构建部署（生成可执行文件）
- **PyInstaller**: 最新版本
- **构建内存**: 8GB+ RAM（构建过程需要更多内存）
- **构建存储**: 15GB+ 磁盘空间

### 🌐 网络要求
- **默认端口**:
  - Docker: 10001
  - 本地: 5000
  - Windows EXE: 5000 (可配置)
  - macOS APP: 10001 (可配置)
- **镜像源**: 支持国内镜像源加速 (清华、中科大、网易)
- **防火墙**: 需要开放对应端口

### 💾 平台特殊要求

#### Windows
- **操作系统**: Windows 10/11 或 Windows Server 2016+
- **权限**: 管理员权限（用于服务安装）
- **依赖**: Visual C++ Redistributable（通常已预装）

#### macOS
- **操作系统**: macOS 10.14 (Mojave) 或更高版本
- **架构**: 支持 Intel 和 Apple Silicon (M1/M2)
- **权限**: 可能需要在"安全性与隐私"中允许运行

#### Linux
- **发行版**: Ubuntu 18.04+, CentOS 7+, Debian 10+
- **依赖**: 通常需要安装 `python3-dev`, `build-essential`
- **权限**: 普通用户权限即可（服务安装需要 sudo）

## 🛠️ 故障排除

### 🐳 Docker 相关问题

#### 1. 镜像下载失败
```bash
# 运行诊断工具（Linux/macOS）
./deploy.sh --diagnose

# 检查网络连接
ping docker.io

# 手动配置镜像源 (已自动配置)
# 清华源: https://docker.mirrors.ustc.edu.cn
# 中科大源: https://docker.mirrors.ustc.edu.cn
# 网易源: https://hub-mirror.c.163.com
```

#### 2. 端口冲突
```bash
# 检查端口占用
lsof -i :10001  # macOS/Linux
netstat -ano | findstr :10001  # Windows

# 修改端口 (编辑 docker-compose.sqlite.yml)
ports:
  - "新端口:5000"
```

#### 3. 容器启动失败
```bash
# 查看详细日志
docker logs rebugtracker_app_sqlite

# 检查容器状态
docker ps -a

# 重新构建镜像
docker-compose -f docker-compose.sqlite.yml up -d --build
```

### 🖥️ 构建部署问题

#### Windows 构建问题
```cmd
# 0. 找不到 deploy.bat - 主目录没有此文件
# 正确路径：
cd cross_platform_build\windows
deploy.bat

# 0.1 找不到 dist 目录 - 需要先构建
# dist 目录只有在构建后才存在：
python build_windows.py  # 这会创建 dist 目录

# 1. PyInstaller 未安装
pip install pyinstaller

# 2. 缺少依赖
pip install -r requirements.txt

# 3. 权限问题 - 以管理员身份运行
# 右键点击命令提示符 -> "以管理员身份运行"

# 4. 路径问题 - 确保在正确目录
cd cross_platform_build\windows
python build_windows.py
```

#### macOS 构建问题
```bash
# 1. 权限问题
chmod +x dist_mac/ReBugTracker
chmod +x dist_mac/start_rebugtracker.sh

# 2. 加密模块问题（已自动修复）
# 构建脚本包含 crypto_compat_macos.py 修复

# 3. 端口占用
# 修改 .env 文件中的 SERVER_PORT

# 4. 测试构建
cd cross_platform_build/macos
python test_macos_build.py
```

#### Linux 构建问题
```bash
# 1. 缺少系统依赖
sudo apt-get install python3-dev build-essential  # Ubuntu/Debian
sudo yum install python3-devel gcc  # CentOS/RHEL

# 2. 权限问题
chmod +x dist/ReBugTracker
chmod +x dist/start_rebugtracker.sh

# 3. 库依赖问题
ldd dist/ReBugTracker  # 检查动态库依赖
```

### 🔧 常见问题

#### 平台特定问题

**macOS 用户**
- **端口 5000 被占用**: macOS AirPlay 服务占用，已改为端口 10001
- **Docker 环境**: 支持 Docker Desktop、OrbStack、Colima
- **安全性提示**: 在"系统偏好设置 > 安全性与隐私"中允许运行

**Windows 用户**
- **杀毒软件误报**: 将构建目录添加到杀毒软件白名单
- **服务安装失败**: 确保以管理员身份运行
- **VBS 脚本被阻止**: 在组策略中允许 VBS 脚本执行

**Linux 用户**
- **端口权限**: 使用 1024 以上端口避免权限问题
- **系统服务**: 可使用 systemd 管理服务
- **防火墙**: 确保防火墙允许对应端口

#### 网络问题
- **Docker Hub 连接失败**: 自动使用国内镜像源
- **pip 安装慢**: 自动配置清华 PyPI 源
- **代理环境**: 配置 HTTP_PROXY 和 HTTPS_PROXY 环境变量

## 🎯 最佳实践

### 📊 部署方式选择指南

```mermaid
flowchart TD
    A[开始部署] --> B{使用场景?}

    B -->|个人开发/测试| C[本地部署]
    B -->|生产环境| D[Docker部署]
    B -->|桌面应用| E[构建部署]

    C --> C1[python rebugtracker.py]

    D --> D1{平台?}
    D1 -->|Linux/macOS| D2[./deploy.sh]
    D1 -->|Windows| D3[deploy.bat]

    E --> E1{目标平台?}
    E1 -->|Windows| E2[build_windows.py]
    E1 -->|macOS| E3[build_macos_fixed.py]
    E1 -->|Linux| E4[build_linux.py]
    E1 -->|多平台| E5[build_universal.py]

    C1 --> F[访问 localhost:5000]
    D2 --> G[访问 localhost:10001]
    D3 --> G
    E2 --> H[运行 ReBugTracker.exe]
    E3 --> I[运行 ReBugTracker]
    E4 --> I
    E5 --> I
```

### 🏆 推荐配置

#### 开发环境
- **部署方式**: 本地部署
- **数据库**: SQLite
- **端口**: 5000
- **优势**: 快速启动、易于调试

#### 测试环境
- **部署方式**: Docker 部署
- **数据库**: PostgreSQL
- **端口**: 10001
- **优势**: 环境隔离、接近生产

#### 生产环境
- **部署方式**: Docker 部署 + Nginx 反向代理
- **数据库**: PostgreSQL（独立部署）
- **端口**: 80/443（通过 Nginx）
- **优势**: 高可用、负载均衡、SSL 支持

#### 桌面应用
- **部署方式**: 构建部署
- **数据库**: SQLite
- **端口**: 自动分配
- **优势**: 免安装、用户友好

### 🔒 安全建议

1. **修改默认密码**: 首次登录后立即修改 admin 账户密码
2. **使用 HTTPS**: 生产环境建议配置 SSL 证书
3. **数据库安全**: PostgreSQL 使用强密码和限制访问
4. **防火墙配置**: 只开放必要的端口
5. **定期备份**: 设置自动数据库备份

### 📈 性能优化

1. **数据库选择**:
   - 小团队（<50人）: SQLite
   - 大团队（>50人）: PostgreSQL
2. **内存配置**:
   - 开发环境: 2GB
   - 生产环境: 4GB+
3. **存储优化**:
   - 定期清理日志文件
   - 压缩上传文件
   - 数据库定期维护

## 📞 技术支持

- **项目地址**: https://github.com/bjkdgh/ReBugTracker
- **问题反馈**: 提交 GitHub Issue
- **详细文档**: 查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**ReBugTracker** - 让缺陷跟踪更简单、更高效！ 🚀


