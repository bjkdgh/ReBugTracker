#!/bin/bash
# ReBugTracker 全功能一键部署脚本
# 支持Docker和本地部署，支持PostgreSQL和SQLite数据库
# 适用于全新机器，零基础用户

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 全局变量
DEPLOYMENT_MODE=""
DATABASE_TYPE=""
USE_DOCKER=""
DOCKER_COMPOSE_FILE=""
DOCKER_COMPOSE_CMD=""
PROJECT_DIR=$(pwd)
VENV_PATH="$PROJECT_DIR/.venv"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="rebugtracker"
DB_USER="postgres"
DB_PASSWORD=""

# 系统信息变量
OS=""
DISTRO=""
VERSION=""
ARCH=""
PKG_MANAGER=""
PKG_UPDATE=""
PKG_INSTALL=""
SERVICE_MANAGER=""
SERVICE_START=""
SERVICE_ENABLE=""
PYTHON_CMD=""
IS_APPLE_SILICON=false

# 打印带颜色的消息
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_step() { echo -e "${PURPLE}🔧 $1${NC}"; }
print_choice() { echo -e "${CYAN}👉 $1${NC}"; }

# 分隔线
print_separator() {
    echo "=================================================="
}

# 欢迎界面
welcome() {
    clear
    echo "🚀 ReBugTracker 全功能一键部署脚本"
    print_separator
    echo ""
    echo "本脚本支持多种部署方式，适合不同使用场景："
    echo ""
    echo "📦 Docker部署 (推荐)"
    echo "   • 环境隔离，一键启动"
    echo "   • 支持PostgreSQL和SQLite"
    echo "   • 适合生产环境和开发环境"
    echo ""
    echo "💻 本地部署"
    echo "   • 使用Python虚拟环境"
    echo "   • 支持PostgreSQL和SQLite"
    echo "   • 适合开发调试"
    echo ""
    echo "🗄️ 数据库选择"
    echo "   • PostgreSQL: 高性能，适合生产环境"
    echo "   • SQLite: 轻量级，适合小团队"
    echo ""
    echo "🔧 故障诊断"
    echo "   • 如遇到 Docker 问题，可运行: ./deploy.sh --diagnose"
    echo "   • 提供详细的环境检查和故障排除建议"
    echo ""
    print_info "脚本将引导您完成所有配置，无需手动修改配置文件"
    echo ""
    read -p "按回车键开始部署..." -r
}

# Docker 诊断功能
diagnose_docker_macos() {
    print_step "Docker 环境诊断..."
    echo ""

    print_info "=== Docker 命令检查 ==="
    if command -v docker &> /dev/null; then
        print_success "✓ docker 命令可用"
        echo "  路径: $(which docker)"
        echo "  版本: $(docker --version 2>/dev/null || echo '获取版本失败')"
    else
        print_error "✗ docker 命令不可用"
    fi

    echo ""
    print_info "=== Docker 服务状态 ==="
    if docker info &> /dev/null 2>&1; then
        print_success "✓ Docker 服务运行中"
        echo "  容器数量: $(docker ps -q | wc -l | tr -d ' ')"
        echo "  镜像数量: $(docker images -q | wc -l | tr -d ' ')"
        echo "  运行中容器: $(docker ps --format 'table {{.Names}}\t{{.Status}}' | tail -n +2 | wc -l | tr -d ' ')"
        echo "  Docker 根目录: $(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo '未知')"
        echo "  存储驱动: $(docker info --format '{{.Driver}}' 2>/dev/null || echo '未知')"
    else
        print_warning "✗ Docker 服务未运行或无法连接"
        local docker_error=$(docker info 2>&1 | head -3)
        echo "  错误信息: $docker_error"

        # 提供详细的错误分析
        if echo "$docker_error" | grep -q "Cannot connect to the Docker daemon"; then
            print_info "  分析: Docker 守护进程未运行"
        elif echo "$docker_error" | grep -q "permission denied"; then
            print_info "  分析: 权限问题，可能需要将用户添加到 docker 组"
        elif echo "$docker_error" | grep -q "dial unix"; then
            print_info "  分析: Docker socket 连接问题"
        fi
    fi

    echo ""
    print_info "=== Docker 安装检测 ==="

    # Docker Desktop
    if [ -d "/Applications/Docker.app" ]; then
        print_success "✓ Docker Desktop 已安装"
        echo "  路径: /Applications/Docker.app"

        # 检查 Docker Desktop 是否正在运行
        if pgrep -f "Docker Desktop" > /dev/null; then
            print_success "  状态: 正在运行"
        else
            print_warning "  状态: 未运行"
        fi

        # 检查 Docker Desktop 版本
        local desktop_version=""
        if [ -f "/Applications/Docker.app/Contents/Info.plist" ]; then
            desktop_version=$(defaults read /Applications/Docker.app/Contents/Info.plist CFBundleShortVersionString 2>/dev/null || echo "未知")
            echo "  版本: $desktop_version"
        fi
    else
        print_info "✗ Docker Desktop 未检测到"
    fi

    # Homebrew Docker
    if command -v brew &> /dev/null; then
        if brew list --cask 2>/dev/null | grep -q "^docker$"; then
            print_success "✓ Homebrew Docker 已安装"
            local brew_docker_version=$(brew list --cask --versions docker 2>/dev/null | cut -d' ' -f2 || echo "未知")
            echo "  版本: $brew_docker_version"
        else
            print_info "✗ Homebrew Docker 未安装"
        fi
    else
        print_info "✗ Homebrew 不可用"
    fi

    # Colima
    if command -v colima &> /dev/null; then
        print_success "✓ Colima 已安装"
        echo "  版本: $(colima version 2>/dev/null || echo '获取版本失败')"
        local colima_status=$(colima status 2>/dev/null || echo '获取状态失败')
        echo "  状态: $colima_status"

        if echo "$colima_status" | grep -q "Running"; then
            print_success "  Colima 正在运行"
        else
            print_warning "  Colima 未运行"
        fi
    else
        print_info "✗ Colima 未安装"
    fi

    echo ""
    print_info "=== Docker Compose 检查 ==="
    if docker compose version &> /dev/null; then
        print_success "✓ Docker Compose V2 可用"
        echo "  版本: $(docker compose version --short 2>/dev/null || echo '获取版本失败')"
    elif command -v docker-compose &> /dev/null; then
        print_success "✓ Docker Compose V1 可用"
        echo "  版本: $(docker-compose --version 2>/dev/null || echo '获取版本失败')"
    else
        print_error "✗ Docker Compose 不可用"
    fi

    echo ""
    print_info "=== 网络连接检查 ==="
    if ping -c 1 docker.io &> /dev/null; then
        print_success "✓ 可以连接到 Docker Hub"
    else
        print_warning "✗ 无法连接到 Docker Hub"
        echo "  这可能影响镜像下载"
    fi

    echo ""
    print_info "=== 系统资源检查 ==="
    echo "  操作系统: $(sw_vers -productName) $(sw_vers -productVersion)"
    echo "  架构: $(uname -m)"
    echo "  内存: $(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024) "GB"}')"
    echo "  CPU 核心: $(sysctl -n hw.ncpu)"
    echo "  磁盘空间: $(df -h / | tail -1 | awk '{print $4}') 可用"
    echo "  Shell: $SHELL"

    echo ""
    print_info "=== 环境变量检查 ==="
    echo "  PATH: $PATH"
    if [ -n "$DOCKER_HOST" ]; then
        echo "  DOCKER_HOST: $DOCKER_HOST"
    else
        echo "  DOCKER_HOST: 未设置"
    fi

    echo ""
    print_info "=== 故障排除建议 ==="
    if ! command -v docker &> /dev/null; then
        print_warning "Docker 未安装，建议："
        echo "  1. 安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
        echo "  2. 或使用 Homebrew: brew install --cask docker"
        echo "  3. 或使用 Colima: brew install colima docker"
    elif ! docker info &> /dev/null 2>&1; then
        print_warning "Docker 已安装但未运行，建议："
        echo "  1. 启动 Docker Desktop 应用"
        echo "  2. 或运行: colima start (如果使用 Colima)"
        echo "  3. 检查系统资源是否充足"
        echo "  4. 重启 Docker 服务"
    else
        print_success "Docker 环境正常"
    fi

    echo ""
    read -p "按回车键继续部署，或按 Ctrl+C 退出..." -r
}

