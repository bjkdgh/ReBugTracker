# 部署工具集

这个文件夹包含了ReBugTracker应用的部署和运维工具。

## 🛠️ 工具列表

### 1. 生产环境部署

#### `run_waitress.py`
**生产环境WSGI服务器** - 使用Waitress运行应用
- 高性能WSGI服务器
- 适合生产环境使用
- 支持多线程处理
- 自动错误处理和重启

**使用方法**：
```bash
python deployment_tools/run_waitress.py
```

### 2. Windows服务管理

#### `install_windows_service.bat`
**Windows服务安装工具** - 将ReBugTracker安装为Windows服务
- 使用NSSM (Non-Sucking Service Manager)
- 自动配置服务参数
- 支持开机自启动
- 完整的日志记录

#### `uninstall_windows_service.bat`
**Windows服务卸载工具** - 卸载ReBugTracker Windows服务

#### `manage_windows_service.bat`
**Windows服务管理工具** - 图形化服务管理界面

#### `start_service.bat`
**快速启动服务脚本** - 快速启动ReBugTracker Windows服务

### 3. 必需工具下载指南

#### Python 环境 (如果系统未安装)
**官网下载地址**: https://www.python.org/downloads/
- 推荐版本：Python 3.8+ 或 Python 3.12.x

**使用Windows默认工具下载**:
```cmd
# 方法1: 使用PowerShell下载Python安装包
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe' -OutFile 'python-installer.exe'"

# 方法2: 使用curl下载 (Windows 10 1803+自带)
curl -o python-installer.exe https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe

# 方法3: 使用bitsadmin下载 (所有Windows版本)
bitsadmin /transfer "PythonDownload" https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe "%cd%\python-installer.exe"
```

**安装说明**:
- 运行下载的 `python-installer.exe`
- 勾选 "Add Python to PATH" 选项
- 选择 "Install Now" 进行标准安装

#### NSSM (Non-Sucking Service Manager)
**官网下载地址**: https://nssm.cc/download

**使用Windows默认工具下载**:
```cmd
# 方法1: 使用PowerShell下载
powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm-2.24.zip'"

# 方法2: 使用curl下载 (Windows 10 1803+自带)
curl -o nssm-2.24.zip https://nssm.cc/release/nssm-2.24.zip

# 方法3: 使用bitsadmin下载 (所有Windows版本)
bitsadmin /transfer "NSSMDownload" https://nssm.cc/release/nssm-2.24.zip "%cd%\nssm-2.24.zip"
```

**安装说明**:
- 解压下载的 `nssm-2.24.zip`
- 将 `win64\nssm.exe` 复制到 `deployment_tools\` 目录
- 用于将应用程序安装为Windows服务

#### PostgreSQL 数据库
**官网下载地址**: https://www.postgresql.org/download/windows/

**使用Windows默认工具下载**:
```cmd
# 方法1: 使用PowerShell下载PostgreSQL 17.5
powershell -Command "Invoke-WebRequest -Uri 'https://get.enterprisedb.com/postgresql/postgresql-17.5-1-windows-x64.exe' -OutFile 'postgresql-installer.exe'"

# 方法2: 使用curl下载 (Windows 10 1803+自带)
curl -o postgresql-installer.exe https://get.enterprisedb.com/postgresql/postgresql-17.5-1-windows-x64.exe

# 方法3: 使用bitsadmin下载 (所有Windows版本)
bitsadmin /transfer "PostgreSQLDownload" https://get.enterprisedb.com/postgresql/postgresql-17.5-1-windows-x64.exe "%cd%\postgresql-installer.exe"
```

**安装说明**:
- 运行下载的 `postgresql-installer.exe`
- 推荐版本：PostgreSQL 17.5
- 安装时记住设置的密码
- 默认端口：5432

## 📁 目录结构

```
deployment_tools/
├── README.md                          # 本文档
├── run_waitress.py                    # Waitress WSGI服务器
├── install_windows_service.bat        # Windows服务安装
├── uninstall_windows_service.bat      # Windows服务卸载
├── manage_windows_service.bat         # Windows服务管理
├── start_service.bat                  # 快速启动服务
├── windows_service_config.md          # Windows服务配置说明
└── nssm.exe                          # NSSM工具 (需要手动下载)
```

## 🚀 部署方案

### 1. 开发环境
```bash
# 使用Flask开发服务器（仅开发用）
python rebugtracker.py
```

### 2. 生产环境
```bash
# 使用Waitress生产服务器
python deployment_tools/run_waitress.py
```

### 3. Windows服务部署（推荐生产环境）
```cmd
# 1. 下载并放置 NSSM 工具
# 2. 安装为Windows服务
deployment_tools\install_windows_service.bat

# 3. 管理Windows服务
deployment_tools\manage_windows_service.bat
```

### 4. Docker部署
```bash
# 使用Docker容器部署
docker-compose up -d
```

## 📋 部署前准备

### 必需软件
- [ ] Python 3.8+ 
- [ ] pip 包管理器
- [ ] Git (可选，用于代码更新)

### Windows服务部署额外要求
- [ ] NSSM 工具 (从官网下载)
- [ ] PostgreSQL 数据库 (如选择PostgreSQL)
- [ ] 管理员权限

### Docker部署额外要求
- [ ] Docker Desktop
- [ ] Docker Compose

## 🔧 配置参数

### Waitress服务器配置
在 `run_waitress.py` 中修改：
```python
HOST = '0.0.0.0'      # 监听地址
PORT = 8000           # 监听端口
THREADS = 4           # 线程数
```

### 环境变量配置
在项目根目录的 `.env` 文件中配置：
```env
DATABASE_TYPE=sqlite          # 数据库类型
APP_PORT=8000                # 应用端口
DATABASE_HOST=localhost       # 数据库主机
DATABASE_PORT=5432           # 数据库端口
DATABASE_NAME=rebugtracker   # 数据库名称
DATABASE_USER=postgres       # 数据库用户
DATABASE_PASSWORD=your_pass  # 数据库密码
```

## 📊 监控和维护

### 日志管理
- **应用日志**: `logs/` 目录
- **服务日志**: Windows事件查看器
- **访问日志**: Waitress自动记录

### Windows服务管理
```cmd
# 查看服务状态
sc query ReBugTracker

# 启动服务
net start ReBugTracker

# 停止服务
net stop ReBugTracker

# 重启服务
net stop ReBugTracker && net start ReBugTracker
```

## ⚠️ 注意事项

1. **NSSM工具**: 必须从官网下载并手动放置到 `deployment_tools\` 目录
2. **PostgreSQL**: 如选择PostgreSQL，需要先安装并配置数据库
3. **端口冲突**: 确保8000端口未被占用
4. **防火墙**: 开放相应端口的访问权限
5. **管理员权限**: Windows服务安装需要管理员权限

## 🔄 更新部署

### 应用更新流程
1. 备份当前版本和数据
2. 停止服务
3. 更新代码
4. 更新依赖包
5. 重启服务
6. 验证功能

### Windows服务更新
```cmd
# 停止服务
net stop ReBugTracker

# 更新代码和依赖
git pull
.venv\Scripts\pip install -r requirements.txt

# 重启服务
net start ReBugTracker
```

## 🆘 故障排除

### 常见问题
1. **服务启动失败**: 检查 `logs\service_stderr.log`
2. **数据库连接失败**: 检查数据库服务状态和连接参数
3. **端口被占用**: 修改 `.env` 文件中的 `APP_PORT`
4. **权限不足**: 以管理员身份运行相关脚本

### 获取帮助
- 查看项目文档
- 检查日志文件
- 参考 `windows_service_config.md` 详细配置说明

