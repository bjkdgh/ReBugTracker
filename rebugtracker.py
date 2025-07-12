# rebugtracker.py: ReBugTracker主程序
# 基于Flask的缺陷跟踪系统，支持用户注册、登录、问题提交、分配和解决等功能
# 支持PostgreSQL和SQLite两种数据库类型

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort, make_response, send_from_directory
from config import DB_TYPE, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, DATABASE_CONFIG
import psycopg2
from psycopg2.extras import DictCursor
from functools import wraps
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from db_factory import get_db_connection
from sql_adapter import adapt_sql
import traceback
from urllib.parse import quote, unquote

def safe_get(obj, key, default=None):
    """安全获取对象属性，兼容字典和sqlite3.Row对象"""
    if obj is None:
        return default
    try:
        # 尝试字典方式访问
        if hasattr(obj, 'get'):
            return obj.get(key, default)
        # 尝试属性方式访问
        elif hasattr(obj, key):
            return getattr(obj, key, default)
        # 尝试索引方式访问（sqlite3.Row支持）
        elif hasattr(obj, '__getitem__'):
            try:
                return obj[key]
            except (KeyError, IndexError):
                return default
        else:
            return default
    except:
        return default

# 数据库配置
DB_CONFIG = DATABASE_CONFIG[DB_TYPE]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 初始化Flask应用
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')

# 确保默认字符集为UTF-8
app.config.update(
    SECRET_KEY='your-secret-key-here-change-in-production',  # 添加密钥
    DEBUG=True,  # 开启调试模式以显示详细错误
    PROPAGATE_EXCEPTIONS=True,  # 传播异常
    TRAP_HTTP_EXCEPTIONS=False,
    UPLOAD_FOLDER='uploads',
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
    JSON_AS_ASCII=False,  # 确保JSON响应不使用ASCII编码
    DEFAULT_CHARSET='utf-8'  # 设置默认字符集
)

# 添加响应头中间件确保所有响应使用UTF-8
@app.after_request
def add_charset(response):
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

# 错误处理函数
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 注册时间格式化过滤器
@app.template_filter('datetimeformat')
def datetimeformat_filter(value, format='%Y-%m-%d %H:%M'):
    if not value:
        return '--'  # 空值占位符
    
    try:
        # 处理字符串类型输入（兼容多种数据库时间格式）
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M'):
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format)
                except ValueError:
                    continue
            return value  # 无法解析时返回原值
        
        # 处理datetime对象
        return value.strftime(format)
    except Exception as e:
        print(f"时间格式化错误: {str(e)} | 原始值: {value} ({type(value)})")
        return str(value)  # 异常时返回原始值的字符串形式