# Linux Docker 诊断功能
diagnose_docker_linux() {
    print_step "Docker 环境诊断..."
    echo ""

    print_info "=== Docker 命令检查 ==="
    if command -v docker &> /dev/null; then
        print_success "✓ docker 命令可用"
        echo "  路径: $(which docker)"
        echo "  版本: $(docker --version 2>/dev/null || echo '获取版本失败')"
    else
        print_error "✗ docker 命令不可用"
    fi

    echo ""
    print_info "=== Docker 服务状态 ==="
    if docker info &> /dev/null 2>&1; then
        print_success "✓ Docker 服务运行中"
        echo "  容器数量: $(docker ps -q | wc -l | tr -d ' ')"
        echo "  镜像数量: $(docker images -q | wc -l | tr -d ' ')"
        echo "  运行中容器: $(docker ps --format 'table {{.Names}}\t{{.Status}}' | tail -n +2 | wc -l | tr -d ' ')"
        echo "  Docker 根目录: $(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo '未知')"
        echo "  存储驱动: $(docker info --format '{{.Driver}}' 2>/dev/null || echo '未知')"
    else
        print_warning "✗ Docker 服务未运行或无法连接"
        local docker_error=$(docker info 2>&1 | head -3)
        echo "  错误信息: $docker_error"

        # 提供详细的错误分析
        if echo "$docker_error" | grep -q "Cannot connect to the Docker daemon"; then
            print_info "  分析: Docker 守护进程未运行"
        elif echo "$docker_error" | grep -q "permission denied"; then
            print_info "  分析: 权限问题，可能需要将用户添加到 docker 组"
        elif echo "$docker_error" | grep -q "dial unix"; then
            print_info "  分析: Docker socket 连接问题"
        fi
    fi

    echo ""
    print_info "=== Docker 安装检测 ==="
    if command -v docker &> /dev/null; then
        print_success "✓ Docker 已安装"
        local docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | cut -d',' -f1 || echo "未知")
        echo "  版本: $docker_version"
    else
        print_error "✗ Docker 未安装"
    fi

    echo ""
    print_info "=== Docker Compose 检查 ==="
    if docker compose version &> /dev/null; then
        print_success "✓ Docker Compose V2 可用"
        echo "  版本: $(docker compose version --short 2>/dev/null || echo '获取版本失败')"
    elif command -v docker-compose &> /dev/null; then
        print_success "✓ Docker Compose V1 可用"
        echo "  版本: $(docker-compose --version 2>/dev/null || echo '获取版本失败')"
    else
        print_error "✗ Docker Compose 不可用"
    fi

    echo ""
    print_info "=== 系统服务检查 ==="
    if command -v systemctl &> /dev/null; then
        local docker_status=$(systemctl is-active docker 2>/dev/null || echo "未知")
        echo "  Docker 服务状态: $docker_status"
        local docker_enabled=$(systemctl is-enabled docker 2>/dev/null || echo "未知")
        echo "  Docker 开机启动: $docker_enabled"
    fi

    echo ""
    print_info "=== 用户权限检查 ==="
    if groups | grep -q docker; then
        print_success "✓ 当前用户在 docker 组中"
    else
        print_warning "✗ 当前用户不在 docker 组中"
        echo "  建议运行: sudo usermod -aG docker $USER"
    fi

    echo ""
    print_info "=== 网络连接检查 ==="
    if ping -c 1 docker.io &> /dev/null; then
        print_success "✓ 可以连接到 Docker Hub"
    else
        print_warning "✗ 无法连接到 Docker Hub"
        echo "  这可能影响镜像下载"
    fi

    echo ""
    print_info "=== 系统资源检查 ==="
    echo "  操作系统: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '"' || echo '未知')"
    echo "  架构: $(uname -m)"
    echo "  内核版本: $(uname -r)"
    echo "  内存: $(free -h | grep Mem | awk '{print $2}') 总计, $(free -h | grep Mem | awk '{print $7}') 可用"
    echo "  CPU 核心: $(nproc)"
    echo "  磁盘空间: $(df -h / | tail -1 | awk '{print $4}') 可用"

    echo ""
    print_info "=== 故障排除建议 ==="
    if ! command -v docker &> /dev/null; then
        print_warning "Docker 未安装，建议："
        echo "  1. Ubuntu/Debian: sudo apt update && sudo apt install docker.io"
        echo "  2. CentOS/RHEL: sudo yum install docker"
        echo "  3. 或参考官方文档: https://docs.docker.com/engine/install/"
    elif ! docker info &> /dev/null 2>&1; then
        print_warning "Docker 已安装但未运行，建议："
        echo "  1. 启动服务: sudo systemctl start docker"
        echo "  2. 设置开机启动: sudo systemctl enable docker"
        echo "  3. 添加用户到 docker 组: sudo usermod -aG docker $USER"
        echo "  4. 重新登录或运行: newgrp docker"
    else
        print_success "Docker 环境正常"
    fi

    echo ""
    read -p "按回车键继续部署，或按 Ctrl+C 退出..." -r
}

# Linux Docker 诊断功能
diagnose_docker_linux() {
    print_step "Docker 环境诊断..."
    echo ""

    print_info "=== Docker 命令检查 ==="
    if command -v docker &> /dev/null; then
        print_success "✓ docker 命令可用"
        echo "  路径: $(which docker)"
        echo "  版本: $(docker --version 2>/dev/null || echo '获取版本失败')"
    else
        print_error "✗ docker 命令不可用"
    fi

    echo ""
    print_info "=== Docker 服务状态 ==="
    if docker info &> /dev/null 2>&1; then
        print_success "✓ Docker 服务运行中"
        echo "  容器数量: $(docker ps -q | wc -l | tr -d ' ')"
        echo "  镜像数量: $(docker images -q | wc -l | tr -d ' ')"
        echo "  运行中容器: $(docker ps --format 'table {{.Names}}\t{{.Status}}' | tail -n +2 | wc -l | tr -d ' ')"
        echo "  Docker 根目录: $(docker info --format '{{.DockerRootDir}}' 2>/dev/null || echo '未知')"
        echo "  存储驱动: $(docker info --format '{{.Driver}}' 2>/dev/null || echo '未知')"
    else
        print_warning "✗ Docker 服务未运行或无法连接"
        local docker_error=$(docker info 2>&1 | head -3)
        echo "  错误信息: $docker_error"

        # 提供详细的错误分析
        if echo "$docker_error" | grep -q "Cannot connect to the Docker daemon"; then
            print_info "  分析: Docker 守护进程未运行"
        elif echo "$docker_error" | grep -q "permission denied"; then
            print_info "  分析: 权限问题，可能需要将用户添加到 docker 组"
        elif echo "$docker_error" | grep -q "dial unix"; then
            print_info "  分析: Docker socket 连接问题"
        fi
    fi

    echo ""
    print_info "=== Docker 安装检测 ==="
    if command -v docker &> /dev/null; then
        print_success "✓ Docker 已安装"
        local docker_version=$(docker --version 2>/dev/null | cut -d' ' -f3 | cut -d',' -f1 || echo "未知")
        echo "  版本: $docker_version"
    else
        print_error "✗ Docker 未安装"
    fi

    echo ""
    print_info "=== Docker Compose 检查 ==="
    if docker compose version &> /dev/null; then
        print_success "✓ Docker Compose V2 可用"
        echo "  版本: $(docker compose version --short 2>/dev/null || echo '获取版本失败')"
    elif command -v docker-compose &> /dev/null; then
        print_success "✓ Docker Compose V1 可用"
        echo "  版本: $(docker-compose --version 2>/dev/null || echo '获取版本失败')"
    else
        print_error "✗ Docker Compose 不可用"
    fi

    echo ""
    print_info "=== 系统服务检查 ==="
    if command -v systemctl &> /dev/null; then
        local docker_status=$(systemctl is-active docker 2>/dev/null || echo "未知")
        echo "  Docker 服务状态: $docker_status"
        local docker_enabled=$(systemctl is-enabled docker 2>/dev/null || echo "未知")
        echo "  Docker 开机启动: $docker_enabled"
    fi

    echo ""
    print_info "=== 用户权限检查 ==="
    if groups | grep -q docker; then
        print_success "✓ 当前用户在 docker 组中"
    else
        print_warning "✗ 当前用户不在 docker 组中"
        echo "  建议运行: sudo usermod -aG docker $USER"
    fi

    echo ""
    print_info "=== 网络连接检查 ==="
    if ping -c 1 docker.io &> /dev/null; then
        print_success "✓ 可以连接到 Docker Hub"
    else
        print_warning "✗ 无法连接到 Docker Hub"
        echo "  这可能影响镜像下载"
    fi

    echo ""
    print_info "=== 系统资源检查 ==="
    echo "  操作系统: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '"' || echo '未知')"
    echo "  架构: $(uname -m)"
    echo "  内核版本: $(uname -r)"
    echo "  内存: $(free -h | grep Mem | awk '{print $2}') 总计, $(free -h | grep Mem | awk '{print $7}') 可用"
    echo "  CPU 核心: $(nproc)"
    echo "  磁盘空间: $(df -h / | tail -1 | awk '{print $4}') 可用"

    echo ""
    print_info "=== 故障排除建议 ==="
    if ! command -v docker &> /dev/null; then
        print_warning "Docker 未安装，建议："
        echo "  1. Ubuntu/Debian: sudo apt update && sudo apt install docker.io"
        echo "  2. CentOS/RHEL: sudo yum install docker"
        echo "  3. 或参考官方文档: https://docs.docker.com/engine/install/"
    elif ! docker info &> /dev/null 2>&1; then
        print_warning "Docker 已安装但未运行，建议："
        echo "  1. 启动服务: sudo systemctl start docker"
        echo "  2. 设置开机启动: sudo systemctl enable docker"
        echo "  3. 添加用户到 docker 组: sudo usermod -aG docker $USER"
        echo "  4. 重新登录或运行: newgrp docker"
    else
        print_success "Docker 环境正常"
    fi

    echo ""
    read -p "按回车键继续部署，或按 Ctrl+C 退出..." -r
}

