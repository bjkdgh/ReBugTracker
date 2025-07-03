from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, abort, make_response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import DB_CONFIG

app = Flask(__name__, static_folder='uploads', static_url_path='/uploads', template_folder='templates')

# 确保默认字符集为UTF-8
app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True,
    TRAP_HTTP_EXCEPTIONS=True,
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
        
        if not all([user_id, username, role_en]):
            app.logger.debug(f"获取用户信息失败 - 缺少必要cookie: user_id={user_id}, username={username}, role_en={role_en}")
            return None
        
        # 添加调试信息
        app.logger.debug(f"当前用户cookie - user_id: {user_id}, username: {username}, role_en: {role_en}, team: {team}")
        
        return {
            'id': int(user_id),
            'username': username,
            'role': role_en.lower() if role_en else None,
            'team': team.lower() if team else None
        }
    except Exception as e:
        app.logger.error(f"获取用户信息异常: {str(e)}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user or not user.get('role'):
                app.logger.debug(f"权限检查失败 - 用户未登录或缺少角色信息")
                abort(403)
            
            user_role = user['role'].lower()
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

# 初始化数据库
def init_db():
    # 确保数据库连接使用UTF-8编码
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    c = conn.cursor(cursor_factory=DictCursor)
    
    # 创建表(如果不存在)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            role_en TEXT,
            team TEXT,
            team_en TEXT
        ) WITH (ENCODING = 'UTF8')
    ''')
    
    # 添加新列(如果不存在)
    try:
        c.execute('ALTER TABLE users ADD COLUMN role_en TEXT')
        c.execute('ALTER TABLE users ADD COLUMN team_en TEXT')
    except psycopg2.Error:
        conn.rollback()
    
    # 更新现有数据的角色英文缩写
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
    
    # 添加表达式索引来实现大小写不敏感的唯一约束
    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS lowercase_username_idx 
        ON users (LOWER(username))
    ''')
    
    # 检查并添加默认管理员账户(如果不存在)
    c.execute('SELECT * FROM users WHERE username = %s', ('admin',))
    if not c.fetchone():
        hashed_password = generate_password_hash('admin')
        c.execute('''
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, '管理员')
        ''', ('admin', hashed_password))
    
    # 确保角色类型存在
    c.execute('''
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                CREATE TYPE user_role AS ENUM ('管理员', '负责人', '组内成员', '实施组');
            END IF;
        END $$;
    ''')
    

    c.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT '待处理',  -- 待处理/已分配/处理中/已解决/已确认
                assigned_to INTEGER,         -- 负责人ID
                created_by INTEGER,          -- 提交人ID
                project TEXT,               -- 所属项目名称
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                resolution TEXT,            -- 处理详情
                image_path TEXT             -- 图片路径
            ) WITH (ENCODING = 'UTF8')
    ''')
    conn.commit()
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
    # 确保数据库连接使用UTF-8编码
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    if request.method == 'GET':
        return render_template('register.html')
        
    # 处理注册请求
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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    try:
        hashed_password = generate_password_hash(password)
        c.execute('''
            INSERT INTO users (username, password, role, role_en, team, team_en)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (username, hashed_password, role_cn, role_en, team, team_en))
        user_id = c.fetchone()['id']
        conn.commit()
        return jsonify({
            'success': True,
            'redirect': '/login',
            'message': '注册成功'
        })
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor(cursor_factory=DictCursor)
        c.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = c.fetchone()
        conn.close()
        
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
            resp.set_cookie('role_en', role_en)
            if user.get('team'):
                resp.set_cookie('team', user['team'])
            app.logger.info(f"用户 {user['username']} 登录成功，设置cookie: user_id={user['id']}, username={user['username']}, role_en={role_en}")
            return resp
    return render_template('login.html')

# 首页路由
@app.route('/')
@login_required
def index():
    
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    if user['role'] == 'zncy':
        return redirect('/team-issues')
    elif user['role'] == 'gly':
        return redirect('/admin')
    # 实施组和负责人等角色继续执行后面的代码（渲染首页）
    
    # 确保数据库连接使用UTF-8编码
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    c = conn.cursor(cursor_factory=DictCursor)
    
    if user['role'] == '负责人':
        # 负责人看到自己团队的所有问题和待分配问题
        c.execute('''
            SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
                   b.created_at as local_created_at
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            WHERE (b.assigned_to IS NULL OR u2.team = %s) OR u1.team = %s
            ORDER BY b.created_at DESC
        ''', (user['team'], user['team']))
    else:
        # 其他角色看到所有问题
        c.execute('''
            SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
                   b.created_at as local_created_at
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            ORDER BY b.created_at DESC
        ''')
    
    bugs = c.fetchall()
    conn.close()
    return render_template('index.html', bugs=bugs, user=user)

