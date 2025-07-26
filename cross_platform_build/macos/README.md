# ReBugTracker macOS 构建系统

这个目录包含了 ReBugTracker 在 macOS 平台上的构建脚本和相关文件。

## 📁 目录结构

```
cross_platform_build/macos/
├── README.md                    # 本说明文件
├── build_macos_fixed.py         # 主构建脚本（修复版）
├── rebugtracker_macos.py        # macOS 启动脚本
├── rebugtracker_macos.spec      # PyInstaller 配置文件
├── app_config_macos.py          # macOS 专用配置
├── crypto_compat_macos.py       # 加密兼容性模块
├── hook-hashlib_macos.py        # PyInstaller hashlib 钩子
├── fix_admin_macos.py           # 管理员修复脚本
├── test_macos_build.py          # 构建测试脚本
├── uploads/                     # 上传文件目录
├── logs/                        # 日志目录
└── data_exports/                # 数据导出目录
```

## 🚀 快速开始

### 方法1: 使用修复版构建脚本（推荐）

```bash
# 进入 macOS 构建目录
cd cross_platform_build/macos

# 运行构建脚本
python build_macos_fixed.py
```

### 方法2: 使用外层调用脚本

```bash
# 进入跨平台构建目录
cd cross_platform_build

# 运行 macOS 构建脚本（会自动调用 macos 目录下的脚本）
python build_macos.py
```

### 方法3: 使用通用构建脚本

```bash
# 进入跨平台构建目录
cd cross_platform_build

# 运行通用构建脚本（自动检测 macOS）
python build_universal.py
```

## 📋 构建要求

- **操作系统**: macOS 10.14 (Mojave) 或更高版本
- **Python**: 3.8 或更高版本
- **依赖包**: PyInstaller, 以及 requirements.txt 中的所有依赖

### 安装依赖

```bash
# 安装 PyInstaller
pip install pyinstaller

# 安装项目依赖（在项目根目录执行）
pip install -r requirements.txt
```

## 🔧 macOS 特殊功能

### 1. 加密兼容性修复
- **crypto_compat_macos.py**: 解决 macOS 上 hashlib.pbkdf2_hmac 缺失问题
- **hook-hashlib_macos.py**: PyInstaller 钩子，确保加密模块正确打包

### 2. 端口管理
- 默认端口从 10001 开始（避免与系统服务冲突）
- 自动检测端口占用并寻找可用端口
- 支持自定义端口配置

### 3. 路径处理
- 自动处理 macOS 应用包结构
- 支持开发环境和打包环境的路径切换
- 正确处理资源文件路径

## 📦 构建输出

构建完成后，文件将输出到项目根目录的 `dist_mac/` 目录：

```
dist_mac/
├── ReBugTracker                 # 主程序可执行文件
├── start_rebugtracker.sh        # 启动脚本
├── rebugtracker.db             # 数据库文件
├── uploads/                    # 上传文件目录
├── logs/                       # 日志目录
├── data_exports/               # 数据导出目录
├── .env                        # 环境配置文件
└── 配置说明.md                  # 配置说明文档
```

## 🎯 部署方式

### 1. 直接运行
```bash
cd dist_mac
./ReBugTracker
```

### 2. 使用启动脚本（推荐）
```bash
cd dist_mac
./start_rebugtracker.sh
```

### 3. 后台运行
```bash
cd dist_mac
nohup ./ReBugTracker > app.log 2>&1 &
```

## ⚙️ 配置说明

### 环境变量配置
- **配置文件**: `dist_mac/.env`
- **默认端口**: 10001（可在 .env 中修改 SERVER_PORT）
- **数据库**: 默认使用 SQLite，可配置为 PostgreSQL
- **日志级别**: 默认 INFO，可配置为 DEBUG

### 常用配置项
```bash
# 修改端口
SERVER_PORT=8080

# 切换到 PostgreSQL
DB_TYPE=postgres
DATABASE_HOST=localhost
DATABASE_NAME=rebugtracker
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# 修改上传目录
UPLOAD_FOLDER=/path/to/uploads

# 修改日志级别
LOG_LEVEL=DEBUG
```

## 🔍 故障排除

### 常见问题

1. **PyInstaller 未安装**
   ```bash
   pip install pyinstaller
   ```

2. **缺少依赖包**
   ```bash
   pip install -r requirements.txt
   ```

3. **权限问题**
   ```bash
   chmod +x dist_mac/ReBugTracker
   chmod +x dist_mac/start_rebugtracker.sh
   ```

4. **端口占用**
   - 修改 `.env` 文件中的 `SERVER_PORT`
   - 或让程序自动寻找可用端口

5. **加密模块问题**
   - 构建脚本已包含 crypto_compat_macos.py 修复
   - 如仍有问题，检查 Python 版本和 OpenSSL 版本

### 调试模式

如果遇到问题，可以：

1. 运行测试脚本：
   ```bash
   python test_macos_build.py
   ```

2. 检查构建日志输出

3. 查看 `logs/` 目录中的应用日志

4. 使用调试模式运行：
   ```bash
   python rebugtracker_macos.py
   ```

## 🧪 测试功能

### 构建测试
```bash
# 运行构建测试
python test_macos_build.py
```

### 管理员修复
```bash
# 如果管理员账户有问题，运行修复脚本
python fix_admin_macos.py
```

## 📚 技术细节

### 1. 加密兼容性
- 解决了 macOS 上 hashlib.pbkdf2_hmac 在打包后缺失的问题
- 提供了兼容性实现，确保密码哈希功能正常

### 2. PyInstaller 配置
- 使用专门的 spec 文件配置
- 包含所有必要的隐藏导入
- 正确处理数据文件和资源

### 3. 路径管理
- 支持开发环境和打包环境
- 自动检测应用目录
- 正确处理相对路径和绝对路径

## 🔄 功能特性

macOS构建版本包含完整的ReBugTracker功能：

### 核心功能
- **问题管理**：创建、分配、处理、解决问题
- **状态流转**：待处理 → 已分配 → 处理中 → 已解决 → 已完成
- **驳回功能**：负责人可驳回待处理或已分配的问题
- **通知系统**：邮件、Gotify推送、应用内通知
- **用户权限**：管理员、负责人、组内成员、实施组四级权限
- **数据分析**：图表统计、数据导出

### 状态说明
| 状态 | 说明 | 可执行操作 |
|------|------|----------|
| 待处理 | 新提交问题 | 分配、驳回 |
| 已分配 | 已分配处理人 | 开始处理、驳回 |
| 处理中 | 正在处理 | 标记已解决 |
| 已解决 | 等待确认 | 确认闭环 |
| 已驳回 | 被驳回问题 | 重新提交 |
| 已完成 | 流程结束 | 查看记录 |

### macOS 特有优化
- **加密兼容性**：解决了 hashlib.pbkdf2_hmac 打包问题
- **路径管理**：智能处理 macOS 应用包路径
- **权限处理**：适配 macOS 安全策略
- **性能优化**：针对 Apple Silicon 和 Intel 芯片优化

## 🔗 相关文档

- [项目主文档](../../README.md)
- [部署指南](../../DEPLOYMENT_GUIDE.md)
- [跨平台构建说明](../README.md)
- [Windows 构建说明](../windows/README.md)
- [状态工作流程](../../docs/bug_status_workflow_guide.md)

## 🤝 贡献

如果您发现问题或有改进建议，请：

1. 提交 Issue
2. 创建 Pull Request
3. 参与讨论

---

**注意**: 这是专门为 macOS 优化的构建系统，包含了针对 macOS 特有问题的修复和优化。
