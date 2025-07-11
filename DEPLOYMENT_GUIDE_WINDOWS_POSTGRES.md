# ReBugTracker Windows 服务器部署指南 (无 Docker, PostgreSQL)

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
    请确保 `requirements.txt` 中包含 `waitress` 和 `psycopg2-binary`。如果缺少，请手动安装：
    ```bash
pip install waitress psycopg2-binary
    ```

### 步骤 3.3: 配置 PostgreSQL 数据库

1.  **安装 PostgreSQL**: 如果尚未安装，请按照 PostgreSQL 官方指南进行安装。
2.  **创建数据库和用户**:
    *   使用 `psql` 或 pgAdmin 创建一个数据库（例如 `rebugtracker_db`）。
    *   创建一个数据库用户（例如 `rebugtracker_user`）并设置密码，并赋予该用户对 `rebugtracker_db` 的所有权限。
3.  **配置 `config.py`**:
    打开 `D:\app_data\repository\ReBugTracker\config.py` 文件，确保 `DB_CONFIG` 字典中的数据库连接信息与您的 PostgreSQL 配置一致。

    ```python
# D:\app_data\repository\ReBugTracker\config.py
DB_CONFIG = {
        'dbname': 'rebugtracker_db', # 您的数据库名称
        'user': 'rebugtracker_user', # 您的数据库用户名
        'password': 'your_db_password', # 您的数据库密码
        'host': 'localhost', # 如果数据库在同一服务器，使用 localhost 或 127.0.0.1
        'port': 5432 # PostgreSQL 默认端口
    }
    ```
    **重要**: 将 `your_db_password` 替换为您的实际数据库密码。
4.  **防火墙配置**: 确保 Windows 防火墙允许您的应用服务器（如果与数据库不在同一台服务器）访问 PostgreSQL 的 5432 端口。

### 步骤 3.4: 创建 Waitress 启动脚本

在 `D:\app_data\repository\ReBugTracker\` 目录下创建一个名为 `run_waitress.py` 的文件，并添加以下内容：

```python
# D:\app_data\repository\ReBugTracker\run_waitress.py
from waitress import serve
from rebugtracker import app, init_db
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    logging.info("正在初始化数据库...")
    try:
        init_db()
        logging.info("数据库初始化完成。")
    except Exception as e:
        logging.error(f"数据库初始化失败: {e}")
        # 如果数据库初始化失败，通常需要退出，以便管理员检查问题
        sys.exit(1)

    logging.info("Waitress 服务器启动中...")
    # 监听所有可用网络接口的5000端口
    # 0.0.0.0 表示监听所有网络接口，允许外部访问
    # 5000 是 Waitress 监听的端口，Nginx 将会代理到此端口
    serve(app, host='0.0.0.0', port=5000)
    logging.info("Waitress 服务器已停止。")
```

### 步骤 3.5: 配置 Nginx 作为反向代理

1.  **安装 Nginx**: 将下载的 Nginx 压缩包解压到您希望安装的目录，例如 `C:\nginx`。
2.  **修改 Nginx 配置**:
    打开 `C:\nginx\conf\nginx.conf` 文件，并将其内容替换为以下示例。请根据您的实际路径进行修改。

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
            server_name  localhost; # 替换为您的服务器 IP 地址或域名，例如 example.com

            # 静态文件服务：ReBugTracker 的 static 目录
            location /static/ {
                alias D:/app_data/repository/ReBugTracker/static/; # **重要：替换为您的实际 static 目录路径**
                expires 30d; # 浏览器缓存静态文件 30 天
                add_header Cache-Control "public, no-transform";
            }

            # 上传文件服务：ReBugTracker 的 uploads 目录
            location /uploads/ {
                alias D:/app_data/repository/ReBugTracker/uploads/; # **重要：替换为您的实际 uploads 目录路径**
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
                proxy_redirect off; # 不重写响应头中的 Location 字段
            }

            # 错误页面配置 (可选)
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   html; # Nginx 默认的错误页面目录
            }
        }
    }
    ```
    **重要**: 务必将 `alias` 指令中的路径替换为您的 ReBugTracker 项目的实际 `static` 和 `uploads` 目录的绝对路径。
3.  **启动 Nginx**:
    打开命令提示符，进入 Nginx 安装目录（例如 `C:\nginx`），然后运行：
    ```bash
    start nginx
    ```
    要停止 Nginx，运行 `nginx -s stop`。要重新加载配置，运行 `nginx -s reload`。

### 步骤 3.6: 将 ReBugTracker 注册为 Windows 服务 (使用 NSSM)

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

## 5. 优化建议 (回顾)

*   **安全性**:
    *   **HTTPS**: 强烈建议为 Nginx 配置 SSL/TLS 证书，启用 HTTPS，以加密所有传输数据。
    *   **防火墙**: 配置 Windows 防火墙，只允许必要的端口（如 80/443 用于 Web 访问）对外开放。数据库端口（5432）应只允许应用服务器访问。
    *   **环境变量**: 将数据库密码等敏感信息存储在 Windows 环境变量中，而不是硬编码在 `config.py` 中。生产环境建议使用以下方式：
    *   在 NSSM 服务配置界面的 "Environment" 标签页设置环境变量
    *   或通过命令行使用 `setx` 命令设置：
        ```bash
        setx DATABASE_NAME "production_db" /M
        setx DATABASE_USER "db_admin" /M
        setx DATABASE_PASSWORD "secure_password" /M
        setx DATABASE_HOST "localhost" /M
        ```
    *   修改 `config.py` 使用环境变量（保留默认值用于开发环境）：
        ```python
        import os
        DB_CONFIG = {
            'dbname': os.getenv('DATABASE_NAME', 'postgres'),
            'user': os.getenv('DATABASE_USER', 'postgres'),
            'password': os.getenv('DATABASE_PASSWORD', '$RFV5tgb'),
            'host': os.getenv('DATABASE_HOST', '192.168.1.5'),
            'port': int(os.getenv('DATABASE_PORT', '5432'))
        }
        ```
    *   生产环境最佳实践：移除默认值，强制要求设置环境变量
*   **监控**:
    *   使用 Windows 自带的性能监视器或第三方工具监控服务器的 CPU、内存、磁盘 I/O 和网络使用情况。
*   **备份**:
    *   定期备份 PostgreSQL 数据库。

---

希望这份详细的部署文档能帮助您成功部署 ReBugTracker 应用!