# 检测操作系统
detect_os() {
    print_step "详细检测操作系统..."

    # 获取架构信息
    ARCH=$(uname -m)

    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        # 检测 macOS 版本
        MACOS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "未知")
        print_success "检测到 macOS $MACOS_VERSION ($ARCH)"

        # 检测 Apple Silicon
        if [[ "$ARCH" == "arm64" ]]; then
            IS_APPLE_SILICON=true
            print_info "检测到 Apple Silicon Mac"
        fi

        # macOS 包管理器检测
        if command -v brew &> /dev/null; then
            PKG_MANAGER="brew"
            PKG_INSTALL="brew install"
            print_info "包管理器: Homebrew"
        else
            print_warning "未检测到 Homebrew"
        fi

    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # 详细的 Linux 发行版检测
        if command -v lsb_release &> /dev/null; then
            DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
            VERSION=$(lsb_release -sr)
        elif [ -f /etc/os-release ]; then
            source /etc/os-release
            DISTRO=$(echo "$ID" | tr '[:upper:]' '[:lower:]')
            VERSION="$VERSION_ID"
        elif [ -f /etc/debian_version ]; then
            DISTRO="debian"
            VERSION=$(cat /etc/debian_version)
        elif [ -f /etc/redhat-release ]; then
            DISTRO="rhel"
            VERSION=$(grep -oE '[0-9]+\.[0-9]+' /etc/redhat-release | head -1)
        else
            DISTRO="linux"
            VERSION="未知"
        fi

        OS="linux"
        print_success "检测到 Linux: $DISTRO $VERSION ($ARCH)"

        # 设置包管理器
        case $DISTRO in
            ubuntu|debian|linuxmint|pop)
                PKG_MANAGER="apt"
                PKG_UPDATE="apt update"
                PKG_INSTALL="apt install -y"
                ;;
            centos|rhel|fedora|rocky|almalinux|ol)
                if command -v dnf &> /dev/null; then
                    PKG_MANAGER="dnf"
                    PKG_UPDATE="dnf check-update || true"
                    PKG_INSTALL="dnf install -y"
                else
                    PKG_MANAGER="yum"
                    PKG_UPDATE="yum check-update || true"
                    PKG_INSTALL="yum install -y"
                fi
                ;;
            opensuse*|sles)
                PKG_MANAGER="zypper"
                PKG_UPDATE="zypper refresh"
                PKG_INSTALL="zypper install -y"
                ;;
            arch|manjaro|endeavouros)
                PKG_MANAGER="pacman"
                PKG_UPDATE="pacman -Sy"
                PKG_INSTALL="pacman -S --noconfirm"
                ;;
            alpine)
                PKG_MANAGER="apk"
                PKG_UPDATE="apk update"
                PKG_INSTALL="apk add"
                ;;
            *)
                print_warning "未知的 Linux 发行版: $DISTRO，使用通用设置"
                PKG_MANAGER="unknown"
                ;;
        esac

        print_info "包管理器: $PKG_MANAGER"

    else
        print_error "不支持的操作系统: $OSTYPE"
        echo "支持的系统: Linux (Ubuntu/Debian/CentOS/RHEL/Fedora/openSUSE/Arch/Alpine) 和 macOS"
        exit 1
    fi

    # 检测系统服务管理器
    if command -v systemctl &> /dev/null && systemctl --version &> /dev/null; then
        SERVICE_MANAGER="systemd"
        SERVICE_START="systemctl start"
        SERVICE_ENABLE="systemctl enable"
        SERVICE_STATUS="systemctl is-active"
    elif command -v service &> /dev/null; then
        SERVICE_MANAGER="sysv"
        SERVICE_START="service"
        SERVICE_ENABLE="chkconfig --add"
        SERVICE_STATUS="service"
    elif command -v rc-service &> /dev/null; then
        SERVICE_MANAGER="openrc"
        SERVICE_START="rc-service"
        SERVICE_ENABLE="rc-update add"
        SERVICE_STATUS="rc-service"
    else
        SERVICE_MANAGER="unknown"
        print_warning "未检测到系统服务管理器"
    fi

    print_info "服务管理器: $SERVICE_MANAGER"
}

# 选择部署方式
choose_deployment_mode() {
    clear
    print_step "选择部署方式"
    print_separator
    echo ""
    echo "请选择您的部署方式："
    echo ""
    print_choice "1) Docker部署 (推荐)"
    echo "   ✅ 环境隔离，避免依赖冲突"
    echo "   ✅ 一键启动，易于管理"
    echo "   ✅ 支持快速扩展"
    echo ""
    print_choice "2) 本地部署"
    echo "   ✅ 直接运行，性能最优"
    echo "   ✅ 便于开发调试"
    echo "   ✅ 使用Python虚拟环境隔离"
    echo ""
    
    while true; do
        read -p "请输入选择 (1-2): " choice
        case $choice in
            1)
                DEPLOYMENT_MODE="docker"
                USE_DOCKER="yes"
                print_success "已选择: Docker部署"
                break
                ;;
            2)
                DEPLOYMENT_MODE="local"
                USE_DOCKER="no"
                print_success "已选择: 本地部署"
                break
                ;;
            *)
                print_warning "无效选择，请输入 1 或 2"
                ;;
        esac
    done
}

# 选择数据库类型
choose_database_type() {
    clear
    print_step "选择数据库类型"
    print_separator
    echo ""
    echo "请选择数据库类型："
    echo ""
    print_choice "1) SQLite (推荐新手)"
    echo "   ✅ 零配置，开箱即用"
    echo "   ✅ 适合小团队 (<10人)"
    echo "   ✅ 数据文件便于备份"
    echo ""
    print_choice "2) PostgreSQL (推荐生产)"
    echo "   ✅ 高性能，支持大并发"
    echo "   ✅ 适合大团队 (>10人)"
    echo "   ✅ 企业级数据库功能"
    echo ""
    
    while true; do
        read -p "请输入选择 (1-2): " choice
        case $choice in
            1)
                DATABASE_TYPE="sqlite"
                print_success "已选择: SQLite 数据库"
                break
                ;;
            2)
                DATABASE_TYPE="postgres"
                print_success "已选择: PostgreSQL 数据库"
                break
                ;;
            *)
                print_warning "无效选择，请输入 1 或 2"
                ;;
        esac
    done
}

