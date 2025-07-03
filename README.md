# ReBugTracker

一个基于Flask和PostgreSQL的Bug跟踪系统

## 部署方式
- 直接部署: 使用Gunicorn运行
- Docker单容器部署
- Docker Compose多服务部署
(详见DEPLOYMENT.md)

## 功能特性
- 用户角色管理(管理员/负责人/组内成员)
- Bug提交与分配
- Bug状态跟踪(待处理/已分配/处理中/已解决)
- 项目关联管理
- 图片附件支持

## 技术栈
- Python 3.x
- Flask
- PostgreSQL
- psycopg2
- Bootstrap 5

## 快速开始
1. 安装依赖: `pip install -r requirements.txt`
2. 配置数据库连接: 修改config.py
3. 初始化数据库: `python rebugtracker.py` (首次运行会自动创建表结构)
4. 启动开发服务器: `python rebugtracker.py`
5. 生产部署: 参考DEPLOYMENT.md

默认管理员账号: admin/admin

## 项目结构
```
ReBugTracker/
├── rebugtracker.py       # 主应用文件
├── config.py             # 配置文件
├── requirements.txt      # 依赖列表
├── static/               # 静态资源
├── templates/            # 模板文件
└── uploads/              # 上传文件存储
```
