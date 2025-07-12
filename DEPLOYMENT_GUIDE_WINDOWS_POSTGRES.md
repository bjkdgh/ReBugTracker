# DEPLOYMENT_GUIDE_WINDOWS_POSTGRES.md: Windows部署指南（PostgreSQL）

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]
本文档旨在提供在 Windows 服务器上部署 ReBugTracker 应用的详细步骤和优化建议。本指南不使用 Docker，而是采用 Nginx 作为反向代理，Waitress 作为 WSGI 服务器，并使用 PostgreSQL 数据库。

## 1. 部署概述

*   **应用服务器**: Waitress (Python WSGI 服务器)
*   **前端 Web 服务器**: Nginx (反向代理和静态文件服务)
*   **数据库**: PostgreSQL
*   **进程管理**: NSSM (将 Python 应用注册为 Windows 服务)

## 2. 部署前准备

在开始部署之前，请确保您的 Windows 服务器满足以下条件并安装好所需软件：

*   **操作系统**: Windows Server 2012 R2 或更高版本。
*   **Python**: 安装 Python 3.8+ (推荐从 [python.org](https://www.python.org/downloads/windows/) 下载安装器，并勾选“Add Python to PATH”)。
*   **Git**: 用于克隆 ReBugTracker 仓库。
*   **PostgreSQL**: 安装 PostgreSQL 数据库服务器 (推荐从 [postgresql.org](https://www.postgresql.org/download/windows/) 下载)。
*   **Nginx**: 下载 Nginx for Windows (从 [nginx.org](https://nginx.org/en/download.html) 下载稳定版)。
*   **NSSM**: 下载 Non-Sucking Service Manager (从 [nssm.cc/download/](https://nssm.cc/download/) 下载最新版本)。

## 3. 部署步骤

### 步骤 3.1: 克隆 ReBugTracker 仓库

在您选择的部署路径下（例如 `D:\app_data\repository\`），克隆 ReBugTracker 仓库：

```bash
cd D:\app_data\repository\
git clone <您的 ReBugTracker 仓库地址> ReBugTracker
cd ReBugTracker
```

### 步骤 3.2: 准备 Python 环境

1.  **创建并激活虚拟环境**:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
2.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
    项目的 `requirements.txt` 已经包含所有必要依赖：
    - `flask==2.3.3`
    - `psycopg2-binary==2.9.10` (PostgreSQL支持)
    - `waitress==2.1.2` (生产环境WSGI服务器)
    - `gunicorn==21.2.0` (备选WSGI服务器)
    - `Werkzeug==2.3.7`

### 步骤 3.3: 配置 PostgreSQL 数据库

1.  **安装 PostgreSQL**: 如果尚未安装，请按照 PostgreSQL 官方指南进行安装。
2.  **创建数据库和用户**:
    *   使用 `psql` 或 pgAdmin 创建一个数据库（例如 `rebugtracker_db`）。
    *   创建一个数据库用户（例如 `rebugtracker_user`）并设置密码，并赋予该用户对 `rebugtracker_db` 的所有权限。
3.  **配置数据库连接**:
    项目已经支持环境变量配置，推荐使用环境变量而不是直接修改 `config.py`。

    **方法1: 使用环境变量 (推荐)**
    ```bash
    # 设置环境变量
    setx DATABASE_NAME "rebugtracker_db" /M
    setx DATABASE_USER "rebugtracker_user" /M
    setx DATABASE_PASSWORD "your_secure_password" /M
    setx DATABASE_HOST "localhost" /M
    setx DATABASE_PORT "5432" /M
    setx DB_TYPE "postgres" /M
    ```

    **方法2: 修改config.py (不推荐用于生产环境)**
    如果需要修改默认值，可以编辑 `config.py` 中的 `POSTGRES_CONFIG`：
    ```python
    # config.py 中的配置已经支持环境变量
    POSTGRES_CONFIG = {
        'dbname': os.getenv('DATABASE_NAME', 'rebugtracker_db'),
        'user': os.getenv('DATABASE_USER', 'rebugtracker_user'),
        'password': os.getenv('DATABASE_PASSWORD', 'your_secure_password'),
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', '5432'))
    }
    ```
4.  **防火墙配置**: 确保 Windows 防火墙允许您的应用服务器（如果与数据库不在同一台服务器）访问 PostgreSQL 的 5432 端口。

### 步骤 3.4: 使用现有的 Waitress 启动脚本

项目已经提供了优化的 Waitress 启动脚本，位于 `deployment_tools/run_waitress.py`。您可以直接使用此脚本，或者在项目根目录创建一个简化版本：

**选项1: 使用项目提供的脚本**
```bash
# 直接使用项目提供的生产环境脚本
python deployment_tools/run_waitress.py
```

**选项2: 创建简化的启动脚本**
在 `D:\app_data\repository\ReBugTracker\` 目录下创建 `run_waitress.py`：

```python
# D:\app_data\repository\ReBugTracker\run_waitress.py
from waitress import serve
from rebugtracker import app
import logging
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/waitress.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    logging.info("Waitress 服务器启动中...")
    # 监听所有可用网络接口的5000端口
    # 0.0.0.0 表示监听所有网络接口，允许外部访问
    # 5000 是 Waitress 监听的端口，Nginx 将会代理到此端口
    serve(
        app,
        host='0.0.0.0',
        port=5000,
        threads=4,
        cleanup_interval=30,
        channel_timeout=120
    )
    logging.info("Waitress 服务器已停止。")
```

### 步骤 3.5: 测试 Waitress 启动

在命令提示符中，导航到 ReBugTracker 目录并运行：

```bash
cd D:\app_data\repository\ReBugTracker
python run_waitress.py
```

或者使用项目提供的生产环境脚本：

```bash
python deployment_tools/run_waitress.py
```

如果一切正常，您应该看到类似以下的输出：

```
INFO:root:Waitress 服务器启动中...
INFO:waitress:Serving on http://0.0.0.0:5000
```

此时，您可以在浏览器中访问 `http://localhost:5000` 来测试应用是否正常运行。

**默认登录账号**:
- 管理员: `admin` / `admin`
- 负责人: `zjn` / `123456`
- 实施组: `gh` / `123456`
- 组内成员: `wbx` / `123456`

### 步骤 3.6: 配置 Nginx 作为反向代理

1.  **安装 Nginx**: 将下载的 Nginx 压缩包解压到您希望安装的目录，例如 `C:\nginx`。
2.  **修改 Nginx 配置**:
    项目已经提供了 Nginx 配置示例文件 `nginx_windows_config_example.conf`，您可以直接使用或参考。

    将 `nginx_windows_config_example.conf` 的内容复制到 `C:\nginx\conf\nginx.conf`，或者手动配置：

    ```nginx
# C:\nginx\conf\nginx.conf
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    server {
        listen       80; # Nginx 监听的端口，通常是 80 (HTTP) 或 443 (HTTPS)
        server_name  localhost; # 替换为您的服务器 IP 地址或域名

        # 静态文件服务：ReBugTracker 的 static 目录
        location /static/ {
            alias D:/app_data/repository/ReBugTracker/static/; # **重要：替换为您的实际路径**
            expires 30d; # 浏览器缓存静态文件 30 天
            add_header Cache-Control "public, no-transform";
        }

        # 上传文件服务：ReBugTracker 的 uploads 目录
        location /uploads/ {
            alias D:/app_data/repository/ReBugTracker/uploads/; # **重要：替换为您的实际路径**
            expires 30d; # 浏览器缓存上传文件 30 天
            add_header Cache-Control "public, no-transform";
        }

        # 将所有其他请求代理到 Waitress 应用服务器
        location / {
            proxy_pass http://127.0.0.1:5000; # Waitress 监听的地址和端口
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }

        # 错误页面配置 (可选)
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
    ```

    **快速配置方法**:
    ```bash
    # 复制项目提供的配置文件
    copy nginx_windows_config_example.conf C:\nginx\conf\nginx.conf
    # 然后编辑路径部分
    ```
3.  **启动 Nginx**:
    打开命令提示符，进入 Nginx 安装目录（例如 `C:\nginx`），然后运行：
    ```bash
    start nginx
    ```
    要停止 Nginx，运行 `nginx -s stop`。要重新加载配置，运行 `nginx -s reload`。

4.  **测试完整部署**:
    现在，您应该能够通过 `http://localhost` (端口 80) 访问您的 ReBugTracker 应用。
    Nginx 会将请求代理到运行在端口 5000 的 Waitress 服务器。

    **测试步骤**:
    - 确保 Waitress 服务器正在运行 (端口 5000)
    - 确保 Nginx 正在运行 (端口 80)
    - 访问 `http://localhost` 测试应用
    - 使用默认账号登录测试功能

## 4. 配置为 Windows 服务 (可选)

### 步骤 4.1: 将 ReBugTracker 注册为 Windows 服务 (使用 NSSM)

使用 NSSM 可以确保 ReBugTracker 应用在服务器启动时自动运行，并在崩溃时自动重启。

1.  **解压 NSSM**: 将下载的 NSSM 压缩包解压到一个方便的目录，例如 `C:\nssm`。
2.  **打开管理员权限的命令提示符或 PowerShell**。
3.  **进入 NSSM 目录**:
    ```bash
    cd C:\nssm\win64 # 根据您的系统选择 win64 或 win32
    ```
4.  **安装服务**:
    运行以下命令，这将弹出一个 NSSM GUI 配置界面：
    ```bash
    nssm install ReBugTrackerService
    ```
    在弹出的 NSSM GUI 界面中，按照以下说明填写字段：
    *   **Application Tab (应用程序选项卡)**:
        *   **Path (路径)**: 填写您的虚拟环境中 Python 解释器的完整路径。
            例如: `D:\app_data\repository\ReBugTracker\.venv\Scripts\python.exe`
        *   **Startup directory (启动目录)**: 填写您的 ReBugTracker 项目的根目录。
            例如: `D:\app_data\repository\ReBugTracker`
        *   **Arguments (参数)**: 填写您的 Waitress 启动脚本的文件名。
            例如: `run_waitress.py`
    *   **Details Tab (详细信息选项卡)**:
        *   **Display name (显示名称)**: `ReBugTracker Web Service` (服务在 Windows 服务管理器中显示的名称)
        *   **Description (描述)**: `ReBugTracker Flask Application powered by Waitress`
    *   **Log On Tab (登录选项卡)**:
        *   建议选择 `Local System account` (本地系统账户)，或一个具有足够权限的用户账户。
    *   **I/O Tab (输入/输出选项卡)**: (可选，但强烈推荐配置日志输出)
        *   **Output (stdout)**: `D:\app_data\repository\ReBugTracker\logs\waitress_stdout.log` (确保 `logs` 目录存在)
        *   **Error (stderr)**: `D:\app_data\repository\ReBugTracker\logs\waitress_stderr.log` (确保 `logs` 目录存在)
    *   **Exit Actions Tab (退出操作选项卡)**:
        *   **Restart Application (重启应用程序)**: 确保选中此项，以便在应用崩溃时自动重启。
    *   **点击 "Install service" (安装服务)**。

5.  **启动服务**:
    安装完成后，您可以在 Windows 服务管理器中找到 `ReBugTracker Web Service` 并手动启动它，或者通过命令行：
    ```bash
    nssm start ReBugTrackerService
    ```
    要停止服务，运行 `nssm stop ReBugTrackerService`。

## 4. 最终检查与测试

1.  **确认所有服务运行正常**:
    *   **PostgreSQL**: 确保 PostgreSQL 数据库服务正在运行。
    *   **ReBugTracker Service**: 检查 Windows 服务管理器，确认 `ReBugTracker Web Service` 状态为“正在运行”。
    *   **Nginx**: 确认 Nginx 进程正在运行。
2.  **检查日志**:
    *   查看 `D:\app_data\repository\ReBugTracker\logs\` 目录下的 `waitress_stdout.log` 和 `waitress_stderr.log` 文件，确保没有错误信息。
    *   查看 Nginx 的日志文件（通常在 `C:\nginx\logs\` 目录下），检查 `access.log` 和 `error.log`。
3.  **访问应用**:
    在浏览器中输入您的服务器 IP 地址或配置的域名（例如 `http://localhost` 或 `http://your_server_ip`），应该能看到 ReBugTracker 的登录页面。

## 5. 优化建议实施状态

### ✅ 已实施的优化

*   **环境变量配置**: ✅ **已完成**
    *   项目的 `config.py` 已经完全支持环境变量配置
    *   所有敏感信息都可以通过环境变量设置
    *   支持开发和生产环境的不同配置

*   **Waitress优化**: ✅ **已完成**
    *   提供了优化的 Waitress 启动脚本 (`deployment_tools/run_waitress.py`)
    *   配置了合理的线程数、超时时间等参数
    *   支持日志记录和错误处理

*   **Nginx配置**: ✅ **已完成**
    *   提供了完整的 Nginx 配置示例 (`nginx_windows_config_example.conf`)
    *   包含静态文件缓存、代理配置等优化

### 🔧 推荐的额外优化

*   **安全性**:
    *   **HTTPS**: 强烈建议为 Nginx 配置 SSL/TLS 证书，启用 HTTPS
    *   **防火墙**: 配置 Windows 防火墙，只允许必要端口对外开放
    *   **环境变量设置** (已支持，需要手动配置):
        ```bash
        # 生产环境环境变量设置
        setx DB_TYPE "postgres" /M
        setx DATABASE_NAME "rebugtracker_production" /M
        setx DATABASE_USER "rebugtracker_user" /M
        setx DATABASE_PASSWORD "your_secure_password" /M
        setx DATABASE_HOST "localhost" /M
        setx DATABASE_PORT "5432" /M
        ```

*   **监控和日志**:
    *   **日志管理**: 项目已支持日志记录，建议配置日志轮转
    *   **性能监控**: 使用 Windows 性能监视器监控系统资源
    *   **应用监控**: 监控 Waitress 进程和 Nginx 状态

*   **备份策略**:
    *   **数据库备份**: 定期备份 PostgreSQL 数据库
        ```bash
        # PostgreSQL 备份命令示例
        pg_dump -U rebugtracker_user -h localhost rebugtracker_db > backup_$(date +%Y%m%d).sql
        ```
    *   **应用备份**: 备份上传文件目录和配置文件

*   **性能优化**:
    *   **数据库连接池**: 考虑使用连接池优化数据库连接
    *   **缓存策略**: 对于高访问量场景，考虑添加 Redis 缓存
    *   **静态文件CDN**: 对于大规模部署，考虑使用 CDN 加速静态文件

### 📋 部署检查清单

- [ ] 设置生产环境的环境变量
- [ ] 配置 HTTPS 证书 (推荐)
- [ ] 设置防火墙规则
- [ ] 配置日志轮转
- [ ] 设置数据库备份计划
- [ ] 配置监控告警
- [ ] 测试故障恢复流程

## 6. 总结

本指南涵盖了在 Windows 环境下使用 PostgreSQL 部署 ReBugTracker 的完整流程：

### ✅ 已完成的部署内容
1. **PostgreSQL 数据库配置**
2. **Python 环境和依赖安装**
3. **Waitress WSGI 服务器配置**
4. **Nginx 反向代理配置**
5. **Windows 服务注册 (可选)**
6. **生产环境优化建议**

### 🔗 相关资源
- **Docker 部署**: 参考 `docker-compose.yml` 和 `DEPLOYMENT.md`
- **SQLite 模式**: 修改 `config.py` 中的 `DB_TYPE = 'sqlite'`
- **开发环境**: 直接运行 `python rebugtracker.py`
- **测试工具**: 使用 `database_tools/` 目录下的测试脚本

### 📞 技术支持
如果在部署过程中遇到问题，请：
1. 检查日志文件 (`logs/` 目录)
2. 验证数据库连接 (`python database_tools/test_db_connection.py`)
3. 测试应用功能 (`python database_tools/test_user_management.py`)

---

**ReBugTracker Windows + PostgreSQL 部署指南** - 版本 1.0

希望这份详细的部署文档能帮助您成功部署 ReBugTracker 应用!