# 检查Docker环境
check_docker() {
    print_step "智能检测 Docker 环境..."

    case $OS in
        "macos")
            check_docker_macos
            ;;
        "linux")
            check_docker_linux
            ;;
    esac

    # 检测 Docker Compose 命令
    detect_docker_compose_cmd

    print_success "Docker 环境检查完成"
}

# macOS Docker 检测
check_docker_macos() {
    local docker_methods=()
    local preferred_docker=""

    # 首先检查 Docker 命令是否可用 (最重要的检查)
    if ! command -v docker &> /dev/null; then
        print_error "Docker 命令不可用"
        print_info "请确保 Docker 已正确安装并添加到 PATH"
        echo ""
        print_info "是否需要运行 Docker 环境诊断来获取详细信息？"
        read -p "运行诊断 (y/n): " run_diagnosis
        if [[ $run_diagnosis =~ ^[Yy]$ ]]; then
            diagnose_docker_macos
        fi
        show_docker_install_options_macos
        exit 1
    fi

    print_success "Docker 命令可用"

    # 检测具体的安装方式 (用于确定启动方法)
    # 检测 Docker Desktop
    if [ -d "/Applications/Docker.app" ]; then
        docker_methods+=("Docker Desktop")
        preferred_docker="desktop"
        print_info "检测到 Docker Desktop 安装"
    fi

    # 检测 Homebrew Docker (更安全的检测方式)
    if command -v brew &> /dev/null; then
        if brew list --cask 2>/dev/null | grep -q "^docker$"; then
            docker_methods+=("Homebrew Docker")
            if [ -z "$preferred_docker" ]; then
                preferred_docker="homebrew"
            fi
            print_info "检测到 Homebrew Docker 安装"
        fi
    fi

    # 检测 Colima
    if command -v colima &> /dev/null; then
        docker_methods+=("Colima")
        if [ -z "$preferred_docker" ]; then
            preferred_docker="colima"
        fi
        print_info "检测到 Colima 安装"
    fi

    # 如果没有检测到具体安装方式，使用通用方式
    if [ ${#docker_methods[@]} -eq 0 ]; then
        docker_methods+=("Docker (未知安装方式)")
        preferred_docker="other"
        print_info "Docker 可用但未检测到具体安装方式"
    fi

    print_info "Docker 安装方式: ${docker_methods[*]}"

    # 检查 Docker 服务状态
    ensure_docker_running_macos "$preferred_docker"
}

# 显示 macOS Docker 安装选项
show_docker_install_options_macos() {
    echo ""
    print_info "macOS Docker 安装选项："
    echo ""
    echo "1) Docker Desktop (推荐新手):"
    if [[ "$IS_APPLE_SILICON" == "true" ]]; then
        echo "   https://desktop.docker.com/mac/main/arm64/Docker.dmg"
    else
        echo "   https://desktop.docker.com/mac/main/amd64/Docker.dmg"
    fi
    echo ""
    echo "2) Homebrew (推荐开发者):"
    echo "   brew install --cask docker"
    echo ""
    echo "3) Colima (轻量级):"
    echo "   brew install colima docker"
    echo "   colima start"
    echo ""
    print_error "请选择一种方式安装 Docker 后重新运行此脚本"
}

# 确保 macOS Docker 运行
ensure_docker_running_macos() {
    local method=$1

    print_step "检查 Docker 服务状态..."

    if docker info &> /dev/null; then
        print_success "Docker 服务正在运行"

        # 显示 Docker 版本信息
        local docker_version=$(docker --version 2>/dev/null || echo "未知版本")
        print_info "Docker 版本: $docker_version"
        return
    fi

    print_warning "Docker 命令可用但服务未运行，尝试启动..."

    case $method in
        "desktop")
            if [ -d "/Applications/Docker.app" ]; then
                print_info "启动 Docker Desktop..."
                open -a Docker

                # 等待 Docker 启动（最多等待 120 秒）
                local count=0
                while [ $count -lt 24 ]; do
                    if docker info &> /dev/null; then
                        print_success "Docker Desktop 启动成功"
                        return
                    fi
                    sleep 5
                    count=$((count + 1))
                    echo -n "."
                done
                echo ""
                print_error "Docker Desktop 启动超时，请手动启动"
                echo ""
                print_info "是否需要运行 Docker 环境诊断来获取详细信息？"
                read -p "运行诊断 (y/n): " run_diagnosis
                if [[ $run_diagnosis =~ ^[Yy]$ ]]; then
                    diagnose_docker_macos
                fi
                exit 1
            fi
            ;;
        "colima")
            if command -v colima &> /dev/null; then
                print_info "启动 Colima..."
                colima start
                if docker info &> /dev/null; then
                    print_success "Colima 启动成功"
                    return
                fi
            fi
            ;;
        "other")
            print_warning "检测到 Docker 命令但无法自动启动"
            print_info "请手动确保 Docker 服务正在运行"
            print_info "常见启动方式："
            echo "  • Docker Desktop: 打开 Docker Desktop 应用"
            echo "  • Colima: colima start"
            echo "  • 其他方式: 请参考相应文档"
            echo ""
            read -p "Docker 服务已启动？按回车继续..." -r
            if ! docker info &> /dev/null; then
                print_error "Docker 服务仍未运行，请启动后重试"
                echo ""
                print_info "是否需要运行 Docker 环境诊断来获取详细信息？"
                read -p "运行诊断 (y/n): " run_diagnosis
                if [[ $run_diagnosis =~ ^[Yy]$ ]]; then
                    diagnose_docker_macos
                fi
                exit 1
            fi
            print_success "Docker 服务确认运行"
            return
            ;;
    esac

    print_error "无法启动 Docker 服务，请手动启动后重新运行脚本"
    echo ""
    print_info "是否需要运行 Docker 环境诊断来获取详细信息？"
    read -p "运行诊断 (y/n): " run_diagnosis
    if [[ $run_diagnosis =~ ^[Yy]$ ]]; then
        diagnose_docker_macos
    fi
    exit 1
}

# Linux Docker 检测
check_docker_linux() {
    if ! command -v docker &> /dev/null; then
        print_warning "Docker 未安装"
        echo ""
        print_info "是否需要运行 Docker 环境诊断来获取详细信息？"
        read -p "运行诊断 (y/n): " run_diagnosis
        if [[ $run_diagnosis =~ ^[Yy]$ ]]; then
            diagnose_docker_linux
        fi
        show_docker_install_options_linux
        exit 1
    fi

    # 检查 Docker 服务状态
    if ! docker info &> /dev/null; then
        print_warning "Docker 服务未运行，尝试启动..."
        start_docker_service_linux

        # 如果启动后仍然失败，提供诊断选项
        if ! docker info &> /dev/null; then
            print_error "Docker 服务启动失败"
            echo ""
            print_info "是否需要运行 Docker 环境诊断来获取详细信息？"
            read -p "运行诊断 (y/n): " run_diagnosis
            if [[ $run_diagnosis =~ ^[Yy]$ ]]; then
                diagnose_docker_linux
            fi
            exit 1
        fi
    else
        print_success "Docker 服务正在运行"
    fi
}

