# 部署指南

## 1. 开发环境运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python rebugtracker.py
```

## 2. 生产环境部署

### 使用Gunicorn运行

```bash
gunicorn --bind 0.0.0.0:5000 --name ReBugTracker rebugtracker:app
```

参数说明：
- `--name`：设置进程名称，系统中会显示为ReBugTracker
- 第一个`rebugtracker`：Python模块文件名(不带.py后缀)，这里是rebugtracker.py
- 第二个`app`：Flask应用实例变量名，在rebugtracker.py中通过`app = Flask(__name__)`创建
- `--bind`：指定绑定的IP和端口，0.0.0.0表示监听所有网络接口

示例启动命令分解：
1. 查找rebugtracker.py文件中的Flask应用实例
2. 在5000端口启动WSGI服务器
3. 设置进程名称为ReBugTracker
4. 接收所有网络接口的请求

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