def get_current_user():
    """从cookie获取当前用户信息"""
    try:
        user_id = request.cookies.get('user_id')
        username = request.cookies.get('username')
        role_en = request.cookies.get('role_en')
        team = request.cookies.get('team')
        chinese_name = request.cookies.get('chinese_name')

        # 解码URL编码的cookie值
        if team:
            team = unquote(team)
        if chinese_name:
            chinese_name = unquote(chinese_name)
        
        if not all([user_id, username, role_en]):
            app.logger.debug(f"获取用户信息失败 - 缺少必要cookie: user_id={user_id}, username={username}, role_en={role_en}")
            return None
        
        # 添加调试信息
        app.logger.debug(f"当前用户cookie - user_id: {user_id}, username: {username}, role_en: {role_en}, team: {team}, chinese_name: {chinese_name}")
        
        # 角色映射
        role_mapping = {
            'gly': '管理员',
            'fzr': '负责人',
            'zncy': '组内成员',
            'ssz': '实施组'
        }

        role_en_lower = role_en.lower() if role_en else None
        role_cn = role_mapping.get(role_en_lower, role_en_lower)

        user_data = {
            'id': int(user_id),
            'username': username,
            'chinese_name': chinese_name,
            'role': role_cn,  # 中文角色
            'role_en': role_en_lower,  # 英文角色
            'team': team
        }
        app.logger.debug(f"返回用户数据: {user_data}")
        return user_data
    except Exception as e:
        app.logger.error(f"获取用户信息异常: {str(e)}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            resp = make_response(redirect('/login'))
            resp.delete_cookie('user_id')
            resp.delete_cookie('username') 
            resp.delete_cookie('role_en')
            resp.delete_cookie('team')
            resp.delete_cookie('chinese_name')
            return resp
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user or not safe_get(user, 'role'):
                app.logger.debug(f"权限检查失败 - 用户未登录或缺少角色信息")
                abort(403)

            user_role = safe_get(user, 'role_en', '').lower()
            required_role = role.lower()
            
            app.logger.debug(f"权限检查 - 用户角色: {user_role}, 要求角色: {required_role}")
            
            # 管理员拥有所有权限
            if user_role == 'gly':
                app.logger.debug("权限检查通过 - 管理员权限")
                return f(*args, **kwargs)
                
            # 允许更高权限角色访问
            if required_role == 'zncy' and user_role in ['zncy', 'fzr', 'ssz']:
                app.logger.debug(f"权限检查通过 - 用户角色 {user_role} 满足要求 {required_role}")
                return f(*args, **kwargs)
                
            if required_role == 'fzr' and user_role in ['fzr', 'ssz']:
                app.logger.debug(f"权限检查通过 - 用户角色 {user_role} 满足要求 {required_role}")
                return f(*args, **kwargs)
                
            if required_role == 'ssz' and user_role == 'ssz':
                app.logger.debug(f"权限检查通过 - 用户角色 {user_role} 匹配要求 {required_role}")
                return f(*args, **kwargs)
                
            if user_role == required_role:
                app.logger.debug(f"权限检查通过 - 用户角色 {user_role} 匹配要求 {required_role}")
                return f(*args, **kwargs)
                
            app.logger.debug(f"权限检查失败 - 用户角色 {user_role} 不满足要求 {required_role}")
            abort(403)
        return decorated_function
    return decorator

# 数据库初始化函数
def init_db():
    """初始化数据库结构
    
    功能：
    - 根据数据库类型创建users表和bugs表
    - 添加缺失的字段（如role_en, team_en, chinese_name）
    - 更新现有数据的角色英文标识
    - 创建表达式索引以实现大小写不敏感的用户名唯一约束
    - 确保存在默认管理员账户
    """
    # 获取数据库连接
    conn = get_db_connection()
    # 对于SQLite，设置自动提交模式（SQLite没有显式的事务，所以设置autocommit为True没有实际作用，但为了兼容性保留）
    if DB_TYPE == 'postgres':
        conn.autocommit = True
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    # 创建用户表（兼容SQLite和PostgreSQL）
    if DB_TYPE == 'postgres':
        # PostgreSQL建表语句
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                chinese_name TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                role_en TEXT,
                team TEXT,
                team_en TEXT
            ) WITH (ENCODING = 'UTF8')
        ''')
    else:
        # SQLite建表语句
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                chinese_name TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                role_en TEXT,
                team TEXT,
                team_en TEXT
            )
        ''')
    
    # 添加新列(如果不存在) - 兼容SQLite和PostgreSQL
    columns_to_add = ['role_en', 'team_en', 'chinese_name']
    for col in columns_to_add:
        try:
            if DB_TYPE == 'postgres':
                # 使用IF NOT EXISTS语法添加列（PostgreSQL特性）
                c.execute(f'ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} TEXT')
            else:
                # SQLite不支持ADD COLUMN IF NOT EXISTS，需要先检查列是否存在
                c.execute(f"PRAGMA table_info(users)")
                columns = [info[1] for info in c.fetchall()]
                if col not in columns:
                    c.execute(f'ALTER TABLE users ADD COLUMN {col} TEXT')
        except Exception as e:
            print(f"添加列{col}时出错: {str(e)}")
            if DB_TYPE == 'postgres':
                conn.rollback()
    
    # 更新现有数据的角色英文缩写（仅当有数据时）
    if DB_TYPE == 'postgres':
        # 使用CASE语句将中文角色转换为英文标识
        c.execute('''
            UPDATE users SET 
                role_en = CASE role 
                    WHEN '管理员' THEN 'gly' 
                    WHEN '负责人' THEN 'fzr' 
                    WHEN '组内成员' THEN 'zncy' 
                    WHEN '实施组' THEN 'ssz' 
                    ELSE role 
                END
        ''')
    else:
        # SQLite版本
        c.execute('''
            UPDATE users SET 
                role_en = CASE role 
                    WHEN '管理员' THEN 'gly' 
                    WHEN '负责人' THEN 'fzr' 
                    WHEN '组内成员' THEN 'zncy' 
                    WHEN '实施组' THEN 'ssz' 
                    ELSE role 
                END
        ''')
    
    # 添加表达式索引来实现大小写不敏感的唯一约束（仅PostgreSQL需要，SQLite默认大小写不敏感）
    if DB_TYPE == 'postgres':
        # 创建表达式索引
        c.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS lowercase_username_idx 
            ON users (LOWER(username))
        ''')
    
    # 检查并添加默认管理员账户(如果不存在)
    # 查询用户名为admin的用户
    query, params = adapt_sql('SELECT * FROM users WHERE username = %s', ('admin',))
    c.execute(query, params)
    if not c.fetchone():
        # 如果不存在则创建默认管理员账户
        hashed_password = generate_password_hash('admin')
        query, params = adapt_sql('''
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, '管理员')
        ''', ('admin', hashed_password))
        c.execute(query, params)
    
    # PostgreSQL: 确保角色类型存在
    if DB_TYPE == 'postgres':
        # 使用DO块执行条件创建类型的操作
        c.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                    CREATE TYPE user_role AS ENUM ('管理员', '负责人', '组内成员', '实施组');
                END IF;
            END $$;
        ''')
    
    # 创建bugs表（兼容SQLite和PostgreSQL）
    if DB_TYPE == 'postgres':
        c.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT '待处理',  -- 待处理/已分配/处理中/已解决/已完成
                assigned_to INTEGER,         -- 负责人ID
                created_by INTEGER,          -- 提交人ID
                project TEXT,               -- 所属项目名称
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution TEXT,            -- 处理详情
                image_path TEXT             -- 图片路径
            ) WITH (ENCODING = 'UTF8')
        ''')
    else:
        c.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT '待处理',  -- 待处理/已分配/处理中/已解决/已完成
                assigned_to INTEGER,         -- 负责人ID
                created_by INTEGER,          -- 提交人ID
                project TEXT,               -- 所属项目名称
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution TEXT,            -- 处理详情
                image_path TEXT             -- 图片路径
            )
        ''')
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
@app.route('/bug/complete/<int:bug_id>', methods=['POST'])
@login_required
@role_required('ssz')
def complete_bug(bug_id):
    """确认闭环问题"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    try:
        # 检查问题是否存在且状态为'已解决'
        query, params = adapt_sql('SELECT status FROM bugs WHERE id = %s', (bug_id,))
        c.execute(query, params)
        bug = c.fetchone()
        if not bug:
            return jsonify({'success': False, 'message': '问题不存在'}), 404
        if bug['status'] != '已解决':
            return jsonify({'success': False, 'message': '问题状态不是已解决，无法闭环'}), 400
        
        # 更新问题状态为"已完成"
        query, params = adapt_sql('''
            UPDATE bugs 
            SET status = '已完成'
            WHERE id = %s
        ''', (bug_id,))
        c.execute(query, params)
        conn.commit()
        return jsonify({'success': True, 'message': '问题已成功闭环'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

# 登录路由
@app.route('/logout')
def logout():
    """用户登出"""
    resp = make_response(redirect('/login'))
    resp.delete_cookie('user_id')
    resp.delete_cookie('username')
    resp.delete_cookie('role_en')
    resp.delete_cookie('team_en')
    return resp

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册路由"""
    if request.method == 'GET':
        return render_template('register.html')
        
    # 处理注册请求
    chinese_name = request.form.get('chinese_name')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    team = request.form.get('team')
    
    if not all([username, password, role]):
        return jsonify({'success': False, 'message': '请填写完整信息'}), 400
    
    # 角色值映射
    role_mapping = {
        'ssz': '实施组',
        'fzr': '负责人', 
        'zncy': '组内成员'
    }
    role_cn = role_mapping.get(role, role)
    role_en = role  # 保持原英文缩写
    
    # 简单处理team_en
    team_en = team if team else None
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(password)
        if DB_TYPE == 'postgres':
            query, params = adapt_sql(
                '''INSERT INTO users (chinese_name, username, password, role, role_en, team, team_en)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id''',
                (chinese_name, username, hashed_password, role_cn, role_en, team, team_en)
            )
            c.execute(query, params)
            user_id = c.fetchone()['id']
        else:
            # SQLite模式
            query, params = adapt_sql(
                '''INSERT INTO users (chinese_name, username, password, role, role_en, team, team_en)
                VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (chinese_name, username, hashed_password, role_cn, role_en, team, team_en)
            )
            c.execute(query, params)
            user_id = c.lastrowid
        conn.commit()
        return jsonify({
            'success': True,
            'redirect': '/login',
            'message': '注册成功'
        })
    except Exception as e:
        if 'UNIQUE constraint' in str(e):
            conn.rollback()
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        # 处理其他类型异常
        conn.rollback()
        return jsonify({'success': False, 'message': '注册失败: ' + str(e)}), 500
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        app.logger.debug(f"登录请求: username={username}, password={'*' * len(password) if password else None}")

        if not username or not password:
            app.logger.debug("用户名或密码为空")
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
            
        conn = None
        try:
            conn = get_db_connection()
            if DB_TYPE == 'postgres':
                c = conn.cursor(cursor_factory=DictCursor)
            else:
                c = conn.cursor()
            query, params = adapt_sql('SELECT * FROM users WHERE username = %s', (username,))
            c.execute(query, params)
            user = c.fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
                
            if check_password_hash(user['password'], password):
                # 确保role_en不为空
                if not user['role_en']:
                    return jsonify({'success': False, 'message': '用户角色信息不完整，请联系管理员'}), 403
                role_en = user['role_en']
                resp = make_response(jsonify({
                    'success': True,
                    'redirect': '/',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'role': user['role_en']
                    }
                }))
                resp.set_cookie('user_id', str(user['id']))
                resp.set_cookie('username', user['username'])
                chinese_name = safe_get(user, 'chinese_name') or user['username'] or 'Unknown'
                resp.set_cookie('chinese_name', quote(str(chinese_name)))
                resp.set_cookie('role_en', role_en)
                team_name = safe_get(user, 'team') or 'Unknown'
                resp.set_cookie('team', quote(str(team_name)))
                app.logger.info(f"用户 {user['username']} 登录成功，设置cookie: user_id={user['id']}, username={user['username']}, role_en={role_en}")
                return resp
            else:
                return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        except Exception as e:
            try:
                app.logger.error(f"登录过程中发生错误: {str(e)}")
            except:
                pass  # 即使记录日志失败也继续
            return jsonify({'success': False, 'message': '服务器内部错误'}), 500
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    try:
                        app.logger.error(f"关闭数据库连接时出错: {str(e)}")
                    except:
                        pass

    # 
    if request.method == 'GET':
        return render_template('login.html')
    
    # 
    return jsonify({'success': False, 'message': '无效的请求方法'}), 400

# 首页路由
@app.route('/')
@login_required
def index():
    
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    if safe_get(user, 'role_en') == 'zncy':
        # 组内成员直接跳转到team-issues页面
        return redirect('/team-issues')
    elif safe_get(user, 'role_en') == 'gly':
        return redirect('/admin')
    # 实施组和负责人等角色继续执行后面的代码（渲染首页）
    
    # 确保数据库连接使用UTF-8编码
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    if user['role_en'] == 'fzr':
        # 负责人看到自己团队的所有问题和待分配问题
        query = '''
            SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
                   b.created_at as local_created_at, b.resolved_at as local_resolved_at
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            WHERE (b.assigned_to IS NULL OR u2.team = %s) OR u1.team = %s
            ORDER BY b.created_at DESC
        '''
        adapted_query, adapted_params = adapt_sql(query, (user['team'], user['team']))
        c.execute(adapted_query, adapted_params)
    else:
        # 其他角色看到所有问题
        query = '''
            SELECT b.*, COALESCE(u1.chinese_name, u1.username) as creator_name, COALESCE(u2.chinese_name, u2.username) as assignee_name,
                   b.created_at as local_created_at, b.resolved_at as local_resolved_at
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            ORDER BY b.created_at DESC
        '''
        adapted_query, adapted_params = adapt_sql(query, ())
        c.execute(adapted_query, adapted_params)
    
    bugs = c.fetchall()
    
    # 格式化问题创建时间和解决时间
    formatted_bugs = []
    for bug in bugs:
        bug_dict = dict(bug)
        # 处理created_at
        if isinstance(bug_dict['created_at'], str):
            bug_dict['created_at'] = bug_dict['created_at']  # 已经是字符串则直接使用
        elif bug_dict['created_at']:
            bug_dict['created_at'] = bug_dict['created_at'].strftime('%Y-%m-%d %H:%M')
        else:
            bug_dict['created_at'] = '--'
        
        # 处理resolved_at
        if isinstance(bug_dict['resolved_at'], str):
            bug_dict['resolved_at'] = bug_dict['resolved_at']  # 已经是字符串则直接使用
        elif bug_dict['resolved_at']:
            bug_dict['resolved_at'] = bug_dict['resolved_at'].strftime('%Y-%m-%d %H:%M')
        else:
            bug_dict['resolved_at'] = '--'
            
        formatted_bugs.append(bug_dict)
    conn.close()
    return render_template('index.html', bugs=bugs, user=user)

# 组内成员问题列表
@app.route('/admin/users', methods=['GET', 'POST', 'PUT'])
@login_required
@role_required('gly')
def admin_users():
    """用户管理API"""
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    if request.method == 'GET':
        # 获取所有用户
        query, params = adapt_sql('SELECT id, username, chinese_name, role, team FROM users ORDER BY id', ())
        c.execute(query, params)
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(users)
        
    elif request.method == 'POST':
        # 添加新用户(JSON格式)
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'}), 400
            
        username = data.get('username')
        chinese_name = data.get('chinese_name')
        password = data.get('password')
        role = data.get('role')
        team = data.get('team')

        if not all([username, password, role]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400

        hashed_password = generate_password_hash(password)
        try:
            if DB_TYPE == 'postgres':
                query, params = adapt_sql('''
                    INSERT INTO users (username, chinese_name, password, role, team)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                ''', (username, chinese_name, hashed_password, role, team))
                c.execute(query, params)
                user_id = c.fetchone()['id']
            else:
                # SQLite模式
                query, params = adapt_sql('''
                    INSERT INTO users (username, chinese_name, password, role, team)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (username, chinese_name, hashed_password, role, team))
                c.execute(query, params)
                user_id = c.lastrowid
            conn.commit()
            return jsonify({'success': True, 'user_id': user_id})
        except Exception as e:
            conn.rollback()
            # 检查是否是用户名重复错误
            if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e):
                return jsonify({'success': False, 'message': '用户名已存在'}), 400
            else:
                return jsonify({'success': False, 'message': f'添加用户失败: {str(e)}'}), 500
        finally:
            conn.close()
            
    elif request.method == 'PUT':
        # 更新用户信息
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'}), 400

        user_id = data.get('id')
        username = data.get('username')
        chinese_name = data.get('chinese_name')
        password = data.get('password')
        role = data.get('role')
        team = data.get('team')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少用户ID'}), 400
            
        try:
            if password:
                hashed_password = generate_password_hash(password)
                query, params = adapt_sql('''
                    UPDATE users
                    SET username=%s, chinese_name=%s, password=%s, role=%s, team=%s
                    WHERE id=%s
                ''', (username, chinese_name, hashed_password, role, team, user_id))
                c.execute(query, params)
            else:
                query, params = adapt_sql('''
                    UPDATE users
                    SET username=%s, chinese_name=%s, role=%s, team=%s
                    WHERE id=%s
                ''', (username, chinese_name, role, team, user_id))
                c.execute(query, params)
                
            conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            conn.rollback()
            # 检查是否是用户名重复错误
            if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e):
                return jsonify({'success': False, 'message': '用户名已存在'}), 400
            else:
                return jsonify({'success': False, 'message': f'更新用户失败: {str(e)}'}), 500
        finally:
            conn.close()