# 显示 Linux Docker 安装选项
show_docker_install_options_linux() {
    echo ""
    print_info "Linux Docker 安装命令："
    echo ""

    case $PKG_MANAGER in
        "apt")
            echo "# Ubuntu/Debian:"
            echo "sudo $PKG_UPDATE"
            echo "sudo $PKG_INSTALL docker.io docker-compose-plugin"
            echo "sudo $SERVICE_START docker"
            echo "sudo $SERVICE_ENABLE docker"
            echo "sudo usermod -aG docker \$USER"
            ;;
        "dnf"|"yum")
            echo "# CentOS/RHEL/Fedora:"
            echo "sudo $PKG_INSTALL docker docker-compose"
            echo "sudo $SERVICE_START docker"
            echo "sudo $SERVICE_ENABLE docker"
            echo "sudo usermod -aG docker \$USER"
            ;;
        "zypper")
            echo "# openSUSE:"
            echo "sudo $PKG_INSTALL docker docker-compose"
            echo "sudo $SERVICE_START docker"
            echo "sudo $SERVICE_ENABLE docker"
            echo "sudo usermod -aG docker \$USER"
            ;;
        "pacman")
            echo "# Arch Linux:"
            echo "sudo $PKG_INSTALL docker docker-compose"
            echo "sudo $SERVICE_START docker"
            echo "sudo $SERVICE_ENABLE docker"
            echo "sudo usermod -aG docker \$USER"
            ;;
        "apk")
            echo "# Alpine Linux:"
            echo "sudo $PKG_INSTALL docker docker-compose"
            echo "sudo $SERVICE_START docker"
            echo "sudo $SERVICE_ENABLE docker default"
            echo "sudo addgroup \$USER docker"
            ;;
        *)
            echo "请参考 Docker 官方文档安装: https://docs.docker.com/engine/install/"
            ;;
    esac

    echo ""
    print_error "请安装 Docker 后重新运行此脚本"
}

# 启动 Linux Docker 服务
start_docker_service_linux() {
    case $SERVICE_MANAGER in
        "systemd")
            sudo systemctl start docker
            if docker info &> /dev/null; then
                print_success "Docker 服务启动成功"
            else
                print_error "Docker 服务启动失败"
                exit 1
            fi
            ;;
        "sysv")
            sudo service docker start
            sleep 3
            if docker info &> /dev/null; then
                print_success "Docker 服务启动成功"
            else
                print_error "Docker 服务启动失败"
                exit 1
            fi
            ;;
        "openrc")
            sudo rc-service docker start
            sleep 3
            if docker info &> /dev/null; then
                print_success "Docker 服务启动成功"
            else
                print_error "Docker 服务启动失败"
                exit 1
            fi
            ;;
        *)
            print_error "无法启动 Docker 服务，请手动启动"
            exit 1
            ;;
    esac
}

# 检测 Docker Compose 命令
detect_docker_compose_cmd() {
    # 检查新版本的 docker compose
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
        print_info "使用 Docker Compose V2"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
        print_info "使用 Docker Compose V1"
    else
        print_error "Docker Compose 不可用"

        case $OS in
            "macos")
                print_info "Docker Desktop 应该包含 Docker Compose"
                ;;
            "linux")
                print_info "尝试安装 Docker Compose..."
                install_docker_compose_linux
                ;;
        esac

        # 重新检测
        if docker compose version &> /dev/null; then
            DOCKER_COMPOSE_CMD="docker compose"
        elif command -v docker-compose &> /dev/null; then
            DOCKER_COMPOSE_CMD="docker-compose"
        else
            print_error "Docker Compose 安装失败"
            exit 1
        fi
    fi
}

# 安装 Linux Docker Compose
install_docker_compose_linux() {
    case $PKG_MANAGER in
        "apt")
            sudo $PKG_INSTALL docker-compose-plugin
            ;;
        "dnf"|"yum")
            sudo $PKG_INSTALL docker-compose
            ;;
        *)
            # 通用安装方法
            print_info "下载 Docker Compose 二进制文件..."
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
    esac
}

# 配置Docker环境变量
configure_docker_env() {
    print_step "配置Docker环境变量..."
    
    # 检查是否存在.env文件
    if [ -f ".env" ]; then
        print_warning "发现现有的 .env 文件"
        read -p "是否要重新配置? (y/n): " recreate
        if [[ ! $recreate =~ ^[Yy]$ ]]; then
            print_info "使用现有配置"
            return
        fi
    fi
    
    # 生成安全密钥
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-this-secret-key-in-production")
    
    # 创建.env文件
    cat > .env << EOF
# ReBugTracker Docker 环境配置
# 由部署脚本自动生成

# 数据库类型选择
DB_TYPE=$DATABASE_TYPE

EOF
    
    if [ "$DATABASE_TYPE" = "postgres" ]; then
        # PostgreSQL配置
        configure_postgres_for_docker
    else
        # SQLite配置
        cat >> .env << EOF
# SQLite 数据库配置
SQLITE_DB_PATH=/app/data/rebugtracker.db

EOF
    fi
    
    # 应用配置
    cat >> .env << EOF
# Flask 应用配置
FLASK_ENV=production
FLASK_SECRET_KEY=$SECRET_KEY
APP_PORT=5000

# 文件上传配置
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# 日志配置
LOG_LEVEL=INFO
EOF
    
    print_success "Docker环境配置完成"
}

# 配置PostgreSQL for Docker
configure_postgres_for_docker() {
    print_step "配置PostgreSQL数据库..."
    
    # 生成随机密码
    DB_PASSWORD=$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "ReBugTracker2024")
    
    cat >> .env << EOF
# PostgreSQL 数据库配置
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=db
DATABASE_PORT=$DB_PORT

# PostgreSQL Docker 配置
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD

EOF
    
    print_success "PostgreSQL配置完成"
    print_info "数据库密码: $DB_PASSWORD"
}

# 启动Docker服务
start_docker_services() {
    print_step "启动Docker服务..."

    # 选择compose文件
    if [ "$DATABASE_TYPE" = "sqlite" ]; then
        DOCKER_COMPOSE_FILE="docker-compose.sqlite.yml"
        print_info "使用SQLite模式启动"
    else
        DOCKER_COMPOSE_FILE="docker-compose.yml"
        print_info "使用PostgreSQL模式启动"
    fi

    # 检查compose文件是否存在
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "Docker Compose 文件不存在: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    # 停止现有服务
    print_info "停止现有服务..."
    $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true

    # 构建并启动服务
    print_info "构建并启动服务..."
    $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" up -d --build

    # 等待服务启动
    print_info "等待服务启动..."
    sleep 10

    # 检查服务状态
    print_info "检查服务状态..."

    # 等待更长时间让服务完全启动
    local max_attempts=12
    local attempt=0
    local services_running=false

    while [ $attempt -lt $max_attempts ]; do
        # 检查服务状态 (兼容 Docker Compose V1 和 V2)
        if $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps --format table | grep -E "(Up|running)" > /dev/null 2>&1 || \
           $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps | grep -E "(Up|running)" > /dev/null 2>&1; then
            services_running=true
            break
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 5
    done

    echo ""

    if [ "$services_running" = true ]; then
        print_success "Docker服务启动成功"

        # 显示服务状态
        print_info "服务状态："
        $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" ps
    else
        print_error "Docker服务启动失败或超时"
        print_info "查看服务日志："
        $DOCKER_COMPOSE_CMD -f "$DOCKER_COMPOSE_FILE" logs --tail=50
        exit 1
    fi
}

# 检查并安装系统依赖 (本地部署)
install_system_dependencies() {
    print_step "安装系统依赖..."

    case $OS in
        "macos")
            install_system_dependencies_macos
            ;;
        "linux")
            install_system_dependencies_linux
            ;;
    esac

    print_success "系统依赖安装完成"
}

# macOS 系统依赖安装
install_system_dependencies_macos() {
    # 检查 Homebrew
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew 未安装"
        echo ""
        echo "安装选项："
        echo "1) 自动安装 Homebrew (推荐)"
        echo "2) 手动安装后继续"
        echo ""
        read -p "请选择 (1-2): " choice

        case $choice in
            1)
                print_info "正在安装 Homebrew..."
                if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
                    # 添加 Homebrew 到 PATH (Apple Silicon)
                    if [[ "$IS_APPLE_SILICON" == "true" ]]; then
                        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
                        eval "$(/opt/homebrew/bin/brew shellenv)"
                    fi
                    print_success "Homebrew 安装成功"
                else
                    print_error "Homebrew 安装失败"
                    exit 1
                fi
                ;;
            2)
                print_info "请手动安装 Homebrew 后重新运行脚本"
                echo "安装命令: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
                ;;
            *)
                print_error "无效选择"
                exit 1
                ;;
        esac
    fi

    # 安装基础工具
    print_info "安装基础工具..."
    brew install git curl wget

    # 安装 Python (如果需要)
    if ! command -v python3 &> /dev/null || ! python_version_check "$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"; then
        print_info "安装 Python..."
        brew install python@3.11
    fi

    # 安装 PostgreSQL (如果需要)
    if [ "$DATABASE_TYPE" = "postgres" ]; then
        print_info "安装 PostgreSQL..."
        brew install postgresql@15
        brew services start postgresql@15
    fi
}

