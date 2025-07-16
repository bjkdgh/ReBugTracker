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
PROJECT_DIR=$(pwd)
VENV_PATH="$PROJECT_DIR/.venv"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="rebugtracker"
DB_USER="postgres"
DB_PASSWORD=""

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
    print_info "脚本将引导您完成所有配置，无需手动修改配置文件"
    echo ""
    read -p "按回车键开始部署..." -r
}

# 检测操作系统
detect_os() {
    print_step "检测操作系统..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="ubuntu"
            print_success "检测到 Ubuntu/Debian 系统"
        elif [ -f /etc/redhat-release ]; then
            OS="centos"
            print_success "检测到 CentOS/RHEL 系统"
        else
            OS="linux"
            print_success "检测到 Linux 系统"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "检测到 macOS 系统"
    else
        print_error "不支持的操作系统: $OSTYPE"
        echo "请在 Linux 或 macOS 系统上运行此脚本"
        exit 1
    fi
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
    print_step "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker 未安装"
        echo ""
        echo "请先安装Docker："
        case $OS in
            "ubuntu")
                echo "sudo apt update"
                echo "sudo apt install -y docker.io docker-compose"
                echo "sudo systemctl start docker"
                echo "sudo systemctl enable docker"
                echo "sudo usermod -aG docker \$USER"
                ;;
            "centos")
                echo "sudo yum install -y docker docker-compose"
                echo "sudo systemctl start docker"
                echo "sudo systemctl enable docker"
                echo "sudo usermod -aG docker \$USER"
                ;;
            "macos")
                echo "请访问 https://docs.docker.com/desktop/mac/install/ 下载安装Docker Desktop"
                ;;
        esac
        echo ""
        print_error "请安装Docker后重新运行此脚本"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose 未安装"
        case $OS in
            "ubuntu"|"centos")
                print_info "正在安装 Docker Compose..."
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
                ;;
            "macos")
                print_error "请安装Docker Desktop，它包含Docker Compose"
                exit 1
                ;;
        esac
    fi
    
    # 检查Docker服务状态
    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行，请启动Docker服务"
        case $OS in
            "ubuntu"|"centos")
                echo "sudo systemctl start docker"
                ;;
            "macos")
                echo "请启动Docker Desktop应用"
                ;;
        esac
        exit 1
    fi
    
    print_success "Docker 环境检查完成"
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
    docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true

    # 构建并启动服务
    print_info "构建并启动服务..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build

    # 等待服务启动
    print_info "等待服务启动..."
    sleep 10

    # 检查服务状态
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "Docker服务启动成功"
    else
        print_error "Docker服务启动失败"
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs
        exit 1
    fi
}

# 检查并安装系统依赖 (本地部署)
install_system_dependencies() {
    print_step "检查系统依赖..."

    case $OS in
        "ubuntu")
            print_info "更新软件包列表..."
            sudo apt update

            print_info "安装系统依赖..."
            sudo apt install -y \
                curl \
                wget \
                git \
                build-essential \
                libssl-dev \
                libffi-dev \
                python3-dev \
                python3-pip \
                python3-venv

            if [ "$DATABASE_TYPE" = "postgres" ]; then
                sudo apt install -y \
                    postgresql \
                    postgresql-contrib \
                    postgresql-client \
                    libpq-dev
            fi
            ;;

        "centos")
            print_info "安装系统依赖..."
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \
                curl \
                wget \
                git \
                openssl-devel \
                libffi-devel \
                python3 \
                python3-pip \
                python3-devel

            if [ "$DATABASE_TYPE" = "postgres" ]; then
                sudo yum install -y \
                    postgresql-server \
                    postgresql-contrib \
                    postgresql-devel
            fi
            ;;

        "macos")
            print_info "检查 Homebrew..."
            if ! command -v brew &> /dev/null; then
                print_warning "Homebrew 未安装，正在安装..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi

            print_info "安装系统依赖..."
            brew install python3 git

            if [ "$DATABASE_TYPE" = "postgres" ]; then
                brew install postgresql
            fi
            ;;
    esac

    print_success "系统依赖安装完成"
}