@app.route('/admin/users/<int:user_id>', methods=['GET', 'PUT'])
@login_required
@role_required('gly')
def user_detail(user_id):
    """获取或更新单个用户信息"""
    if request.method == 'GET':
        conn = get_db_connection()
        if DB_TYPE == 'postgres':
            c = conn.cursor(cursor_factory=DictCursor)
        else:
            c = conn.cursor()
        query, params = adapt_sql('SELECT id, username, chinese_name, role, team FROM users WHERE id = %s', (user_id,))
        c.execute(query, params)
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
            
        return jsonify(dict(user))
    """更新用户信息"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '缺少请求数据'}), 400
        
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    team = data.get('team')
    role_en = data.get('role_en')
    chinese_name = data.get('chinese_name')
    
    # 生成团队英文编码(中文取首字母拼音大写)
    team_en = None
    if team:
        # 中文转拼音首字母映射表(大写)
        pinyin_map = {
            '啊':'A', '阿':'A', '埃':'A', '哎':'A', '唉':'A', '哀':'A', '皑':'A', '癌':'A', '蔼':'A', '矮':'A',
            '艾':'A', '碍':'A', '爱':'A', '隘':'A', '鞍':'A', '氨':'A', '安':'A', '俺':'A', '按':'A', '暗':'A',
            '吧':'B', '八':'B', '巴':'B', '拔':'B', '跋':'B', '靶':'B', '把':'B', '坝':'B', '霸':'B', '罢':'B',
            '白':'B', '百':'B', '柏':'B', '摆':'B', '败':'B', '拜':'B', '班':'B', '般':'B', '颁':'B', '板':'B',
            '擦':'C', '猜':'C', '裁':'C', '材':'C', '才':'C', '财':'C', '睬':'C', '踩':'C', '采':'C', '彩':'C',
            '菜':'C', '蔡':'C', '餐':'C', '参':'C', '蚕':'C', '残':'C', '惭':'C', '惨':'C', '灿':'C', '仓':'C',
            '大':'D', '呆':'D', '歹':'D', '傣':'D', '戴':'D', '带':'D', '殆':'D', '代':'D', '贷':'D', '袋':'D',
            '待':'D', '逮':'D', '怠':'D', '耽':'D', '担':'D', '丹':'D', '单':'D', '郸':'D', '掸':'D', '胆':'D',
            # 其他字母...
            '网络分析':'wlfx','实施组':'ssz','第三道防线':'dsdfx','新能源':'xny' 
        }
        # 只处理中文字符，生成大写拼音首字母
        team_en = ''.join([pinyin_map.get(c, '') for c in team if '\u4e00' <= c <= '\u9fa5'])
        # 如果team_en为空(无中文字符)，则使用team的前3个字符大写
        if not team_en:
            team_en = team[:3].upper()
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    try:
        if password:
            hashed_password = generate_password_hash(password)
            query, params = adapt_sql('''
                UPDATE users
                SET username=%s, password=%s, role=%s, role_en=%s, team=%s, team_en=%s, chinese_name=%s
                WHERE id=%s
            ''', (username, hashed_password, role, role_en, team, team_en, chinese_name, user_id))
            c.execute(query, params)
        else:
            query, params = adapt_sql('''
                UPDATE users
                SET username=%s, role=%s, role_en=%s, team=%s, team_en=%s, chinese_name=%s
                WHERE id=%s
            ''', (username, role, role_en, team, team_en, chinese_name, user_id))
            c.execute(query, params)
            
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        # 检查是否是用户名重复错误
        if 'UNIQUE constraint failed' in str(e) or 'duplicate key' in str(e):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        else:
            return jsonify({'success': False, 'message': f'更新用户失败: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('gly')
def delete_user(user_id):
    """删除用户"""
    # 不能删除自己
    current_user = get_current_user()
    if current_user['id'] == user_id:
        return jsonify({'success': False, 'message': '不能删除自己'}), 400
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    try:
        # 检查用户是否存在
        query, params = adapt_sql('SELECT id FROM users WHERE id = %s', (user_id,))
        c.execute(query, params)
        if not c.fetchone():
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 删除用户
        query, params = adapt_sql('DELETE FROM users WHERE id = %s', (user_id,))
        c.execute(query, params)
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@app.route('/admin/bugs', methods=['GET'])
@login_required
@role_required('gly')
def admin_bugs():
    """获取所有问题数据(API)"""
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query = '''
        SELECT b.id, b.title, b.status, b.created_at, b.resolved_at, COALESCE(u.chinese_name, u.username) as creator_name
        FROM bugs b
        JOIN users u ON b.created_by = u.id
        ORDER BY b.created_at DESC
    '''
    adapted_query, adapted_params = adapt_sql(query, ())
    c.execute(adapted_query, adapted_params)
    bugs = []
    for row in c.fetchall():
        bug = dict(row)
        # 处理created_at - 兼容SQLite字符串和PostgreSQL datetime
        if bug['created_at']:
            if isinstance(bug['created_at'], str):
                bug['created_at'] = bug['created_at']  # SQLite已经是字符串格式
            else:
                bug['created_at'] = bug['created_at'].strftime('%Y-%m-%d %H:%M')  # PostgreSQL datetime
        else:
            bug['created_at'] = '--'
        # 处理resolved_at - 兼容SQLite字符串和PostgreSQL datetime
        if bug['resolved_at']:
            if isinstance(bug['resolved_at'], str):
                bug['resolved_at'] = bug['resolved_at']  # SQLite已经是字符串格式
            else:
                bug['resolved_at'] = bug['resolved_at'].strftime('%Y-%m-%d %H:%M')  # PostgreSQL datetime
        else:
            bug['resolved_at'] = '--'
        bugs.append(bug)
    conn.close()
    return jsonify(bugs)

@app.route('/admin')
@login_required
@role_required('gly')
def admin():
    """管理员控制面板"""
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    # 获取所有用户
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query, params = adapt_sql('SELECT id, username, chinese_name, role, team FROM users ORDER BY id', ())
    c.execute(query, params)
    users = c.fetchall()

    # 获取所有问题
    query, params = adapt_sql('''
        SELECT b.id, b.title, b.status, b.created_at, b.resolved_at, COALESCE(u.chinese_name, u.username) as creator_name
        FROM bugs b
        JOIN users u ON b.created_by = u.id
        ORDER BY b.created_at DESC
    ''', ())
    c.execute(query, params)
    bugs = c.fetchall()
    
    # 格式化问题创建时间和解决时间
    formatted_bugs = []
    for bug in bugs:
        bug_dict = dict(bug)
        # 处理created_at
        if isinstance(bug_dict['created_at'], str):
            bug_dict['created_at'] = bug_dict['created_at']  # 已经是字符串则直接使用
        elif bug_dict['created_at']:
            bug_dict['created_at'] = bug_dict['created_at'].strftime('%Y-%m-%d %H:%M')
        else:
            bug_dict['created_at'] = '--'
        
        # 处理resolved_at
        if isinstance(bug_dict['resolved_at'], str):
            bug_dict['resolved_at'] = bug_dict['resolved_at']  # 已经是字符串则直接使用
        elif bug_dict['resolved_at']:
            bug_dict['resolved_at'] = bug_dict['resolved_at'].strftime('%Y-%m-%d %H:%M')
        else:
            bug_dict['resolved_at'] = '--'
            
        formatted_bugs.append(bug_dict)
    conn.close()
    
    return render_template('admin.html', users=users, bugs=formatted_bugs, user=user)

@app.route('/team-issues')
@login_required
@role_required('zncy')
def team_issues():
    """组内成员问题列表"""
    try:
        app.logger.debug("开始处理team-issues请求")
        user = get_current_user()
        app.logger.debug(f"当前用户: {user}")
        if not user:
            app.logger.debug("用户未登录，重定向到登录页面")
            return redirect('/login')

        conn = get_db_connection()
        if DB_TYPE == 'postgres':
            c = conn.cursor(cursor_factory=DictCursor)
        else:
            c = conn.cursor()
        query, params = adapt_sql('''
            SELECT b.id, b.title, b.description, b.status, b.assigned_to, b.created_by, b.project,
                   b.created_at as local_created_at,
                   b.resolved_at as local_resolved_at,
                   b.resolution, b.image_path,
                   COALESCE(u1.chinese_name, u1.username) as creator_name, COALESCE(u2.chinese_name, u2.username) as assignee_name
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            WHERE (
                (b.assigned_to = %s)
                OR
                (b.status = '待处理' AND b.assigned_to IS NULL AND u1.team = %s)
                OR
                (b.status = '已解决' AND b.assigned_to = %s)
            )
            ORDER BY b.created_at DESC
        ''', (user['id'], user['team'], user['id']))
        c.execute(query, params)
        bugs = c.fetchall()

        # 格式化问题创建时间和解决时间
        formatted_bugs = []
        for bug in bugs:
            bug_dict = dict(bug)
            # 处理local_created_at (别名为created_at)
            created_at = bug_dict.get('local_created_at')
            if isinstance(created_at, str):
                bug_dict['created_at'] = created_at  # 已经是字符串则直接使用
            elif created_at:
                bug_dict['created_at'] = created_at.strftime('%Y-%m-%d %H:%M')
            else:
                bug_dict['created_at'] = '--'

            # 处理local_resolved_at (别名为resolved_at)
            resolved_at = bug_dict.get('local_resolved_at')
            if isinstance(resolved_at, str):
                bug_dict['resolved_at'] = resolved_at  # 已经是字符串则直接使用
            elif resolved_at:
                bug_dict['resolved_at'] = resolved_at.strftime('%Y-%m-%d %H:%M')
            else:
                bug_dict['resolved_at'] = '--'

            formatted_bugs.append(bug_dict)

        conn.close()
        app.logger.debug(f"Rendering team_issues.html with user role: {user['role']} and bugs: {formatted_bugs}")
        return render_template('team_issues.html', bugs=formatted_bugs, user=user)
    except Exception as e:
        error_msg = f"team_issues页面错误: {str(e)}"
        print(error_msg)
        print(f"错误类型: {type(e)}")
        print(f"错误发生位置:")
        traceback.print_exc()
        try:
            app.logger.error(error_msg, exc_info=True)
        except:
            pass
        # 如果模板渲染失败，返回简单的HTML
        return f"""
        <html>
        <head><title>我的任务</title><meta charset="UTF-8"></head>
        <body>
            <h1>我的任务</h1>
            <p>抱歉，页面加载出现问题。</p>
            <p>错误信息: {str(e)}</p>
            <p><a href="/">返回首页</a> | <a href="/logout">退出登录</a></p>
        </body>
        </html>
        """, 500

# 提交问题页面
@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_page():
    user = get_current_user()
    if not user:
        return redirect('/login')

    if request.method == 'POST':
        # 处理问题提交
        return submit_bug_handler(user)

    # GET请求 - 显示提交页面
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    try:
        # 查询所有负责人（角色英文缩写为'fzr'）并确保显示名称唯一
        query, params = adapt_sql('''
            SELECT DISTINCT COALESCE(chinese_name, username) as display_name
            FROM users
            WHERE role_en = %s
        ''', ('fzr',))
        c.execute(query, params)
        managers = [row['display_name'] for row in c.fetchall()]
        app.logger.debug(f"获取到的负责人列表: {managers}")

        # 调试：打印实际查询到的负责人显示名称
        app.logger.debug(f"实际负责人显示名称: {managers}")

        return render_template('submit.html', managers=managers, projects=[], user=user)
    finally:
        conn.close()

def submit_bug_handler(user):
    """处理问题提交的逻辑"""
    app.logger.debug(f"收到问题提交请求，表单数据: {request.form}")

    title = request.form.get('title')
    description = request.form.get('description')
    created_by = user['id']
    app.logger.debug(f"提交用户ID: {created_by}, 标题: {title}, 描述: {description}")

    if not title or not description:
        return redirect('/submit?error=标题和描述不能为空')

    # 处理图片上传
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            upload_dir = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, mode=0o777, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            image_path = f'/uploads/{filename}'
            app.logger.debug(f"文件保存成功: {filepath}")

    # 存入数据库
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()

    try:
        manager_name = request.form.get('manager')
        if not manager_name:
            return redirect('/submit?error=请选择负责人')

        # 获取负责人ID（使用显示名查询）
        query, params = adapt_sql('SELECT id FROM users WHERE COALESCE(chinese_name, username) = %s', (manager_name,))
        c.execute(query, params)
        manager = c.fetchone()
        if not manager:
            return redirect(f'/submit?error=指定的负责人"{manager_name}"不存在')

        manager_id = manager['id'] if DB_TYPE == 'postgres' else manager[0]
        project_id = request.form.get('project', '')

        if DB_TYPE == 'postgres':
            query, params = adapt_sql('''
                INSERT INTO bugs (title, description, created_by, project, image_path, assigned_to, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, '待处理', CURRENT_TIMESTAMP)
                RETURNING id
            ''', (title, description, created_by, project_id, image_path, manager_id))
            c.execute(query, params)
            bug_id = c.fetchone()['id']
        else:
            query, params = adapt_sql('''
                INSERT INTO bugs (title, description, created_by, project, image_path, assigned_to, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, '待处理', datetime('now'))
            ''', (title, description, created_by, project_id, image_path, manager_id))
            c.execute(query, params)
            bug_id = c.lastrowid

        conn.commit()
        return redirect(f'/?message=问题提交成功')

    except Exception as e:
        conn.rollback()
        app.logger.error(f"提交问题失败: {str(e)}", exc_info=True)
        return redirect(f'/submit?error=提交失败: {str(e)}')
    finally:
        try:
            conn.close()
        except:
            pass

# 提交问题API
@app.route('/bug/submit', methods=['POST'])
@login_required
def submit_bug():
    app.logger.debug(f"收到问题提交请求，表单数据: {request.form}")
    user = get_current_user()
    if not user:
        app.logger.warning("提交问题失败: 用户未登录")
        return jsonify({'success': False, 'message': '用户未登录'}), 401
        
    title = request.form.get('title')
    description = request.form.get('description')
    created_by = user['id']
    app.logger.debug(f"提交用户ID: {created_by}, 标题: {title}, 描述: {description}")
    
    if not title or not description:
        return jsonify({'success': False, 'message': '标题和描述不能为空'}), 400
    
    # 处理图片上传
    image_path = None
    if 'image' in request.files:
        app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ... (rest of the file)

# ... (inside the file upload logic)
        file = request.files['image']
        if file and allowed_file(file.filename):
            # ... (rest of the file upload logic)
            upload_dir = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir, mode=0o777, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            image_path = f'/uploads/{filename}'
            app.logger.debug(f"文件保存成功: {filepath}")
    
    # 存入数据库
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    try:
        manager_name = request.form.get('manager')
        if not manager_name:
            return jsonify({'success': False, 'message': '请选择负责人'}), 400
        
        # 获取负责人ID（使用显示名查询）
        query, params = adapt_sql('SELECT id FROM users WHERE COALESCE(chinese_name, username) = %s', (manager_name,))
        c.execute(query, params)
        manager = c.fetchone()
        if not manager:
            return jsonify({'success': False, 'message': f'指定的负责人"{manager_name}"不存在'}), 404
        
        manager_id = manager['id']
        project_id = request.form.get('project', '')
        
        query, params = adapt_sql('''
            INSERT INTO bugs (title, description, created_by, project, image_path, assigned_to, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, '待处理', CURRENT_TIMESTAMP)
            RETURNING id
        ''', (title, description, created_by, project_id, image_path, manager_id))
        c.execute(query, params)
        
        bug_id = c.fetchone()['id']
        conn.commit()
        return jsonify({
            'success': True, 
            'bug_id': bug_id, 
            'redirect': f'/bug/{bug_id}'
        })
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        if 'connection' in error_msg.lower() or 'operational' in error_msg.lower():
            app.logger.error(f"数据库连接失败: {error_msg}")
            return jsonify({'success': False, 'message': '数据库连接失败，请检查数据库服务'}), 503
        elif 'constraint' in error_msg.lower() or 'integrity' in error_msg.lower():
            app.logger.error(f"数据完整性错误: {error_msg}")
            return jsonify({'success': False, 'message': '数据验证失败，请检查输入'}), 400
    except Exception as e:
        conn.rollback()
        app.logger.error(f"提交问题失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'系统错误: {str(e)}'}), 500
    finally:
        try:
            conn.close()
        except:
            pass

# 问题详情页
@app.route('/bug/<int:bug_id>')
@login_required
def bug_detail(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query = '''
        SELECT b.*, COALESCE(u1.chinese_name, u1.username) as creator_name, COALESCE(u2.chinese_name, u2.username) as assignee_name,
               b.created_at as local_created_at,
               b.resolved_at as local_resolved_at
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    '''
    adapted_query, adapted_params = adapt_sql(query, (bug_id,))
    c.execute(adapted_query, adapted_params)
    bug = c.fetchone()
    conn.close()
    if not bug:
        return "问题不存在", 404
    
    # 格式化时间 - 兼容SQLite字符串和PostgreSQL datetime
    bug_dict = dict(bug)
    if bug_dict['local_created_at']:
        if isinstance(bug_dict['local_created_at'], str):
            bug_dict['local_created_at'] = bug_dict['local_created_at']  # SQLite已经是字符串格式
        else:
            bug_dict['local_created_at'] = bug_dict['local_created_at'].strftime('%Y-%m-%d %H:%M')  # PostgreSQL datetime
    else:
        bug_dict['local_created_at'] = '--'
    if bug_dict['local_resolved_at']:
        if isinstance(bug_dict['local_resolved_at'], str):
            bug_dict['local_resolved_at'] = bug_dict['local_resolved_at']  # SQLite已经是字符串格式
        else:
            bug_dict['local_resolved_at'] = bug_dict['local_resolved_at'].strftime('%Y-%m-%d %H:%M')  # PostgreSQL datetime
    else:
        bug_dict['local_resolved_at'] = '--'

    message = request.args.get('message')
    # 将创建者ID传递给模板
    return render_template('bug_detail.html', bug=bug_dict, message=message, created_by=bug_dict['created_by'], user=user)

# 分配问题页面
@app.route('/bug/assign/<int:bug_id>')
@login_required
@role_required('fzr')
def assign_page(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query, params = adapt_sql('''
        SELECT b.*, COALESCE(u1.chinese_name, u1.username) as creator_name, COALESCE(u2.chinese_name, u2.username) as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    ''', (bug_id,))
    c.execute(query, params)
    bug = c.fetchone()

    # 获取当前负责人的组内成员
    query, params = adapt_sql('''
        SELECT id, COALESCE(chinese_name, username) as username FROM users
        WHERE team = %s AND (role = '组内成员' OR role = '负责人')
    ''', (user['team'],))
    c.execute(query, params)
    team_members = [{'id': row['id'], 'username': row['username']} for row in c.fetchall()]
    
    conn.close()
    if not bug:
        return "问题不存在", 404
    return render_template('assign.html', bug=bug, team_members=team_members, user=user)

# 分配问题API
@app.route('/bug/assign/<int:bug_id>', methods=['POST'])
@login_required
@role_required('fzr')
def assign_bug(bug_id):
    """指派问题给组内成员"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
    
    assigned_to = request.form.get('assigned_to')
    if not assigned_to:
        return jsonify({'success': False, 'message': '负责人不能为空'})
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    # 检查被指派人是否在同一团队
    query, params = adapt_sql('SELECT team FROM users WHERE id = %s', (assigned_to,))
    c.execute(query, params)
    assignee = c.fetchone()
    if not assignee or assignee['team'] != user['team']:
        conn.close()
        return jsonify({'success': False, 'message': '只能指派给同团队成员'})
    
    # 更新问题状态
    query, params = adapt_sql('''
        UPDATE bugs
        SET status = '已分配',
            assigned_to = %s
        WHERE id = %s
    ''', (assigned_to, bug_id))
    c.execute(query, params)
    conn.commit()
    
    # 获取被指派人用户名
    query, params = adapt_sql('SELECT username FROM users WHERE id = %s', (assigned_to,))
    c.execute(query, params)
    assignee_name = c.fetchone()['username']
    conn.close()
    
    return jsonify({
        'success': True, 
        'message': f'问题已成功指派给 {assignee_name}',
        'redirect': f'/bug/{bug_id}?message=问题已成功指派给 {assignee_name}'
    })