# Linux 系统依赖安装
install_system_dependencies_linux() {
    # 更新包列表
    if [ -n "$PKG_UPDATE" ]; then
        print_info "更新软件包列表..."
        sudo $PKG_UPDATE
    fi

    # 基础依赖包映射
    local build_tools=""
    local python_dev=""
    local ssl_dev=""
    local postgres_dev=""
    local postgres_server=""

    case $PKG_MANAGER in
        "apt")
            build_tools="build-essential"
            python_dev="python3-dev python3-pip python3-venv"
            ssl_dev="libssl-dev libffi-dev"
            postgres_dev="libpq-dev"
            postgres_server="postgresql postgresql-contrib postgresql-client"
            ;;
        "dnf"|"yum")
            build_tools="gcc gcc-c++ make"
            python_dev="python3-devel python3-pip"
            ssl_dev="openssl-devel libffi-devel"
            postgres_dev="postgresql-devel"
            postgres_server="postgresql-server postgresql-contrib"
            ;;
        "zypper")
            build_tools="gcc gcc-c++ make"
            python_dev="python3-devel python3-pip"
            ssl_dev="libopenssl-devel libffi-devel"
            postgres_dev="postgresql-devel"
            postgres_server="postgresql-server postgresql-contrib"
            ;;
        "pacman")
            build_tools="base-devel"
            python_dev="python python-pip"
            ssl_dev="openssl libffi"
            postgres_dev="postgresql-libs"
            postgres_server="postgresql"
            ;;
        "apk")
            build_tools="build-base"
            python_dev="python3-dev py3-pip"
            ssl_dev="openssl-dev libffi-dev"
            postgres_dev="postgresql-dev"
            postgres_server="postgresql postgresql-contrib"
            ;;
        *)
            print_error "不支持的包管理器: $PKG_MANAGER"
            exit 1
            ;;
    esac

    # 安装基础依赖
    print_info "安装基础工具..."
    sudo $PKG_INSTALL curl wget git

    print_info "安装编译工具..."
    sudo $PKG_INSTALL $build_tools

    print_info "安装 Python 开发环境..."
    sudo $PKG_INSTALL $python_dev

    print_info "安装 SSL 开发库..."
    sudo $PKG_INSTALL $ssl_dev

    # 安装 PostgreSQL (如果需要)
    if [ "$DATABASE_TYPE" = "postgres" ]; then
        print_info "安装 PostgreSQL 开发库..."
        sudo $PKG_INSTALL $postgres_dev

        print_info "安装 PostgreSQL 服务器..."
        sudo $PKG_INSTALL $postgres_server
    fi
}

# 检查并安装Python
check_install_python() {
    print_step "设置 Python 环境..."

    # 查找可用的 Python 版本
    local python_candidates=("python3.12" "python3.11" "python3.10" "python3.9" "python3.8" "python3" "python")
    PYTHON_CMD=""

    for cmd in "${python_candidates[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            if [ -n "$version" ] && python_version_check "$version"; then
                PYTHON_CMD="$cmd"
                print_success "找到合适的 Python: $cmd ($version)"
                break
            fi
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        print_warning "未找到合适的 Python 版本 (需要 3.8+)"
        install_python_smart

        # 重新检测
        for cmd in "${python_candidates[@]}"; do
            if command -v "$cmd" &> /dev/null; then
                local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
                if [ -n "$version" ] && python_version_check "$version"; then
                    PYTHON_CMD="$cmd"
                    print_success "Python 安装成功: $cmd ($version)"
                    break
                fi
            fi
        done

        if [ -z "$PYTHON_CMD" ]; then
            print_error "Python 安装失败"
            exit 1
        fi
    fi

    # 检查 pip
    check_pip

    print_success "Python 环境设置完成"
}

# Python 版本检查
python_version_check() {
    local version=$1
    local major=$(echo "$version" | cut -d. -f1)
    local minor=$(echo "$version" | cut -d. -f2)

    if [ "$major" -gt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -ge 8 ]); then
        return 0
    else
        return 1
    fi
}

# 智能安装 Python
install_python_smart() {
    print_step "安装 Python..."

    case $OS in
        "macos")
            if command -v brew &> /dev/null; then
                brew install python@3.11
                # 创建符号链接
                if [ -f "/opt/homebrew/bin/python3.11" ]; then
                    export PATH="/opt/homebrew/bin:$PATH"
                elif [ -f "/usr/local/bin/python3.11" ]; then
                    export PATH="/usr/local/bin:$PATH"
                fi
            else
                print_error "需要 Homebrew 来安装 Python"
                exit 1
            fi
            ;;
        "linux")
            case $PKG_MANAGER in
                "apt")
                    sudo $PKG_INSTALL python3.11 python3.11-venv python3.11-dev python3-pip
                    ;;
                "dnf"|"yum")
                    sudo $PKG_INSTALL python3.11 python3.11-devel python3-pip
                    ;;
                "zypper")
                    sudo $PKG_INSTALL python311 python311-devel python3-pip
                    ;;
                "pacman")
                    sudo $PKG_INSTALL python python-pip
                    ;;
                "apk")
                    sudo $PKG_INSTALL python3 py3-pip python3-dev
                    ;;
                *)
                    print_error "不支持的包管理器: $PKG_MANAGER"
                    exit 1
                    ;;
            esac
            ;;
    esac
}

# 检查 pip
check_pip() {
    local pip_cmd=""

    # 查找 pip 命令
    if command -v pip3 &> /dev/null; then
        pip_cmd="pip3"
    elif command -v pip &> /dev/null; then
        pip_cmd="pip"
    elif $PYTHON_CMD -m pip --version &> /dev/null; then
        pip_cmd="$PYTHON_CMD -m pip"
    else
        print_info "安装 pip..."
        case $OS in
            "macos")
                $PYTHON_CMD -m ensurepip --upgrade
                ;;
            "linux")
                case $PKG_MANAGER in
                    "apt")
                        sudo $PKG_INSTALL python3-pip
                        ;;
                    "dnf"|"yum")
                        sudo $PKG_INSTALL python3-pip
                        ;;
                    *)
                        $PYTHON_CMD -m ensurepip --upgrade
                        ;;
                esac
                ;;
        esac
        pip_cmd="$PYTHON_CMD -m pip"
    fi

    print_info "使用 pip: $pip_cmd"
}

# 创建Python虚拟环境
create_virtual_env() {
    print_step "创建 Python 虚拟环境..."

    if [ -d "$VENV_PATH" ]; then
        print_warning "虚拟环境已存在"
        read -p "是否重新创建? (y/n): " recreate
        if [[ $recreate =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_PATH"
        else
            print_info "使用现有虚拟环境"
            return
        fi
    fi

    # 使用检测到的 Python 命令创建虚拟环境
    $PYTHON_CMD -m venv "$VENV_PATH"

    # 激活虚拟环境
    source "$VENV_PATH/bin/activate"

    # 升级 pip
    print_info "升级 pip..."
    python -m pip install --upgrade pip

    print_success "虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    print_step "安装 Python 依赖包..."

    if [ ! -f "requirements.txt" ]; then
        print_error "未找到 requirements.txt 文件"
        exit 1
    fi

    source "$VENV_PATH/bin/activate"

    # 确保安装 python-dotenv（脚本需要）
    print_info "安装基础依赖..."
    pip install python-dotenv wheel setuptools

    print_info "安装项目依赖..."
    pip install -r requirements.txt

    print_success "Python 依赖安装完成"
}

# 配置PostgreSQL (本地部署)
setup_postgresql() {
    if [ "$DATABASE_TYPE" != "postgres" ]; then
        return
    fi

    print_step "配置 PostgreSQL 数据库..."

    case $OS in
        "macos")
            setup_postgresql_macos
            ;;
        "linux")
            setup_postgresql_linux
            ;;
    esac

    print_success "PostgreSQL 配置完成"
}

