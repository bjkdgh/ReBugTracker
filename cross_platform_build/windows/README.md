# ReBugTracker Windows 构建系统

这个目录包含了 ReBugTracker 在 Windows 平台上的构建脚本和相关文件。

## 📁 目录结构

```
cross_platform_build/windows/
├── build_windows.py          # 主构建脚本（推荐使用）
├── build_exe.py             # 传统构建脚本
├── rebugtracker.spec        # PyInstaller 配置文件
├── rebugtracker_exe.py      # EXE 启动脚本
├── app_config_exe.py        # EXE 专用配置
├── deploy.bat               # Windows 一键部署脚本
├── deployment_tools/        # 部署工具
│   ├── nssm.exe            # Windows 服务管理工具
│   └── run_waitress.py     # Waitress 服务器启动脚本
├── dist/                   # 构建输出目录
├── start_rebugtracker.vbs  # VBS 后台启动脚本
├── start_rebugtracker_example.vbs  # VBS 脚本示例
├── nginx_windows_config_example.conf  # Nginx 配置示例
└── README.md               # 本文件
```

## 🚀 快速开始

### 方法1: 使用新的构建脚本（推荐）

```bash
# 进入 Windows 构建目录
cd cross_platform_build/windows

# 运行构建脚本
python build_windows.py
```

### 方法2: 使用传统构建脚本

```bash
# 进入 Windows 构建目录
cd cross_platform_build/windows

# 运行传统构建脚本
python build_exe.py
```

### 方法3: 使用一键部署脚本

```bash
# 进入 Windows 构建目录
cd cross_platform_build/windows

# 运行部署脚本
deploy.bat
```

## 📋 构建要求

- **操作系统**: Windows 10/11 或 Windows Server 2016+
- **Python**: 3.8 或更高版本
- **依赖包**: PyInstaller, 以及 requirements.txt 中的所有依赖

### 安装依赖

```bash
# 安装 PyInstaller
pip install pyinstaller

# 安装项目依赖（在项目根目录执行）
pip install -r requirements.txt
```

## 🔧 构建选项

### 构建脚本功能对比

| 功能 | build_windows.py | build_exe.py | deploy.bat |
|------|------------------|--------------|------------|
| 系统检查 | ✅ | ✅ | ✅ |
| 环境设置 | ✅ | ✅ | ✅ |
| 清理构建目录 | ✅ | ✅ | ✅ |
| PyInstaller 打包 | ✅ | ✅ | ✅ |
| 复制额外文件 | ✅ | ✅ | ✅ |
| 创建启动脚本 | ✅ | ✅ | ✅ |
| 创建配置说明 | ✅ | ✅ | ✅ |
| 虚拟环境支持 | ✅ | ❌ | ✅ |
| 数据库配置 | ✅ | ❌ | ✅ |
| 服务安装 | ❌ | ❌ | ✅ |
| VBS 后台运行 | ❌ | ❌ | ✅ |

## 📦 构建输出

构建完成后，所有文件将输出到项目根目录的 `dist/` 目录：

**输出路径**: `项目根目录/dist/`

```
dist/
├── ReBugTracker.exe         # 主程序
├── start_rebugtracker.bat   # 启动脚本
├── install_service.bat      # 服务安装脚本
├── manage_service.bat       # 服务管理脚本
├── nssm.exe                # 服务管理工具
├── README_EXE.md           # 使用说明
├── 配置说明.md              # 配置说明
├── 故障排除指南.md          # 故障排除指南
├── Windows服务安装手册.md   # 服务安装手册
├── .env                    # 环境配置文件
├── rebugtracker.db         # 数据库文件
├── uploads/                # 上传文件目录
├── logs/                   # 日志目录
├── data_exports/           # 数据导出目录
├── test_upload_config.py   # 配置测试脚本
└── fix_uploads.py          # 上传修复脚本
```

**⚠️ 重要提示**:
- 构建脚本会显示最终输出目录的完整路径
- 如果遇到图片上传问题，请检查 `.env` 文件中的 `UPLOAD_FOLDER` 配置
- 建议使用绝对路径配置 `UPLOAD_FOLDER`

## 🎯 部署方式

### 1. 直接运行
```bash
cd dist
ReBugTracker.exe
```

### 2. 使用启动脚本
```bash
cd dist
start_rebugtracker.bat
```

### 3. 安装为 Windows 服务
```bash
cd dist
install_service.bat
```

### 4. VBS 后台运行
```bash
# 使用 VBS 脚本后台运行
wscript.exe start_rebugtracker.vbs
```

## ⚙️ 配置说明

- **配置文件**: `dist/app_config.ini` 或 `.env` 文件
- **数据库**: 默认使用 SQLite，可配置为 PostgreSQL
- **端口**: 默认 5000，可在配置文件中修改
- **日志**: 输出到 `logs/` 目录

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
   - 以管理员身份运行构建脚本
   - 确保有写入权限

4. **路径问题**
   - 确保在正确的目录中运行脚本
   - 检查项目根目录结构

### 调试模式

如果遇到问题，可以：

1. 检查构建日志输出
2. 查看 `logs/` 目录中的日志文件
3. 使用 `python rebugtracker_exe.py` 直接运行测试

## 🔄 功能特性

Windows构建版本包含完整的ReBugTracker功能：

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

## 📚 相关文档

- [项目主文档](../../README.md)
- [部署指南](../../DEPLOYMENT_GUIDE.md)
- [跨平台构建说明](../README.md)

## 🤝 贡献

如果您发现问题或有改进建议，请：

1. 提交 Issue
2. 创建 Pull Request
3. 参与讨论

---

**注意**: 这是新的构建系统，如果遇到问题，可以回退到项目根目录使用原有的构建脚本。