# 组内成员问题列表
@app.route('/admin/users', methods=['GET', 'POST', 'PUT'])
@login_required
@role_required('gly')
def admin_users():
    """用户管理API"""
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    if request.method == 'GET':
        # 获取所有用户
        c.execute('SELECT id, username, role, team FROM users ORDER BY id')
        users = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(users)
        
    elif request.method == 'POST':
        # 添加新用户(JSON格式)
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'}), 400
            
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        team = data.get('team')
        
        if not all([username, password, role]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
            
        hashed_password = generate_password_hash(password)
        try:
            c.execute('''
                INSERT INTO users (username, password, role, team)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (username, hashed_password, role, team))
            user_id = c.fetchone()['id']
            conn.commit()
            return jsonify({'success': True, 'user_id': user_id})
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        finally:
            conn.close()
            
    elif request.method == 'PUT':
        # 更新用户信息
        user_id = request.form.get('id')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        team = request.form.get('team')
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少用户ID'}), 400
            
        try:
            if password:
                hashed_password = generate_password_hash(password)
                c.execute('''
                    UPDATE users 
                    SET username=%s, password=%s, role=%s, team=%s
                    WHERE id=%s
                ''', (username, hashed_password, role, team, user_id))
            else:
                c.execute('''
                    UPDATE users 
                    SET username=%s, role=%s, team=%s
                    WHERE id=%s
                ''', (username, role, team, user_id))
                
            conn.commit()
            return jsonify({'success': True})
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        finally:
            conn.close()

@app.route('/admin/users/<int:user_id>', methods=['GET', 'PUT'])
@login_required
@role_required('gly')
def user_detail(user_id):
    """获取或更新单个用户信息"""
    if request.method == 'GET':
        conn = psycopg2.connect(**DB_CONFIG)
        c = conn.cursor(cursor_factory=DictCursor)
        c.execute('SELECT id, username, role, team FROM users WHERE id = %s', (user_id,))
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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    try:
        if password:
            hashed_password = generate_password_hash(password)
            c.execute('''
                UPDATE users 
                SET username=%s, password=%s, role=%s, role_en=%s, team=%s, team_en=%s
                WHERE id=%s
            ''', (username, hashed_password, role, role_en, team, team_en, user_id))
        else:
            c.execute('''
                UPDATE users 
                SET username=%s, role=%s, role_en=%s, team=%s, team_en=%s
                WHERE id=%s
            ''', (username, role, role_en, team, team_en, user_id))
            
        conn.commit()
        return jsonify({'success': True})
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    try:
        # 检查用户是否存在
        c.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        if not c.fetchone():
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 删除用户
        c.execute('DELETE FROM users WHERE id = %s', (user_id,))
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
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('''
        SELECT b.id, b.title, b.status, b.created_at, u.username as creator_name
        FROM bugs b
        JOIN users u ON b.created_by = u.id
        ORDER BY b.created_at DESC
    ''')
    bugs = [dict(row) for row in c.fetchall()]
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
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('SELECT id, username, role, team FROM users ORDER BY id')
    users = c.fetchall()
    
    # 获取所有问题
    c.execute('''
        SELECT b.id, b.title, b.status, b.created_at, u.username as creator_name
        FROM bugs b
        JOIN users u ON b.created_by = u.id
        ORDER BY b.created_at DESC
    ''')
    bugs = c.fetchall()
    conn.close()
    
    return render_template('admin.html', users=users, bugs=bugs, user=user)

@app.route('/team-issues')
@login_required
@role_required('zncy')
def team_issues():
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('''
        SELECT b.id, b.title, b.description, b.status, b.assigned_to, b.created_by, b.project, 
               b.created_at as local_created_at, 
               b.resolved_at as local_resolved_at,
               b.resolution, b.image_path,
               u1.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE (
            (b.assigned_to = %s) 
            OR 
            (b.status = '待处理' AND b.assigned_to IS NULL AND u1.team = %s)
        )
        ORDER BY b.created_at DESC
    ''', (user['id'], user['team']))
    bugs = c.fetchall()
    conn.close()
    return render_template('team_issues.html', bugs=bugs, user=user)

# 提交问题页面
@app.route('/submit')
@login_required
def submit_page():
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    c = conn.cursor(cursor_factory=DictCursor)
    try:
        c.execute('SELECT username FROM users WHERE role = %s', ('负责人',))
        managers = [row['username'] for row in c.fetchall()]
        
        return render_template('submit.html', managers=managers, projects=[], user=user)
    finally:
        conn.close()

# 提交问题API
@app.route('/bugsubmit', methods=['POST'])
@login_required
def submit_bug():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    title = request.form.get('title')
    description = request.form.get('description')
    created_by = user['id']
    
    # 处理图片上传
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f'/uploads/{filename}'
    
    # 存入数据库
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    c = conn.cursor(cursor_factory=DictCursor)
    project_id = request.form.get('project')
    manager_name = request.form.get('manager')
    
    # 获取负责人ID（大小写不敏感查询）
    c.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(%s)', (manager_name,))
    manager = c.fetchone()
    if not manager:
        return jsonify({'success': False, 'message': '指定的负责人不存在'})
    manager_id = manager['id']
    
    c.execute('''
        INSERT INTO bugs (title, description, created_by, project, image_path, assigned_to, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, '待处理', CURRENT_TIMESTAMP)
        RETURNING id
    ''', (title, description, created_by, project_id, image_path, manager_id))
    bug_id = c.fetchone()['id']
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'bug_id': bug_id, 'redirect': f'/bug/{bug_id}'})

# 问题详情页
@app.route('/bug/<int:bug_id>')
@login_required
def bug_detail(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('''
        SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
               b.created_at as local_created_at,
               b.resolved_at as local_resolved_at
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    ''', (bug_id,))
    bug = c.fetchone()
    conn.close()
    if not bug:
        return "问题不存在", 404
    
    message = request.args.get('message')
    # 将创建者ID传递给模板
    return render_template('bug_detail.html', bug=bug, message=message, created_by=bug['created_by'], user=user)

# 分配问题页面
@app.route('/bug/assign/<int:bug_id>')
@login_required
@role_required('fzr')
def assign_page(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    db_config = DB_CONFIG.copy()
    db_config['client_encoding'] = 'utf8'
    conn = psycopg2.connect(**db_config)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('''
        SELECT b.*, u1.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    ''', (bug_id,))
    bug = c.fetchone()
    
    # 获取当前负责人的组内成员
    c.execute('''
        SELECT id, username FROM users 
        WHERE team = %s AND (role = '组内成员' OR role = '负责人')
    ''', (user['team'],))
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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    # 检查被指派人是否在同一团队
    c.execute('SELECT team FROM users WHERE id = %s', (assigned_to,))
    assignee = c.fetchone()
    if not assignee or assignee['team'] != user['team']:
        conn.close()
        return jsonify({'success': False, 'message': '只能指派给同团队成员'})
    
    # 更新问题状态
    c.execute('''
        UPDATE bugs 
        SET status = '已分配', 
            assigned_to = %s
        WHERE id = %s
    ''', (assigned_to, bug_id))
    conn.commit()
    
    # 获取被指派人用户名
    c.execute('SELECT username FROM users WHERE id = %s', (assigned_to,))
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
        
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('''
        SELECT b.*, u1.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = %s
    ''', (bug_id,))
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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    # 检查用户权限：管理员或问题创建者
    c.execute('SELECT created_by FROM bugs WHERE id = %s', (bug_id,))
    bug = c.fetchone()
    if not bug:
        return jsonify({'success': False, 'message': '问题不存在'})
    
    if user['role'] != 'gly' and user['id'] != bug['created_by']:
        return jsonify({'success': False, 'message': '无权删除此问题'})
    
    # 执行删除
    c.execute('DELETE FROM bugs WHERE id = %s', (bug_id,))
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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    
    # 检查问题是否已分配给当前用户
    c.execute('SELECT assigned_to FROM bugs WHERE id = %s', (bug_id,))
    bug = c.fetchone()
    if not bug:
        conn.close()
        return jsonify({'success': False, 'message': '问题不存在'})
    
    if bug['assigned_to'] != user['id']:
        conn.close()
        return jsonify({'success': False, 'message': '无权操作此问题'})
    
    # 更新问题状态为"处理中"
    c.execute('''
        UPDATE bugs 
        SET status = '处理中'
        WHERE id = %s
    ''', (bug_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

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
    
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('''
        UPDATE bugs 
        SET resolution = %s, status = '已解决', resolved_at = CURRENT_TIMESTAMP
        WHERE id = %s AND assigned_to = %s
    ''', (resolution, bug_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect': f'/bug/{bug_id}'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'RBT.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def handle_chrome_devtools():
    return jsonify({'message': 'Not supported'}), 404

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=True)
    finally:
        # 确保所有资源被释放
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
else:
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