# macOS PostgreSQL 配置
setup_postgresql_macos() {
    # 检测 PostgreSQL 安装方式
    if brew services list | grep -q postgresql; then
        print_info "使用 Homebrew PostgreSQL"

        # 启动服务
        if ! brew services list | grep postgresql | grep -q "started"; then
            brew services start postgresql@15 || brew services start postgresql
        fi

        # 等待服务启动
        sleep 3

        # 创建用户数据库（如果不存在）
        createdb $(whoami) 2>/dev/null || true

        DB_USER=$(whoami)
        DB_HOST="localhost"
        DB_PORT="5432"

    elif [ -d "/Applications/Postgres.app" ]; then
        print_info "检测到 Postgres.app"
        print_warning "请确保 Postgres.app 正在运行"
        DB_USER=$(whoami)
        DB_HOST="localhost"
        DB_PORT="5432"

    else
        print_error "未检测到 PostgreSQL 安装"
        echo "请安装 PostgreSQL："
        echo "1) Homebrew: brew install postgresql@15"
        echo "2) Postgres.app: https://postgresapp.com/"
        exit 1
    fi

    configure_postgres_connection
}

# Linux PostgreSQL 配置
setup_postgresql_linux() {
    case $PKG_MANAGER in
        "apt")
            # Ubuntu/Debian
            sudo $SERVICE_START postgresql || true
            sudo $SERVICE_ENABLE postgresql || true
            ;;
        "dnf"|"yum")
            # CentOS/RHEL/Fedora
            if [ ! -d "/var/lib/pgsql/data" ] && [ ! -d "/var/lib/postgresql/data" ]; then
                if command -v postgresql-setup &> /dev/null; then
                    sudo postgresql-setup initdb
                elif command -v initdb &> /dev/null; then
                    sudo -u postgres initdb -D /var/lib/pgsql/data
                fi
            fi
            sudo $SERVICE_START postgresql || true
            sudo $SERVICE_ENABLE postgresql || true
            ;;
        "zypper")
            # openSUSE
            sudo $SERVICE_START postgresql || true
            sudo $SERVICE_ENABLE postgresql || true
            ;;
        "pacman")
            # Arch Linux
            if [ ! -d "/var/lib/postgres/data" ]; then
                sudo -u postgres initdb -D /var/lib/postgres/data
            fi
            sudo $SERVICE_START postgresql || true
            sudo $SERVICE_ENABLE postgresql || true
            ;;
        "apk")
            # Alpine Linux
            if [ ! -d "/var/lib/postgresql/data" ]; then
                sudo -u postgres initdb -D /var/lib/postgresql/data
            fi
            sudo $SERVICE_START postgresql || true
            sudo $SERVICE_ENABLE postgresql default || true
            ;;
    esac

    # 等待服务启动
    sleep 3

    configure_postgres_connection
}

# 配置PostgreSQL (本地部署)
setup_postgresql() {
    if [ "$DATABASE_TYPE" != "postgres" ]; then
        return
    fi

    print_step "配置 PostgreSQL 数据库..."

    case $OS in
        "ubuntu")
            # 启动PostgreSQL服务
            sudo systemctl start postgresql
            sudo systemctl enable postgresql

            # 检查是否需要配置数据库
            configure_postgres_local
            ;;

        "centos")
            # 初始化数据库
            if [ ! -d "/var/lib/pgsql/data" ]; then
                sudo postgresql-setup initdb
            fi
            sudo systemctl start postgresql
            sudo systemctl enable postgresql

            configure_postgres_local
            ;;

        "macos")
            # 启动PostgreSQL服务
            brew services start postgresql
            sleep 3
            createdb $(whoami) 2>/dev/null || true

            configure_postgres_local
            ;;
    esac

    print_success "PostgreSQL 配置完成"
}

# 配置PostgreSQL连接
configure_postgres_connection() {
    print_step "配置PostgreSQL数据库连接..."

    # 交互式配置数据库连接
    echo ""
    print_info "请配置PostgreSQL数据库连接信息："
    echo ""

    # 数据库主机
    read -p "数据库主机地址 [$DB_HOST]: " input_host
    DB_HOST=${input_host:-$DB_HOST}

    # 数据库端口
    read -p "数据库端口 [$DB_PORT]: " input_port
    DB_PORT=${input_port:-$DB_PORT}

    # 数据库名称
    read -p "数据库名称 [$DB_NAME]: " input_name
    DB_NAME=${input_name:-$DB_NAME}

    # 数据库用户
    read -p "数据库用户名 [$DB_USER]: " input_user
    DB_USER=${input_user:-$DB_USER}

    # 数据库密码
    echo -n "数据库密码 (留空表示无密码): "
    read -s DB_PASSWORD
    echo ""

    # 测试数据库连接
    test_postgres_connection

    # 创建数据库（如果不存在）
    create_postgres_database
}

# 测试PostgreSQL连接
test_postgres_connection() {
    print_step "测试数据库连接..."

    # 激活虚拟环境
    source "$VENV_PATH/bin/activate" 2>/dev/null || true

    # 构建连接参数
    local conn_params="host='$DB_HOST' port='$DB_PORT' dbname='postgres' user='$DB_USER'"
    if [ -n "$DB_PASSWORD" ]; then
        conn_params="$conn_params password='$DB_PASSWORD'"
    fi

    # 使用Python测试连接
    if $PYTHON_CMD -c "
import psycopg2
try:
    conn = psycopg2.connect($conn_params)
    conn.close()
    print('连接成功')
except Exception as e:
    print(f'连接失败: {e}')
    exit(1)
" 2>/dev/null; then
        print_success "数据库连接测试成功"
    else
        print_error "数据库连接失败"
        echo ""
        print_info "请检查以下配置："
        echo "• PostgreSQL服务是否运行"
        echo "• 用户名和密码是否正确"
        echo "• 主机地址和端口是否正确"
        echo "• 防火墙设置"
        echo ""

        # 提供一些调试信息
        case $OS in
            "macos")
                echo "macOS 调试命令："
                echo "• 检查服务: brew services list | grep postgresql"
                echo "• 启动服务: brew services start postgresql"
                ;;
            "linux")
                echo "Linux 调试命令："
                echo "• 检查服务: sudo $SERVICE_STATUS postgresql"
                echo "• 启动服务: sudo $SERVICE_START postgresql"
                echo "• 查看日志: sudo journalctl -u postgresql"
                ;;
        esac

        echo ""
        read -p "是否重新配置数据库连接? (y/n): " retry
        if [[ $retry =~ ^[Yy]$ ]]; then
            configure_postgres_connection
        else
            exit 1
        fi
    fi
}

