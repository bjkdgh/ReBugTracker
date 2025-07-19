git# ReBugTracker 跨平台打包工具

## 📋 概述

本目录包含 ReBugTracker 在不同操作系统上的打包脚本和配置文件。

## 🗂️ 文件结构

```
cross_platform_build/
├── README.md                    # 本说明文件
├── build_macos.py              # macOS 打包脚本（调用器）
├── build_linux.py              # Linux 打包脚本
├── build_universal.py          # 通用跨平台打包脚本
├── configs/                    # 配置文件目录
│   ├── rebugtracker_macos.spec # macOS PyInstaller 配置
│   ├── rebugtracker_linux.spec # Linux PyInstaller 配置
│   └── app_config_unix.py      # Unix系统环境配置
├── templates/                  # 启动脚本模板
│   ├── start_rebugtracker.sh   # Unix启动脚本模板
│   └── install.sh              # 安装脚本模板
├── macos/                      # macOS 构建系统
│   ├── README.md               # macOS 构建说明
│   ├── build_macos_fixed.py    # macOS 主构建脚本
│   ├── rebugtracker_macos.py   # macOS 启动脚本
│   ├── rebugtracker_macos.spec # macOS PyInstaller 配置
│   ├── app_config_macos.py     # macOS 专用配置
│   ├── crypto_compat_macos.py  # 加密兼容性模块
│   ├── hook-hashlib_macos.py   # PyInstaller 钩子
│   ├── fix_admin_macos.py      # 管理员修复脚本
│   └── test_macos_build.py     # 构建测试脚本
└── windows/                    # Windows 构建系统
    ├── README.md               # Windows 构建说明
    ├── build_windows.py        # Windows 主构建脚本
    ├── build_exe.py            # Windows 传统构建脚本
    ├── rebugtracker.spec       # Windows PyInstaller 配置
    ├── rebugtracker_exe.py     # Windows EXE 启动脚本
    ├── app_config_exe.py       # Windows EXE 专用配置
    ├── deploy.bat              # Windows 一键部署脚本
    ├── deployment_tools/       # Windows 部署工具
    ├── dist/                   # Windows 构建输出目录
    └── *.vbs                   # VBS 后台启动脚本
```

## 🚀 使用方法

### Windows 打包
```bash
# 方法1: 使用新的构建脚本（推荐）
cd cross_platform_build/windows
python build_windows.py

# 方法2: 使用传统构建脚本
cd cross_platform_build/windows
python build_exe.py

# 方法3: 使用一键部署脚本
cd cross_platform_build/windows
deploy.bat
```

### macOS 打包
```bash
# 方法1: 使用调用脚本
cd cross_platform_build
python build_macos.py

# 方法2: 直接使用专用脚本
cd cross_platform_build/macos
python build_macos_fixed.py
```

### Linux 打包
```bash
cd cross_platform_build
python build_linux.py
```

### 通用打包（自动检测系统）
```bash
cd cross_platform_build
python build_universal.py
```

## 📦 输出文件

### Windows
- `windows/dist/ReBugTracker.exe` - 可执行文件
- `windows/dist/start_rebugtracker.bat` - 启动脚本
- `windows/dist/install_service.bat` - 服务安装脚本
- `windows/dist/manage_service.bat` - 服务管理脚本
- `windows/dist/README_EXE.md` - 使用说明
- `windows/dist/配置说明.md` - 配置说明

### macOS
- `dist_mac/ReBugTracker` - 可执行文件
- `dist_mac/start_rebugtracker.sh` - 启动脚本
- `dist_mac/.env` - 环境配置文件
- `dist_mac/配置说明.md` - 配置说明
- `dist_mac/rebugtracker.db` - 数据库文件

### Linux
- `dist/ReBugTracker` - 可执行文件
- `dist/start_rebugtracker.sh` - 启动脚本
- `dist/install.sh` - 安装脚本

## ⚠️ 注意事项

1. **依赖要求**: 需要安装 PyInstaller
2. **权限设置**: 生成的文件需要执行权限
3. **系统兼容**: 在目标系统上打包以确保兼容性
4. **路径处理**: 使用Unix风格的路径分隔符

## 🔧 自定义配置

可以修改 `configs/` 目录下的配置文件来自定义打包行为：
- 修改图标文件路径
- 添加额外的数据文件
- 调整打包选项

## 📞 技术支持

如遇问题，请参考主项目文档或提交Issue。
