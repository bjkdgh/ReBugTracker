# ReBugTracker UV 使用指南

本项目现在支持使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理，uv 是一个极快的 Python 包管理器。

## 🚀 快速开始

### 1. 安装 uv

#### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 初始化项目

```bash
# 自动设置项目环境
python uv_setup.py
```

或者手动设置：

```bash
# 初始化 uv 项目
uv init --no-readme

# 从 requirements.txt 添加依赖
uv add -r requirements.txt

# 添加开发依赖
uv add --dev pytest pytest-flask pytest-cov black flake8 mypy

# 同步依赖
uv sync
```

## 📦 依赖管理

### 添加依赖
```bash
# 添加生产依赖
uv add flask==2.3.3

# 添加开发依赖
uv add --dev pytest

# 添加可选依赖组
uv add --optional build pyinstaller
```

### 移除依赖
```bash
uv remove package-name
```

### 更新依赖
```bash
# 更新所有依赖
uv lock --upgrade

# 更新特定依赖
uv add package-name@latest
```

### 查看依赖
```bash
# 查看依赖树
uv tree

# 查看过时的依赖
uv pip list --outdated
```

## 🏃 运行项目

### 运行应用
```bash
# 使用 uv 运行
uv run python rebugtracker.py

# 或使用快捷脚本
python run.py
```

### 运行测试
```bash
# 使用 uv 运行测试
uv run pytest

# 或使用快捷脚本
python test.py

# 运行特定测试
uv run pytest tests/test_specific.py

# 运行测试并生成覆盖率报告
uv run pytest --cov=rebugtracker --cov-report=html
```

### 代码格式化和检查
```bash
# 格式化代码
uv run black .

# 代码检查
uv run flake8 .

# 类型检查
uv run mypy .

# 或使用快捷脚本
python format.py
```

## 🔧 开发工具

### 虚拟环境
```bash
# uv 自动管理虚拟环境，无需手动激活
# 所有命令都通过 uv run 执行

# 如果需要激活虚拟环境（用于IDE等）
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 构建项目
```bash
# 安装构建依赖
uv add --optional build pyinstaller cx-freeze

# 使用 PyInstaller 构建
uv run pyinstaller rebugtracker.spec

# 或使用跨平台构建脚本
cd cross_platform_build
uv run python build_universal.py
```

## 📋 项目配置

### pyproject.toml
项目配置文件包含：
- 项目元数据
- 依赖声明
- 工具配置（black, flake8, mypy, pytest等）
- 构建配置

### uv.lock
自动生成的锁定文件，确保依赖版本一致性。

### .uvignore
指定 uv 应该忽略的文件和目录。

## 🚀 部署

### 生产环境部署
```bash
# 只安装生产依赖
uv sync --no-dev

# 或导出 requirements.txt
uv export --no-dev > requirements-prod.txt
pip install -r requirements-prod.txt
```

### 离线环境部署

#### 方法1：使用 uv 离线包（推荐）

**在有网络的环境中准备：**
```bash
# 1. 创建离线包目录
mkdir rebugtracker-offline
cd rebugtracker-offline

