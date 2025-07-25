# ----------------------------------------------------------------
# 第一阶段：构建环境 (Builder)
# 使用此阶段来安装编译依赖和 Python 包，以保持最终镜像的纯净。
# 支持多架构构建 (amd64/arm64)
# ----------------------------------------------------------------
FROM python:3.9-slim as builder

# 设置 WORKDIR，后续所有操作都在此目录下
WORKDIR /app

# 配置国内镜像源以加速下载
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list || true

# 安装构建依赖 (包括 PostgreSQL 客户端库编译依赖)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# [最佳实践] 创建并配置虚拟环境 (venv)
# 这样做比 --user 安装更标准，依赖隔离更清晰
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# [优化] 仅复制依赖文件，以充分利用 Docker 缓存
COPY requirements.txt .

# 配置 pip 使用国内镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Python 依赖到虚拟环境中
# --no-cache-dir 减少镜像体积
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn


# ----------------------------------------------------------------
# 第二阶段：生产环境 (Production)
# 这是最终运行应用的镜像，只包含必要的文件。
# 支持多架构运行 (amd64/arm64)
# ----------------------------------------------------------------
FROM python:3.9-slim

# [安全] 创建一个非 root 的系统用户和用户组来运行应用
RUN addgroup --system app && adduser --system --ingroup app app

# 设置工作目录
WORKDIR /app

# 配置国内镜像源以加速下载
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list || true

# 安装运行时依赖：curl用于健康检查，tzdata用于时区设置，libpq5用于PostgreSQL连接
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tzdata \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 设置容器时区（亚洲/上海）
ENV TZ=Asia/Shanghai
RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# 从构建阶段复制已经安装好依赖的虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 创建必要的目录
RUN mkdir -p /app/uploads /app/logs /app/data_exports /app/data && \
    chown -R app:app /app/uploads /app/logs /app/data_exports /app/data

# 复制应用代码到工作目录
# --chown=app:app 将文件所有者设置为我们创建的非 root 用户
COPY --chown=app:app . .

# 将虚拟环境的 bin 目录添加到 PATH，这样可以直接运行 gunicorn 等命令
ENV PATH="/opt/venv/bin:$PATH"

# 设置非敏感的环境变量
ENV FLASK_APP=rebugtracker.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
# [安全] 数据库连接字符串等敏感信息，不应硬编码在 Dockerfile 中。
# 请在容器运行时通过环境变量 (-e) 注入。

# [安全] 切换到非 root 用户
USER app

# 暴露应用端口
EXPOSE 5000

# 创建启动脚本
COPY --chown=app:app docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 定义容器启动时要执行的命令
# 使用启动脚本来处理不同的数据库模式
CMD ["/app/docker-entrypoint.sh"]

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:5000/ || exit 1
