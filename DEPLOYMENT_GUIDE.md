# ReBugTracker 完整部署指南

## 🚀 快速开始

### 一键部署（推荐）

#### Windows 用户
```cmd
# 以管理员身份运行
deploy.bat
```

#### Linux/macOS 用户-----没具体测试
```bash
chmod +x deploy.sh
./deploy.sh
```

#### 智能选择器
```bash
python deploy.py
```

## 📋 部署方式对比

| 部署方式 | 适用场景 | 优势 | 要求 |
|----------|----------|------|------|
| **Docker部署** | 生产环境、团队协作 | 环境隔离、一键启动 | Docker Desktop |
| **本地开发** | 开发调试 | 直接运行、便于调试 | Python 3.8+ |
| **Windows服务** | Windows生产环境 | 开机自启、后台运行 | NSSM工具 |
| **VBS后台启动** | Windows轻量部署 | 无窗口运行、原生支持 | Windows系统 |

## 🐳 Docker 部署

### PostgreSQL 模式（推荐生产环境）
```bash
# 1. 克隆项目
git clone https://github.com/bjkdgh/ReBugTracker.git
cd ReBugTracker

# 2. 启动服务
docker-compose up -d

# 3. 查看状态
docker-compose ps
```

### SQLite 模式（轻量部署）
```bash
# 使用 SQLite 配置
docker-compose -f docker-compose.sqlite.yml up -d
```

### Docker 管理命令
```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新镜像
docker-compose pull && docker-compose up -d
```

## 💻 本地开发部署

### 环境准备
```bash
# 1. 检查 Python 版本
python --version  # 需要 3.8+

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows
.venv\Scripts\activate.ps1
# Linux/macOS
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 数据库配置

#### SQLite（零配置）
```bash
# 直接启动，自动创建数据库
python rebugtracker.py
```

#### PostgreSQL（生产推荐）
```bash
# 1. 安装 PostgreSQL
# Windows: https://www.postgresql.org/download/windows/
# Ubuntu: sudo apt install postgresql postgresql-contrib
# macOS: brew install postgresql

# 2. 创建数据库
createdb rebugtracker

# 3. 配置环境变量
export DB_TYPE=postgres
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_NAME=rebugtracker
export DATABASE_USER=postgres
export DATABASE_PASSWORD=your_password

# 4. 启动应用(应用具有初始化数据库的功能)
python rebugtracker.py
```

## 🪟 Windows 专用部署

### Windows 服务部署

#### 准备工作
1. **下载 NSSM**: https://nssm.cc/download
2. **解压并放置**: 将 `nssm.exe` 放到 `deployment_tools/` 目录

#### 自动安装（推荐）
```cmd
# 进入 dist 目录
cd dist

# 运行安装脚本
install_service.bat

# 管理服务
manage_service.bat
```

#### 手动安装
```cmd
# 1. 安装服务
nssm install ReBugTracker "C:\path\to\ReBugTracker.exe"

# 2. 配置服务
nssm set ReBugTracker AppDirectory "C:\path\to\project"
nssm set ReBugTracker DisplayName "ReBugTracker 缺陷跟踪系统"

# 3. 启动服务
nssm start ReBugTracker
```

### VBS 后台启动

#### 使用现有 VBS 脚本
```vbs
' 编辑 start_rebugtracker.vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\path\to\your\project"
WshShell.Run "python deployment_tools\run_waitress.py", 0, False
MsgBox "ReBugTracker已启动，访问地址: http://localhost:5000"
```

#### 开机自动启动
1. 将 VBS 脚本复制到启动文件夹：
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
   ```

## 🍎 macOS 部署

### 使用打包版本
```bash
# 1. 进入跨平台构建目录
cd cross_platform_build

# 2. 运行 macOS 打包
python build_macos.py

# 3. 启动应用
cd dist/ReBugTracker
./start_rebugtracker.sh
```

### 源码运行
```bash
# 1. 安装依赖
brew install python3 postgresql  # 可选

# 2. 设置虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 启动应用
python rebugtracker.py
```

## 🐧 Linux 部署

### 使用打包版本
```bash
# 1. 构建可执行文件
cd cross_platform_build
python build_linux.py

# 2. 安装到系统（可选）
cd dist/ReBugTracker
sudo ./install.sh

# 3. 启动服务
systemctl start rebugtracker
```