# 2. 复制项目文件
cp -r /path/to/rebugtracker/* .

# 3. 下载所有依赖到本地
uv export --no-dev > requirements.txt
uv pip download -r requirements.txt -d wheels/

# 4. 下载 uv 二进制文件
# Windows
curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip -o uv-windows.zip

# Linux
curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz -o uv-linux.tar.gz

# macOS
curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-apple-darwin.tar.gz -o uv-macos.tar.gz

# 5. 创建离线安装脚本
cat > install_offline.sh << 'EOF'
#!/bin/bash
# ReBugTracker 离线安装脚本

echo "正在安装 ReBugTracker 离线环境..."

# 解压并安装 uv
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    tar -xzf uv-linux.tar.gz
    sudo cp uv /usr/local/bin/
elif [[ "$OSTYPE" == "darwin"* ]]; then
    tar -xzf uv-macos.tar.gz
    sudo cp uv /usr/local/bin/
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    unzip uv-windows.zip
    # Windows 需要手动添加到 PATH
fi

# 创建虚拟环境并安装依赖
uv venv
uv pip install --no-index --find-links wheels/ -r requirements.txt

echo "离线安装完成！"
echo "运行命令: uv run python rebugtracker.py"
EOF

chmod +x install_offline.sh

# 6. 打包整个目录
tar -czf rebugtracker-offline.tar.gz .
```

**在离线环境中部署：**
```bash
# 1. 解压离线包
tar -xzf rebugtracker-offline.tar.gz
cd rebugtracker-offline

# 2. 运行安装脚本
./install_offline.sh

# 3. 启动应用
uv run python rebugtracker.py
```

#### 方法2：使用传统 pip 离线包

**在有网络的环境中准备：**
```bash
# 1. 导出依赖
uv export --no-dev > requirements.txt

# 2. 下载所有依赖包
pip download -r requirements.txt -d offline_packages/

# 3. 创建离线安装脚本
cat > install_offline_pip.sh << 'EOF'
#!/bin/bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 离线安装依赖
pip install --no-index --find-links offline_packages/ -r requirements.txt

echo "离线安装完成！"
echo "激活环境: source .venv/bin/activate"
echo "运行应用: python rebugtracker.py"
EOF

chmod +x install_offline_pip.sh
```

**在离线环境中部署：**
```bash
# 1. 运行安装脚本
./install_offline_pip.sh

# 2. 激活环境并启动
source .venv/bin/activate
python rebugtracker.py
```

#### 方法3：完整系统镜像

**创建完整的离线镜像：**
```bash
# 1. 在有网络的环境中完整安装
uv sync

# 2. 打包整个项目目录（包含 .venv）
tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    -czf rebugtracker-complete.tar.gz .

# 3. 创建启动脚本
cat > start_offline.sh << 'EOF'
#!/bin/bash
# 解压并启动 ReBugTracker

# 解压项目
tar -xzf rebugtracker-complete.tar.gz

# 直接使用打包的虚拟环境
./.venv/bin/python rebugtracker.py
EOF

chmod +x start_offline.sh
```

### Docker 离线部署

**构建离线 Docker 镜像：**
```dockerfile
# 多阶段构建 Dockerfile
FROM python:3.11-slim as builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 复制项目文件
COPY . /app
WORKDIR /app

# 安装依赖到指定目录
RUN uv sync --no-dev

# 生产镜像
FROM python:3.11-slim

# 复制应用和依赖
COPY --from=builder /app /app
WORKDIR /app

# 运行应用
CMD ["python", "rebugtracker.py"]
```

**保存和加载镜像：**
```bash
# 构建镜像
docker build -t rebugtracker:offline .

# 保存镜像到文件
docker save rebugtracker:offline > rebugtracker-docker.tar

# 在离线环境中加载镜像
docker load < rebugtracker-docker.tar

# 运行容器
docker run -p 5000:5000 rebugtracker:offline
```

### 离线环境验证

**验证离线安装：**
```bash
# 1. 断网测试
sudo ifconfig eth0 down  # Linux
# 或禁用网络适配器

# 2. 验证应用启动
uv run python rebugtracker.py
# 或
python rebugtracker.py

# 3. 验证功能
curl http://localhost:5000
```

### Docker 部署
```dockerfile
# 在 Dockerfile 中使用 uv
FROM python:3.11-slim

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 复制项目文件
COPY . /app
WORKDIR /app

# 安装依赖
RUN uv sync --no-dev

# 运行应用
CMD ["uv", "run", "python", "rebugtracker.py"]
```

## 🔄 从 pip/venv 迁移

### 迁移现有项目
```bash
# 1. 备份现有环境
pip freeze > requirements-backup.txt

# 2. 运行迁移脚本
python uv_setup.py

# 3. 验证依赖
uv run python -c "import flask; print('Flask imported successfully')"

# 4. 运行测试确保一切正常
uv run pytest
```

### 保持兼容性
项目仍然支持传统的 pip/venv 方式：
```bash
# 传统方式仍然可用
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python rebugtracker.py
```

## 🎯 最佳实践

1. **使用 uv.lock**：始终提交 uv.lock 文件到版本控制
2. **分离依赖**：区分生产依赖和开发依赖
3. **定期更新**：定期运行 `uv lock --upgrade` 更新依赖
4. **使用脚本**：利用 pyproject.toml 中的脚本简化命令
5. **CI/CD 集成**：在 CI/CD 中使用 `uv sync --frozen` 确保一致性

## 🆚 uv vs pip 对比

| 特性 | uv | pip |
|------|----|----|
| 速度 | 极快 (Rust实现) | 较慢 |
| 依赖解析 | 智能解析 | 基础解析 |
| 锁定文件 | uv.lock | requirements.txt |
| 虚拟环境 | 自动管理 | 手动管理 |
| 缓存 | 全局缓存 | 基础缓存 |
| 配置 | pyproject.toml | 多个配置文件 |

## 🔗 相关链接

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub 仓库](https://github.com/astral-sh/uv)
- [Python 打包指南](https://packaging.python.org/)
- [pyproject.toml 规范](https://peps.python.org/pep-0621/)

---

**提示**：如果遇到问题，可以随时回退到传统的 pip/venv 方式，两种方式可以并存。