# 解决问题页面
@app.route('/bug/resolve/<int:bug_id>')
@login_required
@role_required('zncy')
def resolve_page(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query, params = adapt_sql('''
        SELECT b.*, COALESCE(u1.chinese_name, u1.username) as creator_name, COALESCE(u2.chinese_name, u2.username) as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    ''', (bug_id,))
    c.execute(query, params)
    bug = c.fetchone()
    conn.close()
    if not bug:
        return "问题不存在", 404
    return render_template('resolve.html', bug=bug, user=user)

# 解决问题API
@app.route('/bug/delete/<int:bug_id>', methods=['POST'])
@login_required
def delete_bug(bug_id):
    """删除问题"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    # 检查用户权限：管理员或问题创建者
    query, params = adapt_sql('SELECT created_by FROM bugs WHERE id = %s', (bug_id,))
    c.execute(query, params)
    bug = c.fetchone()
    if not bug:
        return jsonify({'success': False, 'message': '问题不存在'})
    
    if user['role_en'] != 'gly' and user['id'] != bug['created_by']:
        return jsonify({'success': False, 'message': '无权删除此问题'})
    
    # 执行删除
    query, params = adapt_sql('DELETE FROM bugs WHERE id = %s', (bug_id,))
    c.execute(query, params)
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/bug/confirm/<int:bug_id>', methods=['POST'])
@login_required
@role_required('zncy')
def confirm_receive(bug_id):
    """确认接收问题"""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    
    # 检查问题是否已分配给当前用户
    query, params = adapt_sql('SELECT assigned_to FROM bugs WHERE id = %s', (bug_id,))
    c.execute(query, params)
    bug = c.fetchone()
    if not bug:
        conn.close()
        return jsonify({'success': False, 'message': '问题不存在'})
    
    if bug['assigned_to'] != user['id']:
        conn.close()
        return jsonify({'success': False, 'message': '无权操作此问题'})
    
    # 更新问题状态为"处理中"
    query, params = adapt_sql('''
        UPDATE bugs 
        SET status = '处理中'
        WHERE id = %s
    ''', (bug_id,))
    c.execute(query, params)
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/bug/resolve/<int:bug_id>', methods=['GET'])
@login_required
@role_required('zncy')
def show_resolve_page(bug_id):
    """解决问题页面"""
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query, params = adapt_sql('''
        SELECT b.*, COALESCE(u1.chinese_name, u1.username) as creator_name, COALESCE(u2.chinese_name, u2.username) as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    ''', (bug_id,))
    c.execute(query, params)
    bug = c.fetchone()
    conn.close()
    if not bug:
        return "问题不存在", 404
    return render_template('resolve.html', bug=bug, user=user)

@app.route('/bug/resolve/<int:bug_id>', methods=['POST'])
@login_required
@role_required('zncy')
def resolve_bug(bug_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    resolution = request.form.get('resolution')
    if not resolution:
        return jsonify({'success': False, 'message': '处理详情不能为空'})
    
    conn = get_db_connection()
    if DB_TYPE == 'postgres':
        c = conn.cursor(cursor_factory=DictCursor)
    else:
        c = conn.cursor()
    query, params = adapt_sql('''
        UPDATE bugs 
        SET resolution = %s, status = '已解决', resolved_at = CURRENT_TIMESTAMP
        WHERE id = %s AND assigned_to = %s
    ''', (resolution, bug_id, user['id']))
    c.execute(query, params)
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect': f'/bug/{bug_id}'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'rbt_title.ico', mimetype='image/vnd.microsoft.icon')

# 添加上传文件访问路由
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def handle_chrome_devtools():
    return jsonify({'message': 'Not supported'}), 404



@app.route('/debug')
def debug_page():
    """调试页面"""
    try:
        user = get_current_user()
        cookies = dict(request.cookies)

        # 测试team-issues功能
        test_result = "未测试"
        try:
            if user and safe_get(user, 'role_en') == 'zncy':
                # 模拟team-issues的数据库查询
                conn = get_db_connection()
                if DB_TYPE == 'postgres':
                    c = conn.cursor(cursor_factory=DictCursor)
                else:
                    c = conn.cursor()

                query, params = adapt_sql('''
                    SELECT COUNT(*) as count
                    FROM bugs b
                    LEFT JOIN users u1 ON b.created_by = u1.id
                    WHERE (
                        (b.assigned_to = %s)
                        OR
                        (b.status = '待处理' AND b.assigned_to IS NULL AND u1.team = %s)
                        OR
                        (b.status = '已解决' AND b.assigned_to = %s)
                    )
                ''', (user['id'], user['team'], user['id']))

                c.execute(query, params)
                result = c.fetchone()
                bug_count = result[0] if result else 0
                conn.close()
                test_result = f"找到 {bug_count} 个问题"
        except Exception as e:
            test_result = f"测试失败: {str(e)}"

        return f"""
        <html>
        <head><title>调试信息</title></head>
        <body>
            <h1>调试信息</h1>
            <h2>用户信息</h2>
            <p>当前用户: {user}</p>

            <h2>Cookies</h2>
            <p>Cookies: {cookies}</p>

            <h2>数据库测试</h2>
            <p>测试结果: {test_result}</p>

            <h2>导航</h2>
            <a href="/login">登录</a> |
            <a href="/">首页</a> |
            <a href="/team-issues">team-issues</a> |
            <a href="/logout">退出</a>

            <h2>直接访问测试</h2>
            <form action="/team-issues" method="get">
                <button type="submit">直接访问team-issues</button>
            </form>
        </body>
        </html>
        """
    except Exception as e:
        import traceback
        return f"""
        <html>
        <head><title>调试错误</title></head>
        <body>
            <h1>调试页面错误</h1>
            <p>错误: {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """

def check_port_available(host, port):
    """检查端口是否可用"""
    import socket
    import sys

    try:
        # 创建socket并尝试绑定端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            # 端口被占用
            print(f"❌ 错误: 端口 {port} 已被占用!")
            print(f"请先关闭占用端口 {port} 的其他应用程序，或者:")
            print(f"1. 使用命令查看占用进程: netstat -ano | findstr :{port}")
            print(f"2. 杀掉占用进程: taskkill /F /PID <进程ID>")
            print(f"3. 然后重新运行此程序")
            sys.exit(1)
        else:
            print(f"✅ 端口 {port} 可用，正在启动应用程序...")
            return True

    except Exception as e:
        print(f"⚠️  端口检测出错: {e}")
        print(f"继续启动应用程序...")
        return True

if __name__ == '__main__':
    # 检查端口是否可用
    HOST = '127.0.0.1'
    PORT = 5000

    print("🚀 ReBugTracker 启动中...")
    check_port_available(HOST, PORT)

    try:
        print(f"📡 应用程序将在 http://{HOST}:{PORT} 启动")
        app.run(host=HOST, port=PORT, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 应用程序已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
    finally:
        # 确保所有资源被释放
        import os
        import signal
        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except:
            pass