# 创建PostgreSQL数据库
create_postgres_database() {
    print_step "创建应用数据库..."

    # 激活虚拟环境
    source "$VENV_PATH/bin/activate" 2>/dev/null || true

    # 构建连接参数
    local conn_params_target="host='$DB_HOST' port='$DB_PORT' dbname='$DB_NAME' user='$DB_USER'"
    local conn_params_postgres="host='$DB_HOST' port='$DB_PORT' dbname='postgres' user='$DB_USER'"

    if [ -n "$DB_PASSWORD" ]; then
        conn_params_target="$conn_params_target password='$DB_PASSWORD'"
        conn_params_postgres="$conn_params_postgres password='$DB_PASSWORD'"
    fi

    # 使用Python检查和创建数据库
    if $PYTHON_CMD -c "
import psycopg2
import sys

db_name = '$DB_NAME'

try:
    # 先尝试连接到目标数据库
    conn = psycopg2.connect($conn_params_target)
    conn.close()
    print('数据库已存在')
except psycopg2.OperationalError:
    # 数据库不存在，尝试创建
    try:
        conn = psycopg2.connect($conn_params_postgres)
        conn.autocommit = True
        cur = conn.cursor()
        # 使用参数化查询避免SQL注入
        cur.execute('CREATE DATABASE \"{}\"'.format(db_name))
        cur.close()
        conn.close()
        print('数据库创建成功')
    except Exception as e:
        print(f'数据库创建失败: {e}')
        sys.exit(1)
except Exception as e:
    print(f'数据库连接失败: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_success "数据库准备完成"
    else
        print_error "数据库操作失败"
        exit 1
    fi
}

# 创建本地配置文件
create_local_config() {
    print_step "创建应用配置..."

    # 生成安全密钥
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-this-secret-key-in-production")

    # 创建.env文件
    cat > .env << EOF
# ReBugTracker 本地部署配置
# 由部署脚本自动生成

# 数据库类型选择
DB_TYPE=$DATABASE_TYPE

EOF

    if [ "$DATABASE_TYPE" = "postgres" ]; then
        # PostgreSQL配置
        cat >> .env << EOF
# PostgreSQL 数据库配置
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=$DB_HOST
DATABASE_PORT=$DB_PORT

EOF
    else
        # SQLite配置
        cat >> .env << EOF
# SQLite 数据库配置
SQLITE_DB_PATH=rebugtracker.db

EOF
    fi

    # 应用配置
    cat >> .env << EOF
# Flask 应用配置
FLASK_ENV=production
FLASK_SECRET_KEY=$SECRET_KEY
APP_PORT=5000

# 文件上传配置
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# 日志配置
LOG_LEVEL=INFO
EOF

    # 设置文件权限
    chmod 600 .env

    print_success "配置文件创建完成"
}

# 创建必要目录
create_directories() {
    print_step "创建必要目录..."

    mkdir -p logs uploads static/uploads data
    chmod 755 logs uploads static/uploads data

    print_success "目录创建完成"
}

# 测试数据库连接
test_database() {
    print_step "测试数据库连接..."

    source "$VENV_PATH/bin/activate"

    $PYTHON_CMD -c "
import os
import sys
sys.path.append('.')

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print('警告: python-dotenv 未安装，使用系统环境变量')

# 测试数据库连接
try:
    from db_factory import get_db_connection
    conn = get_db_connection()
    conn.close()
    print('数据库连接成功')
except ImportError as e:
    print(f'导入错误: {e}')
    print('请确保项目文件完整')
    sys.exit(1)
except Exception as e:
    print(f'数据库连接失败: {e}')
    print('请检查数据库配置和服务状态')
    sys.exit(1)
"

    if [ $? -eq 0 ]; then
        print_success "数据库连接测试通过"
    else
        print_error "数据库连接测试失败"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    print_step "初始化数据库表..."

    source "$VENV_PATH/bin/activate"

    $PYTHON_CMD -c "
import sys
sys.path.append('.')

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print('警告: python-dotenv 未安装，使用系统环境变量')

# 初始化数据库
try:
    # 导入并调用初始化函数
    import rebugtracker
    if hasattr(rebugtracker, 'init_db'):
        rebugtracker.init_db()
        print('数据库初始化完成')
    else:
        # 如果没有 init_db 函数，尝试直接运行应用来初始化
        print('正在初始化数据库...')
        # 这里可能需要根据实际的应用结构调整
        print('请手动运行应用进行数据库初始化')
except ImportError as e:
    print(f'导入错误: {e}')
    print('请确保项目文件完整')
    sys.exit(1)
except Exception as e:
    print(f'数据库初始化失败: {e}')
    sys.exit(1)
"

    if [ $? -eq 0 ]; then
        print_success "数据库初始化完成"
    else
        print_error "数据库初始化失败"
        exit 1
    fi
}

# 创建启动脚本
create_start_script() {
    print_step "创建启动脚本..."

    if [ "$USE_DOCKER" = "yes" ]; then
        # Docker启动脚本
        cat > start_rebugtracker.sh << EOF
#!/bin/bash
# ReBugTracker Docker 启动脚本

cd "\$(dirname "\$0")"

echo "🚀 启动 ReBugTracker (Docker模式)..."
echo "数据库类型: $DATABASE_TYPE"
echo "访问地址: http://localhost:5000"
echo "管理员账号: admin"
echo "管理员密码: admin"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

$DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE up -d
echo "服务已在后台启动"
echo ""
echo "查看日志: $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE logs -f"
echo "停止服务: $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down"
EOF
    else
        # 本地启动脚本
        cat > start_rebugtracker.sh << EOF
#!/bin/bash
# ReBugTracker 本地启动脚本

cd "\$(dirname "\$0")"
source .venv/bin/activate

echo "🚀 启动 ReBugTracker (本地模式)..."
echo "数据库类型: $DATABASE_TYPE"
echo "访问地址: http://localhost:5000"
echo "管理员账号: admin"
echo "管理员密码: admin"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

$PYTHON_CMD rebugtracker.py
EOF
    fi

    chmod +x start_rebugtracker.sh

    print_success "启动脚本创建完成"
}

# 显示部署完成信息
show_completion_info() {
    clear
    print_success "🎉 ReBugTracker 部署完成！"
    print_separator
    echo ""
    echo "📋 部署信息："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 部署模式: $DEPLOYMENT_MODE"
    echo "🗄️ 数据库类型: $DATABASE_TYPE"
    echo "🌐 访问地址: http://localhost:5000"
    echo "👤 管理员账号: admin"
    echo "🔑 管理员密码: admin"
    echo "📁 项目目录: $(pwd)"
    echo ""

    if [ "$USE_DOCKER" = "yes" ]; then
        echo "🐳 Docker 管理命令："
        echo "   启动服务: ./start_rebugtracker.sh"
        echo "   查看日志: $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE logs -f"
        echo "   停止服务: $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE down"
        echo "   重启服务: $DOCKER_COMPOSE_CMD -f $DOCKER_COMPOSE_FILE restart"
    else
        echo "💻 本地部署命令："
        echo "   启动服务: ./start_rebugtracker.sh"
        echo "   手动启动: source .venv/bin/activate && $PYTHON_CMD rebugtracker.py"
        echo "   虚拟环境: source .venv/bin/activate"
        echo "   Python 命令: $PYTHON_CMD"
    fi

    echo ""
    echo "📚 更多信息请查看项目文档"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    read -p "是否现在启动 ReBugTracker? (y/n): " start_now
    if [[ $start_now =~ ^[Yy]$ ]]; then
        ./start_rebugtracker.sh
    fi
}

# 错误处理
handle_error() {
    print_error "部署过程中出现错误！"
    echo ""
    echo "常见问题解决方案："
    echo "1. 确保有 sudo 权限"
    echo "2. 检查网络连接"
    echo "3. 确保系统支持 (Ubuntu/CentOS/macOS)"
    if [ "$USE_DOCKER" = "yes" ]; then
        echo "4. 确保Docker服务正常运行"
        echo "5. 检查Docker Compose文件是否存在"
    else
        echo "4. 检查Python版本 (需要3.8+)"
        echo "5. 检查数据库服务状态"
    fi
    echo ""
    echo "如需帮助，请查看项目文档或联系技术支持"
    exit 1
}

# 设置错误处理
trap handle_error ERR

# 主函数
main() {
    # 检查命令行参数
    if [ "$1" = "--diagnose" ] || [ "$1" = "-d" ]; then
        print_info "运行 Docker 环境诊断..."
        detect_os
        if [ "$OS" = "macos" ]; then
            diagnose_docker_macos
        elif [ "$OS" = "linux" ]; then
            diagnose_docker_linux
        else
            print_error "不支持的操作系统"
            exit 1
        fi
        exit 0
    elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "ReBugTracker 部署脚本"
        echo ""
        echo "用法:"
        echo "  $0                 运行完整部署流程"
        echo "  $0 --diagnose     仅运行 Docker 环境诊断"
        echo "  $0 --help         显示此帮助信息"
        echo ""
        exit 0
    fi

    # 检查是否以root用户运行
    if [ "$EUID" -eq 0 ]; then
        print_error "请不要以 root 用户运行此脚本"
        echo "正确用法: ./deploy.sh"
        echo "诊断模式: ./deploy.sh --diagnose"
        exit 1
    fi

    # 执行部署流程
    welcome
    detect_os
    choose_deployment_mode
    choose_database_type

    if [ "$USE_DOCKER" = "yes" ]; then
        # Docker部署流程
        check_docker
        configure_docker_env
        create_directories
        start_docker_services
    else
        # 本地部署流程
        install_system_dependencies
        check_install_python
        create_virtual_env
        install_python_dependencies
        setup_postgresql
        create_local_config
        create_directories
        test_database
        init_database
    fi

    create_start_script
    show_completion_info
}

# 运行主函数
main "$@"
