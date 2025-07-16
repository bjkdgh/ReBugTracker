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

**特点**：
- 🚀 **高性能**：比Flask开发服务器性能更好
- 🔒 **安全**：适合生产环境的安全配置
- 🔧 **可配置**：支持自定义端口、线程数等参数
- 📊 **监控**：提供基本的性能监控

### 2. Windows服务管理 (NSSM)

#### `install_windows_service.bat`
**Windows服务安装工具** - 将ReBugTracker安装为Windows服务
- 使用NSSM (Non-Sucking Service Manager)
- 自动配置服务参数
- 支持开机自启动
- 完整的日志记录

#### `uninstall_windows_service.bat`
**Windows服务卸载工具** - 卸载ReBugTracker Windows服务
- 安全停止和卸载服务
- 保留日志和配置文件
- 完整性验证

#### `manage_windows_service.bat`
**Windows服务管理工具** - 图形化服务管理界面
- 启动/停止/重启服务
- 查看服务状态和日志
- 配置服务参数
- 快速访问Web界面

### 3. 数据库工具

#### `postgresql-17.5-3-windows-x64.exe`
**PostgreSQL数据库安装包** - Windows版PostgreSQL 17.5
- 完整的PostgreSQL数据库系统
- 适用于Windows x64系统
- 包含管理工具和驱动程序

#### `nssm-2.24.zip`
**NSSM工具包** - Windows服务管理器
- 将任何程序转换为Windows服务
- 支持服务依赖和恢复
- 完整的日志管理
- 图形化配置界面

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

### 3. Windows服务部署
```cmd
# 安装为Windows服务（推荐生产环境）
deployment_tools\install_windows_service.bat

# 管理Windows服务
deployment_tools\manage_windows_service.bat

# 卸载Windows服务
deployment_tools\uninstall_windows_service.bat
```

### 4. Docker部署
```bash
# 使用Docker容器部署
docker-compose up -d
```

### 5. Nginx反向代理
```bash
# 配置Nginx反向代理
# 参考项目根目录的nginx配置文件
```

## 📋 部署检查清单

### 部署前准备
- [ ] 检查Python环境（Python 3.8+）
- [ ] 安装依赖包：`pip install -r requirements.txt`
- [ ] 配置数据库连接
- [ ] 检查端口可用性
- [ ] 准备SSL证书（如需要）

### 数据库准备
- [ ] 创建数据库表结构
- [ ] 导入初始数据
- [ ] 配置数据库连接参数
- [ ] 测试数据库连接

### 安全配置
- [ ] 修改默认密钥（SECRET_KEY）
- [ ] 配置防火墙规则
- [ ] 设置访问权限
- [ ] 启用HTTPS（生产环境）

### 性能优化
- [ ] 配置适当的线程数
- [ ] 设置连接超时时间
- [ ] 配置静态文件服务
- [ ] 启用缓存（如需要）

## 🔧 配置参数

### Waitress服务器配置
```python
# 在run_waitress.py中修改
HOST = '0.0.0.0'      # 监听地址
PORT = 8000           # 监听端口
THREADS = 4           # 线程数
```

### 应用配置
```python
# 在rebugtracker.py中修改
DEBUG = False         # 生产环境关闭调试
SECRET_KEY = 'your-secret-key'  # 修改密钥
```

## 📊 监控和维护

### 日志管理
- 应用日志：`logs/` 目录
- 访问日志：Waitress自动记录
- 错误日志：Python异常日志

### 性能监控
- 内存使用情况
- CPU使用率
- 数据库连接数
- 响应时间

### 备份策略
- 数据库定期备份
- 应用文件备份
- 配置文件备份
- 上传文件备份

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t rebugtracker .
```

### 运行容器
```bash
docker run -d -p 8000:8000 rebugtracker
```

### 使用Docker Compose
```bash
docker-compose up -d
```

## 🌐 Nginx配置

### 反向代理配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## ⚠️ 注意事项

1. **端口冲突**：确保8000端口未被占用
2. **防火墙**：开放相应端口的访问权限
3. **SSL证书**：生产环境建议使用HTTPS
4. **数据库**：确保数据库服务正常运行
5. **备份**：定期备份重要数据

## 🔄 更新部署

### 应用更新流程
1. 备份当前版本
2. 停止服务
3. 更新代码
4. 更新依赖
5. 迁移数据库（如需要）
6. 重启服务
7. 验证功能

### 回滚流程
1. 停止服务
2. 恢复代码版本
3. 恢复数据库（如需要）
4. 重启服务
5. 验证功能