### 源码部署
```bash
# 1. 安装系统依赖
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql-server

# 2. 设置应用
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 配置数据库（PostgreSQL）
sudo -u postgres createdb rebugtracker

# 4. 启动应用
python rebugtracker.py
```

### 系统服务配置
```bash
# 创建服务文件
sudo tee /etc/systemd/system/rebugtracker.service > /dev/null <<EOF
[Unit]
Description=ReBugTracker Bug Tracking System
After=network.target

[Service]
Type=simple
User=rebugtracker
WorkingDirectory=/opt/rebugtracker
ExecStart=/opt/rebugtracker/.venv/bin/python rebugtracker.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable rebugtracker
sudo systemctl start rebugtracker
```

## ⚙️ 配置管理

### 环境变量配置
所有部署方式都支持通过 `.env` 文件进行配置：

```bash
# 数据库配置
DB_TYPE=postgres                    # postgres 或 sqlite
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=rebugtracker
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# 服务器配置
SERVER_HOST=0.0.0.0                # 监听地址
SERVER_PORT=5000                   # 监听端口
SECRET_KEY=your-secret-key         # Flask 密钥

# 文件配置
UPLOAD_FOLDER=uploads              # 上传目录
LOG_FOLDER=logs                    # 日志目录
DATA_EXPORT_FOLDER=data_exports    # 导出目录

# 邮件通知配置（可选）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true

# Gotify 推送配置（可选）
GOTIFY_SERVER_URL=https://your-gotify-server.com
GOTIFY_APP_TOKEN=your_gotify_token
```

### 常用配置修改

#### 修改端口
```bash
# 编辑 .env 文件
SERVER_PORT=8080
```

#### 切换数据库
```bash
# SQLite 转 PostgreSQL
DB_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_NAME=rebugtracker
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# PostgreSQL 转 SQLite
DB_TYPE=sqlite
SQLITE_DB_PATH=rebugtracker.db
```

## 🔧 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/macOS

# 解决方案：修改端口
echo "SERVER_PORT=8080" >> .env
```

#### 2. 数据库连接失败
```bash
# 检查 PostgreSQL 服务
systemctl status postgresql    # Linux
brew services list postgresql  # macOS
net start postgresql-x64-15    # Windows

# 检查连接参数
cat .env | grep DATABASE_
```

#### 3. 权限问题
```bash
# Linux/macOS 设置执行权限
chmod +x ReBugTracker
chmod +x start_rebugtracker.sh

# Windows 以管理员身份运行
```

#### 4. Python 依赖问题
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt

# 清理缓存
pip cache purge
```

### 日志查看

#### 应用日志
```bash
# 查看应用日志
tail -f logs/rebugtracker.log

# Windows
type logs\rebugtracker.log
```

#### 系统服务日志
```bash
# Docker
docker-compose logs -f

# Linux systemd
journalctl -u rebugtracker -f

# Windows 服务
# 查看 Windows 事件查看器
```

## 🌐 访问应用

### 默认访问信息
- **访问地址**: http://localhost:5000
- **管理员账号**: admin
- **管理员密码**: admin

### 测试账号
| 角色 | 用户名 | 密码 | 权限说明 |
|------|--------|------|----------|
| 管理员 | admin | admin | 系统管理、用户管理 |
| 负责人 | zjn | 123456 | 问题分配、状态管理 |---初始化未实际建立
| 实施组 | gh | 123456 | 问题提交、文件上传 |---初始化未实际建立
| 组内成员 | wbx | 123456 | 问题处理、状态更新 |---初始化未实际建立

## 📞 技术支持

### 获取帮助
1. **查看日志**: 检查 `logs/` 目录中的日志文件
2. **检查配置**: 确认 `.env` 文件配置正确
3. **重启服务**: 尝试重启应用服务
4. **查看文档**: 参考项目文档和工具说明

### 联系方式
- **项目地址**: https://github.com/bjkdgh/ReBugTracker
- **问题反馈**: 提交 GitHub Issue
- **技术交流**: 查看项目 Wiki

---

**祝您使用愉快！** 🎉
