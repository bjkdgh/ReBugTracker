# ReBugTracker 部署指南

## 🚀 快速部署

### 方式一：Docker Compose (推荐)

#### 1. 使用启动脚本 (最简单)

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

#### 2. 手动部署

**PostgreSQL模式:**
```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 设置 DB_TYPE=postgres

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

**SQLite模式:**
```bash
# 启动SQLite模式
docker-compose -f docker-compose.sqlite.yml up -d
```

### 方式二：本地开发环境

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置数据库 (编辑 config.py)
# 设置 DB_TYPE = 'sqlite' 或 'postgres'

# 3. 启动开发服务器
python rebugtracker.py
```

## 🔧 生产环境部署

### 1. Docker 生产部署 (推荐)

#### 环境准备
```bash
# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 部署步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd ReBugTracker

# 2. 配置环境变量
cp .env.example .env
vim .env  # 编辑配置

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f app
```

### 2. 传统部署方式

#### 使用 Gunicorn + Nginx

**安装依赖:**
```bash
pip install -r requirements.txt
pip install gunicorn
```

**启动 Gunicorn:**
```bash
gunicorn --bind 127.0.0.1:5000 \
         --workers 4 \
         --timeout 120 \
         --name ReBugTracker \
         rebugtracker:app
```

**Nginx 配置:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/ReBugTracker/static;
        expires 30d;
    }

    location /uploads {
        alias /path/to/ReBugTracker/uploads;
        expires 7d;
    }
}
```

进程查看方法：
```bash
ps aux | grep ReBugTracker
# 或
pgrep -f ReBugTracker
# 或查看master进程
pstree -ap | grep ReBugTracker
```

### 使用Docker部署
```bash
# 构建镜像
docker build -t rebugtracker .

# 运行容器(简单模式)
docker run -d -p 5000:5000 --name rbt rebugtracker

# 运行容器(生产模式，带环境变量)
docker run -d -p 5000:5000 --name rbt \
  -e DATABASE_URL=postgresql://user:pass@db:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  rebugtracker
```

### 使用Docker Compose部署
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: example
      POSTGRES_USER: user
      POSTGRES_DB: dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

### Nginx配置

1. 安装Nginx:
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

2. 配置说明(详见nginx.conf):
- 修改`server_name`为你的域名或IP
- 修改`proxy_pass`地址确保与应用运行地址一致
- 修改`/static/`的`alias`路径指向实际静态文件目录

3. 启用配置:
```bash
# 测试配置是否正确
sudo nginx -t

# 重启Nginx生效
sudo systemctl restart nginx
```

4. 常见问题排查:
- 检查端口冲突: `netstat -tulnp | grep 80`
- 查看错误日志: `tail -f /var/log/nginx/error.log`
- 确保SELinux/firewall允许HTTP流量

## 3. 数据库要求
- PostgreSQL数据库
- 需要提前创建数据库和用户
- 配置见config.py文件

## 4. 生产环境架构说明

### 进程模型
1. Gunicorn主进程 (Master)
   - 负责管理工作进程
   - 监听信号并管理生命周期
2. 工作进程 (Workers)
   - 默认数量: CPU核心数×2+1
   - 处理实际请求
3. 查看方法:
```bash
pstree -ap | grep ReBugTracker
# 或
gunicorn --bind 0.0.0.0:5000 --name ReBugTracker --workers 4 rebugtracker:app
```

### 相关服务
1. Web服务器: Nginx
   - 处理静态文件
   - 反向代理到Gunicorn
   - SSL终止
2. 数据库: PostgreSQL (独立服务)
3. 缓存: Redis (可选)
4. 进程管理: systemd/supervisor

### 监控建议
1. 日志收集:
   - Gunicorn访问日志
   - 应用错误日志
2. 性能监控:
   - Prometheus + Grafana
   - Sentry错误跟踪

## 5. 多平台支持
- Linux: 生产环境首选
- Windows: 适合开发测试
- macOS: 适合开发测试
