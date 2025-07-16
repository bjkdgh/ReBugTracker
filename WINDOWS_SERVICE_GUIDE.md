# ReBugTracker Windows服务部署指南

## 🎯 概述

ReBugTracker现在完全支持Windows服务部署，使用NSSM (Non-Sucking Service Manager) 工具将应用安装为Windows系统服务，实现开机自启动和后台稳定运行。

## 📦 工具包内容

### deployment_tools目录包含：
- **nssm-2.24.zip** - NSSM Windows服务管理器
- **postgresql-17.5-3-windows-x64.exe** - PostgreSQL 17.5 Windows安装包
- **install_windows_service.bat** - Windows服务安装脚本
- **uninstall_windows_service.bat** - Windows服务卸载脚本
- **manage_windows_service.bat** - Windows服务管理工具
- **start_service.bat** - 快速启动服务脚本
- **run_waitress.py** - 生产环境WSGI服务器
- **windows_service_config.md** - 详细配置说明

## 🚀 快速部署

### 1. 一键部署
```cmd
# 运行主部署脚本
deploy.bat
```

部署脚本会：
- ✅ 自动检测PostgreSQL，提供安装选项
- ✅ 创建Python虚拟环境
- ✅ 安装所有依赖包
- ✅ 配置数据库连接
- ✅ 提供Windows服务安装选项

### 2. 手动安装Windows服务
```cmd
# 安装为Windows服务
deployment_tools\install_windows_service.bat

# 管理Windows服务
deployment_tools\manage_windows_service.bat

# 快速启动服务
deployment_tools\start_service.bat
```

## 🔧 服务特性

### 自动化配置
- ✅ **自动解压NSSM工具**
- ✅ **自动配置服务参数**
- ✅ **自动设置日志记录**
- ✅ **自动配置服务依赖** (PostgreSQL)
- ✅ **自动设置故障恢复**

### 服务管理
- ✅ **图形化管理界面**
- ✅ **启动/停止/重启服务**
- ✅ **实时状态监控**
- ✅ **日志查看功能**
- ✅ **配置参数管理**

### 生产环境优化
- ✅ **Waitress WSGI服务器**
- ✅ **多线程处理**
- ✅ **自动故障恢复**
- ✅ **完整日志记录**
- ✅ **环境变量支持**

## 📋 服务信息

### 基本配置
- **服务名称**: ReBugTracker
- **显示名称**: ReBugTracker Bug Tracking System
- **启动类型**: 自动启动
- **运行端口**: 8000 (可配置)
- **工作目录**: 项目根目录

### 文件路径
- **Python解释器**: `.venv\Scripts\python.exe`
- **应用脚本**: `deployment_tools\run_waitress.py`
- **配置文件**: `.env`
- **日志目录**: `logs\`

### 日志文件
- **标准输出**: `logs\service_stdout.log`
- **错误输出**: `logs\service_stderr.log`
- **应用日志**: `logs\rebugtracker.log`

## 🎮 管理命令

### Windows服务命令
```cmd
# 启动服务
net start ReBugTracker

# 停止服务
net stop ReBugTracker

# 查看状态
sc query ReBugTracker

# 重启服务
net stop ReBugTracker && net start ReBugTracker
```

### 管理工具
```cmd
# 图形化管理工具
deployment_tools\manage_windows_service.bat

# 快速启动
deployment_tools\start_service.bat

# 卸载服务
deployment_tools\uninstall_windows_service.bat
```

## 🌐 访问应用

### 默认访问
- **地址**: http://localhost:8000
- **管理员**: admin / admin

### 测试账号
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin |
| 负责人 | zjn | 123456 |
| 实施组 | gh | 123456 |
| 组内成员 | wbx | 123456 |

## 🔍 故障排除

### 常见问题

**1. 服务启动失败**
```cmd
# 检查错误日志
type logs\service_stderr.log

# 检查Python环境
.venv\Scripts\python.exe --version

# 手动测试启动
.venv\Scripts\python.exe deployment_tools\run_waitress.py
```

**2. 数据库连接问题**
```cmd
# 检查PostgreSQL服务
sc query postgresql-x64-17

# 测试数据库连接
.venv\Scripts\python.exe -c "from db_factory import get_db_connection; get_db_connection()"
```

**3. 端口占用**
```cmd
# 检查端口占用
netstat -ano | findstr 8000

# 修改端口配置
echo APP_PORT=8080 >> .env
```

## 🔐 安全建议

### 生产环境配置
1. **修改默认密码**
2. **配置防火墙规则**
3. **使用HTTPS证书**
4. **定期备份数据**
5. **监控服务状态**

### 服务账户
- 默认使用 Local System 账户
- 可配置专用服务账户
- 确保账户有必要权限

## 📊 性能优化

### 配置参数
```bash
# .env文件配置
APP_PORT=8000
WAITRESS_THREADS=4
DB_TYPE=postgres
FLASK_ENV=production
```

### 监控指标
- CPU使用率
- 内存占用
- 响应时间
- 并发连接数

## 🎉 优势总结

### 对比传统部署
- ✅ **开机自启动** vs 手动启动
- ✅ **后台运行** vs 前台运行
- ✅ **自动恢复** vs 手动重启
- ✅ **系统集成** vs 独立运行
- ✅ **日志管理** vs 控制台输出

### 企业级特性
- ✅ **服务依赖管理**
- ✅ **故障自动恢复**
- ✅ **完整日志记录**
- ✅ **图形化管理**
- ✅ **配置集中管理**

---

**现在ReBugTracker可以作为稳定的Windows服务运行，提供企业级的可靠性和易管理性！** 🚀

## 📞 技术支持

如有问题，请查看：
1. `deployment_tools\windows_service_config.md` - 详细配置说明
2. `logs\` 目录中的日志文件
3. Windows事件查看器中的系统日志
