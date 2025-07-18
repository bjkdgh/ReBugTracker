# ReBugTracker 跨平台打包工具

## 📋 概述

本目录包含 ReBugTracker 在不同操作系统上的打包脚本和配置文件。

## 🗂️ 文件结构

```
cross_platform_build/
├── README.md                    # 本说明文件
├── build_macos.py              # macOS 打包脚本
├── build_linux.py              # Linux 打包脚本
├── build_universal.py          # 通用跨平台打包脚本
├── configs/                    # 配置文件目录
│   ├── rebugtracker_macos.spec # macOS PyInstaller 配置
│   ├── rebugtracker_linux.spec # Linux PyInstaller 配置
│   └── app_config_unix.py      # Unix系统环境配置
└── templates/                  # 启动脚本模板
    ├── start_rebugtracker.sh   # Unix启动脚本模板
    └── install.sh              # 安装脚本模板
```

## 🚀 使用方法

### macOS 打包
```bash
cd cross_platform_build
python build_macos.py
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

### macOS
- `dist/ReBugTracker` - 可执行文件
- `dist/start_rebugtracker.sh` - 启动脚本
- `dist/install.sh` - 安装脚本

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
