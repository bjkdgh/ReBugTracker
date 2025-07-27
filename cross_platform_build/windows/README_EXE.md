# ReBugTracker 可执行版本

## 📋 使用说明

### 快速启动
1. 双击 `start_rebugtracker.bat` 启动应用
2. 或者直接运行 `ReBugTracker.exe`
3. 应用启动后会自动打开浏览器访问 http://127.0.0.1:5000

### 文件说明
- `ReBugTracker.exe` - 主程序
- `start_rebugtracker.bat` - 启动脚本
- `配置说明.md` - 配置修改说明文档
- `故障排除指南.md` - 常见问题解决方案
- `rebugtracker.db` - SQLite数据库文件
- `.env` - 环境变量配置文件（自动生成）
- `.env.template` - 配置模板文件
- `uploads/` - 文件上传目录
- `logs/` - 日志文件目录
- `data_exports/` - 数据导出目录
- `test_upload_config.py` - 上传配置测试脚本
- `fix_uploads.py` - 上传问题修复脚本

### 配置修改
1. **编辑配置文件**: 用记事本打开 `.env` 文件进行修改
2. **参考说明**: 查看 `配置说明.md` 了解详细配置方法

### 常用配置修改
- **修改端口**: 在.env中设置 `SERVER_PORT=8080`
- **切换数据库**: 设置 `DB_TYPE=postgres` 并配置数据库连接
- **修改上传目录**: 设置 `UPLOAD_FOLDER=D:\MyUploads`
- **配置邮件**: 设置SMTP服务器相关参数

### 配置修改步骤
1. 停止ReBugTracker应用
2. 用记事本打开 `.env` 文件: `notepad .env`
3. 修改需要的配置项
4. 保存文件
5. 重新启动应用

### 注意事项
1. 首次运行会自动初始化数据库
2. 默认管理员账号: admin / admin
3. 请及时修改默认密码
4. 数据库文件包含所有数据，请注意备份
5. 修改配置后需要重启应用

### 故障排除

#### 常见问题
1. **端口占用**: 如果端口5000被占用，程序会自动寻找其他可用端口
2. **启动失败**: 请检查控制台输出的错误信息
3. **磁盘空间**: 确保有足够的磁盘空间用于数据库和上传文件

#### 图片上传问题 ⚠️ 重要
**问题现象**: 图片上传成功但无法在网页中显示

**解决方法**:
1. 打开 `.env` 文件
2. 找到 `UPLOAD_FOLDER` 配置项
3. 将其修改为绝对路径，例如:
   ```
   UPLOAD_FOLDER=D:\app_data\repositories\ReBugTracker\dist\uploads
   ```
4. 重启应用程序

**快速诊断**:
- 访问 http://localhost:5000/debug/uploads 查看上传配置
- 运行 `python fix_uploads.py` 自动修复
- 查看 `故障排除指南.md` 获取详细解决步骤

### 技术支持
- 项目地址: https://github.com/bjkdgh/ReBugTracker
- 问题反馈: 请在GitHub上提交Issue

---
构建时间: 2025-07-18 10:42:16
