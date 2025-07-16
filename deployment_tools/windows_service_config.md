# ReBugTracker Windows服务配置指南

## 🔧 服务配置说明

### 基本信息
- **服务名称**: ReBugTracker
- **显示名称**: ReBugTracker Bug Tracking System
- **描述**: 企业级缺陷跟踪系统
- **启动类型**: 自动启动
- **运行端口**: 8000 (可通过环境变量配置)

### 文件路径
- **可执行文件**: `.venv\Scripts\python.exe`
- **应用脚本**: `deployment_tools\run_waitress.py`
- **工作目录**: 项目根目录
- **日志目录**: `logs\`

### 环境变量配置
服务会自动读取项目根目录的 `.env` 文件，支持以下配置：

```bash
# 应用端口配置
APP_PORT=8000

# Waitress服务器配置
WAITRESS_THREADS=4

# 数据库配置
DB_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=rebugtracker
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# 应用配置
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key
```

## 📋 服务依赖

### PostgreSQL数据库
如果使用PostgreSQL数据库，服务会自动设置对PostgreSQL服务的依赖：
- **依赖服务**: postgresql-x64-17 (或对应版本)
- **启动顺序**: PostgreSQL → ReBugTracker

### 网络端口
- **HTTP端口**: 8000 (默认)
- **防火墙**: 需要开放对应端口

## 🗂️ 日志管理

### 日志文件位置
- **标准输出**: `logs\service_stdout.log`
- **错误输出**: `logs\service_stderr.log`
- **应用日志**: `logs\rebugtracker.log`

### 日志轮转
- **创建方式**: 追加模式
- **大小限制**: 无限制 (建议定期清理)
- **保留策略**: 手动管理

## 🔄 服务恢复配置

### 自动恢复
- **失败重启**: 启用
- **重启延迟**: 0秒
- **限制重启**: 1500毫秒内不重复重启

### 故障处理
- **程序退出**: 自动重启
- **异常终止**: 自动重启
- **手动停止**: 不重启

## 🛠️ 手动配置 (高级)

### 使用NSSM GUI
```cmd
# 打开NSSM图形界面
deployment_tools\nssm\win64\nssm.exe edit ReBugTracker
```

### 常用NSSM命令
```cmd
# 查看服务配置
nssm get ReBugTracker

# 设置服务参数
nssm set ReBugTracker AppDirectory "C:\path\to\project"
nssm set ReBugTracker AppStdout "C:\path\to\project\logs\stdout.log"
nssm set ReBugTracker AppStderr "C:\path\to\project\logs\stderr.log"

# 设置环境变量
nssm set ReBugTracker AppEnvironmentExtra "APP_PORT=8000"

# 设置服务依赖
nssm set ReBugTracker DependOnService postgresql-x64-17
```

## 🔍 故障排除

### 服务启动失败
1. **检查Python环境**
   ```cmd
   .venv\Scripts\python.exe --version
   ```

2. **检查依赖包**
   ```cmd
   .venv\Scripts\python.exe -c "import waitress, flask"
   ```

3. **检查配置文件**
   ```cmd
   type .env
   ```

4. **查看错误日志**
   ```cmd
   type logs\service_stderr.log
   ```

### 数据库连接问题
1. **检查PostgreSQL服务**
   ```cmd
   sc query postgresql-x64-17
   ```

2. **测试数据库连接**
   ```cmd
   .venv\Scripts\python.exe -c "from db_factory import get_db_connection; get_db_connection()"
   ```

### 端口占用问题
```cmd
# 检查端口占用
netstat -ano | findstr 8000

# 终止占用进程
taskkill /PID <进程ID> /F
```

## 📊 性能监控

### 系统资源
- **内存使用**: 通过任务管理器监控
- **CPU使用**: 通过性能监视器监控
- **磁盘I/O**: 通过资源监视器监控

### 应用监控
- **访问日志**: 查看 `logs\service_stdout.log`
- **错误统计**: 查看 `logs\service_stderr.log`
- **响应时间**: 通过Web界面监控

## 🔐 安全配置

### 服务账户
- **默认**: Local System (推荐)
- **自定义**: 可配置专用服务账户

### 网络安全
- **防火墙**: 仅开放必要端口
- **访问控制**: 通过应用层控制
- **HTTPS**: 建议配置SSL证书

### 数据安全
- **数据库**: 使用强密码
- **备份**: 定期备份数据
- **日志**: 定期清理敏感信息

## 📝 维护建议

### 定期维护
- **日志清理**: 每月清理旧日志
- **数据备份**: 每周备份数据库
- **更新检查**: 定期检查应用更新

### 监控告警
- **服务状态**: 监控服务运行状态
- **磁盘空间**: 监控日志目录空间
- **数据库**: 监控数据库连接状态

---

**配置完成后，ReBugTracker将作为稳定的Windows服务运行！** 🚀
