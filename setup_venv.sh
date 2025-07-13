#!/bin/bash
# ReBugTracker 虚拟环境设置脚本 (Linux/macOS)

echo "ReBugTracker 虚拟环境设置"
echo "============================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found. Please install Python 3.9+"
    exit 1
fi

echo "Python version:"
python3 --version

# 检查是否已存在虚拟环境
if [ -d ".venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf .venv
    else
        echo "Using existing virtual environment."
        source .venv/bin/activate
        echo "Virtual environment activated."
        exit 0
    fi
fi

# 创建虚拟环境
echo "Creating virtual environment..."
python3 -m venv .venv

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source .venv/bin/activate

# 升级pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# 安装依赖
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "================================"
echo "Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "To start ReBugTracker:"
echo "  python rebugtracker.py"
echo ""