# 检查并安装Python
check_install_python() {
    print_step "检查 Python 环境..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 已安装: $PYTHON_VERSION"

        # 检查版本是否满足要求
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python 版本满足要求 (3.8+)"
        else
            print_error "Python 版本过低，需要 3.8+，当前版本: $PYTHON_VERSION"
            install_python
        fi
    else
        print_warning "Python 未安装"
        install_python
    fi

    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        print_info "安装 pip..."
        case $OS in
            "ubuntu") sudo apt install -y python3-pip ;;
            "centos") sudo yum install -y python3-pip ;;
            "macos") python3 -m ensurepip --upgrade ;;
        esac
    fi

    print_success "Python 环境检查完成"
}

# 安装Python
install_python() {
    print_step "安装 Python..."

    case $OS in
        "ubuntu")
            sudo apt update
            sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip
            ;;
        "centos")
            sudo yum install -y python39 python39-devel python39-pip
            ;;
        "macos")
            brew install python@3.9
            ;;
    esac

    print_success "Python 安装完成"
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

    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"

    print_info "升级 pip..."
    pip install --upgrade pip

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

# 配置PostgreSQL本地连接
configure_postgres_local() {
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
    echo -n "数据库密码: "
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

    # 使用Python测试连接
    if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='$DB_HOST',
        port='$DB_PORT',
        dbname='postgres',
        user='$DB_USER',
        password='$DB_PASSWORD'
    )
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
        echo ""
        read -p "是否重新配置数据库连接? (y/n): " retry
        if [[ $retry =~ ^[Yy]$ ]]; then
            configure_postgres_local
        else
            exit 1
        fi
    fi
}

# 创建PostgreSQL数据库
create_postgres_database() {
    print_step "创建应用数据库..."

    # 检查数据库是否存在
    if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='$DB_HOST',
        port='$DB_PORT',
        dbname='$DB_NAME',
        user='$DB_USER',
        password='$DB_PASSWORD'
    )
    conn.close()
    print('数据库已存在')
except psycopg2.OperationalError:
    # 数据库不存在，尝试创建
    try:
        conn = psycopg2.connect(
            host='$DB_HOST',
            port='$DB_PORT',
            dbname='postgres',
            user='$DB_USER',
            password='$DB_PASSWORD'
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute('CREATE DATABASE $DB_NAME')
        cur.close()
        conn.close()
        print('数据库创建成功')
    except Exception as e:
        print(f'数据库创建失败: {e}')
        exit(1)
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

    python3 -c "
import os
import sys
sys.path.append('.')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 测试数据库连接
try:
    from db_factory import get_db_connection
    conn = get_db_connection()
    conn.close()
    print('数据库连接成功')
except Exception as e:
    print(f'数据库连接失败: {e}')
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

    python3 -c "
import sys
sys.path.append('.')

from rebugtracker import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('数据库表创建完成')
"

    print_success "数据库初始化完成"
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

docker-compose -f $DOCKER_COMPOSE_FILE up -d
echo "服务已在后台启动"
echo ""
echo "查看日志: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "停止服务: docker-compose -f $DOCKER_COMPOSE_FILE down"
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

python3 rebugtracker.py
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
        echo "   查看日志: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
        echo "   停止服务: docker-compose -f $DOCKER_COMPOSE_FILE down"
        echo "   重启服务: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    else
        echo "💻 本地部署命令："
        echo "   启动服务: ./start_rebugtracker.sh"
        echo "   手动启动: source .venv/bin/activate && python3 rebugtracker.py"
        echo "   虚拟环境: source .venv/bin/activate"
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
    # 检查是否以root用户运行
    if [ "$EUID" -eq 0 ]; then
        print_error "请不要以 root 用户运行此脚本"
        echo "正确用法: ./deploy_enhanced.sh"
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
