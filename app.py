from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, abort, make_response
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='uploads', static_url_path='/uploads', template_folder='templates')

app.config.update(
    DEBUG=True,
    PROPAGATE_EXCEPTIONS=True,
    TRAP_HTTP_EXCEPTIONS=True,
    UPLOAD_FOLDER='uploads',
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'}
)
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
    user_id = request.cookies.get('user_id')
    username = request.cookies.get('username')
    role = request.cookies.get('role')
    team = request.cookies.get('team')
    
    if not all([user_id, username, role]):
        return None
    
    return {
        'id': int(user_id),
        'username': username,
        'role': role,
        'team': team
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user or 'role' not in user:
                abort(403)
            
            # 管理员拥有所有权限
            if user['role'] == '管理员':
                return f(*args, **kwargs)
                
            # 允许更高权限角色访问
            if role == '组内成员' and user['role'] in ['组内成员', '负责人']:
                return f(*args, **kwargs)
            if role == '负责人' and user['role'] == '负责人':
                return f(*args, **kwargs)
            if user['role'] == role:
                return f(*args, **kwargs)
                
            abort(403)
        return decorated_function
    return decorator

# 初始化数据库
def init_db():
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    
    # 创建表(如果不存在)
    c.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY,
            en_name TEXT NOT NULL,
            cn_name TEXT NOT NULL UNIQUE
        )''')
    
    c.execute('''
        INSERT OR IGNORE INTO roles (id, en_name, cn_name) VALUES
        (1, 'product_member', '组内成员'),
        (2, 'manager', '负责人'),
        (3, 'admin', '管理员'),
        (4, 'requester', '实施组')
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            team TEXT
        )
    ''')
    
    # 检查并添加默认管理员账户(如果不存在)
    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        hashed_password = generate_password_hash('admin')
        c.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, '管理员')
        ''', ('admin', hashed_password))
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            )
    ''')
    conn.commit()
    conn.close()

# 首页路由
@app.route('/')
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    if user['role'] == '组内成员':
        return redirect('/team-issues')
    elif user['role'] == '管理员':
        return redirect('/admin')
    # 实施组和负责人等角色继续执行后面的代码（渲染首页）
    
    conn = sqlite3.connect('bugtracker.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if user['role'] == '负责人':
        # 负责人看到自己团队的所有问题和待分配问题
        c.execute('''
            SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
                   datetime(b.created_at, 'localtime') as local_created_at
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            WHERE (b.assigned_to IS NULL OR u2.team = ?) OR u1.team = ?
            ORDER BY b.created_at DESC
        ''', (user['team'], user['team']))
    else:
        # 其他角色看到所有问题
        c.execute('''
            SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
                   datetime(b.created_at, 'localtime') as local_created_at
            FROM bugs b
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.assigned_to = u2.id
            ORDER BY b.created_at DESC
        ''')
    
    bugs = c.fetchall()
    conn.close()
    return render_template('index.html', bugs=bugs, user=user)

# 组内成员问题列表
@app.route('/team-issues')
@login_required
@role_required('组内成员')
def team_issues():
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = sqlite3.connect('bugtracker.db')
    conn.row_factory = sqlite3.Row  # 启用行工厂转换为字典式对象
    c = conn.cursor()
    c.execute('''
        SELECT b.id, b.title, b.description, b.status, b.assigned_to, b.created_by, b.project, 
               datetime(b.created_at, 'localtime') as local_created_at, 
               datetime(b.resolved_at, 'localtime') as local_resolved_at,
               b.resolution, b.image_path,
               u1.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE (
            (b.assigned_to = ?) 
            OR 
            (b.status = '待处理' AND b.assigned_to IS NULL AND u1.team = ?)
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
        
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    try:
        c.execute('SELECT username FROM users WHERE role = "负责人"')
        managers = [row[0] for row in c.fetchall()]
        
        c.execute('SELECT id, name FROM projects ORDER BY name')
        projects = c.fetchall()
        
        return render_template('submit.html', managers=managers, projects=projects, user=user)
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
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    project_id = request.form.get('project')
    manager_name = request.form.get('manager')
    
    # 获取负责人ID
    c.execute('SELECT id FROM users WHERE username = ?', (manager_name,))
    manager_id = c.fetchone()[0]
    
    c.execute('''
        INSERT INTO bugs (title, description, created_by, project, image_path, assigned_to, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, '待处理', datetime('now', 'localtime'))
    ''', (title, description, created_by, project_id, image_path, manager_id))
    bug_id = c.lastrowid
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
        
    conn = sqlite3.connect('bugtracker.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT b.*, u1.username as creator_name, u2.username as assignee_name,
               datetime(b.created_at, 'localtime') as local_created_at,
               datetime(b.resolved_at, 'localtime') as local_resolved_at
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = ?
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
@role_required('负责人')
def assign_page(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = sqlite3.connect('bugtracker.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT b.*, u1.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = ?
    ''', (bug_id,))
    bug = c.fetchone()
    
    # 获取当前负责人的组内成员
    c.execute('''
        SELECT id, username FROM users 
        WHERE team = ? AND (role = '组内成员' OR role = '负责人')
    ''', (user['team'],))
    team_members = [{'id': row[0], 'username': row[1]} for row in c.fetchall()]
    
    conn.close()
    if not bug:
        return "问题不存在", 404
    return render_template('assign.html', bug=bug, team_members=team_members, user=user)

# 分配问题API
@app.route('/bug/assign/<int:bug_id>', methods=['POST'])
@login_required
@role_required('负责人')
def assign_bug(bug_id):
    assigned_to = request.form.get('assigned_to')
    if not assigned_to:
        return jsonify({'success': False, 'message': '负责人不能为空'})
    
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    c.execute('''
        UPDATE bugs SET status = '已分配', assigned_to = ?
        WHERE id = ?
    ''', (assigned_to, bug_id))
    conn.commit()
    
    # 获取被指派人的用户名
    c.execute('SELECT username FROM users WHERE id = ?', (assigned_to,))
    assignee_name = c.fetchone()[0]
    conn.close()
    
    return jsonify({
        'success': True, 
        'message': f'问题已成功指派给 {assignee_name}',
        'redirect': f'/bug/{bug_id}?message=问题已成功指派给 {assignee_name}'
    })

# 解决问题页面
@app.route('/bug/resolve/<int:bug_id>')
@login_required
@role_required('组内成员')
def resolve_page(bug_id):
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    conn = sqlite3.connect('bugtracker.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT b.*, u1.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u1 ON b.created_by = u1.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        WHERE b.id = ?
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
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    
    # 检查问题是否存在及创建者
    c.execute('SELECT created_by FROM bugs WHERE id = ?', (bug_id,))
    bug = c.fetchone()
    if not bug:
        return jsonify({'success': False, 'message': '问题不存在'})
    
    # 只有管理员或问题创建者可以删除
    if user['role'] != '管理员' and user['id'] != bug[0]:
        abort(403)
    
    c.execute('DELETE FROM bugs WHERE id = ?', (bug_id,))
    conn.commit()
    conn.close()
    return jsonify({
        'success': True, 
        'message': '问题已成功删除',
        'redirect': '/?message=问题已成功删除'
    })

@app.route('/bug/confirm/<int:bug_id>', methods=['POST'])
@login_required
@role_required('组内成员')
def confirm_bug(bug_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    c.execute('''
        UPDATE bugs 
        SET status = '处理中'
        WHERE id = ? AND assigned_to = ?
    ''', (bug_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect': f'/bug/{bug_id}'})

# 保存处理详情API
@app.route('/bug/save_resolution/<int:bug_id>', methods=['POST'])
@login_required
@role_required('组内成员')
def save_resolution(bug_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    resolution = request.form.get('resolution')
    if not resolution:
        return jsonify({'success': False, 'message': '处理详情不能为空'})
    
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    # 只保存处理详情，不改变状态
    c.execute('''
        UPDATE bugs 
        SET resolution = ?
        WHERE id = ? AND assigned_to = ?
    ''', (resolution, bug_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect': f'/bug/{bug_id}'})

# 保存处理详情并标记为已完成API
@app.route('/bug/complete_and_save/<int:bug_id>', methods=['POST'])
@login_required
@role_required('组内成员')
def complete_and_save(bug_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    resolution = request.form.get('resolution')
    if not resolution:
        return jsonify({'success': False, 'message': '处理详情不能为空'})
    
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    # 保存处理详情，同时标记为已完成，并设置解决时间
    c.execute('''
        UPDATE bugs 
        SET resolution = ?, status = '已完成', resolved_at = datetime('now', 'localtime')
        WHERE id = ? AND assigned_to = ?
    ''', (resolution, bug_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect': f'/bug/{bug_id}'})

# 标记问题为已完成API
@app.route('/bug/complete/<int:bug_id>', methods=['POST'])
@login_required
@role_required('组内成员')
def complete_bug(bug_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': '用户未登录'})
        
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    # 更新状态为已完成，并设置解决时间
    c.execute('''
        UPDATE bugs 
        SET status = '已完成', resolved_at = datetime('now', 'localtime')
        WHERE id = ? AND assigned_to = ?
    ''', (bug_id, user['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'redirect': f'/bug/{bug_id}'})

# 获取图片
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 处理网站图标请求
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'faq.ico')

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        next_url = request.form.get('next', '/')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
            
        try:
            conn = sqlite3.connect('bugtracker.db')
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('''
                SELECT id, username, password, role, team
                FROM users
                WHERE username = ?
            ''', (username,))
            user = c.fetchone()
            conn.close()
            
            if not user:
                return jsonify({'success': False, 'message': '用户名或密码错误'})
                
            if not check_password_hash(user['password'], password):
                return jsonify({'success': False, 'message': '用户名或密码错误'})
                
            # 创建响应并设置cookie
            # 根据角色设置重定向路径
            if user['role'] == '管理员':
                redirect_url = '/admin'
            elif user['role'] == '组内成员':
                redirect_url = '/team-issues'
            elif user['role'] == '实施组':
                redirect_url = '/'
            else:
                redirect_url = '/'

            resp = make_response(jsonify({
                'success': True,
                'redirect': redirect_url
            }))
            
            # 设置cookie - 确保能被前端JavaScript读取
            cookie_opts = {
                'httponly': False,
                'samesite': 'Lax',
                'path': '/',
                'max_age': 3600 * 24  # 1天有效期
            }
            
            resp.set_cookie('user_id', str(user['id']), **cookie_opts)
            resp.set_cookie('username', user['username'], **cookie_opts)
            resp.set_cookie('role', user['role'], **cookie_opts)
            if user['team']:
                resp.set_cookie('team', user['team'], **cookie_opts)
                
            return resp
                
        except Exception as e:
            return jsonify({'success': False, 'message': '服务器内部错误'})
    
    return render_template('login.html', next=request.args.get('next', '/'))

# 用户登出
@app.route('/logout')
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('user_id', '', expires=0)
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('role', '', expires=0)
    resp.set_cookie('team', '', expires=0)
    return resp

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        team = request.form.get('team')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
            
        hashed_password = generate_password_hash(password)
        
        conn = sqlite3.connect('bugtracker.db')
        conn.row_factory = sqlite3.Row  # 设置行工厂为Row对象
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (username, password, role, team)
                VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, '组内成员', team))
            conn.commit()
            return jsonify({'success': True, 'redirect': '/login'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': '用户名已存在'})
        finally:
            conn.close()
    return render_template('register.html')
# 管理员用户管理页面
@app.route('/admin')
@login_required
@role_required('管理员')
def admin_page():
    user = get_current_user()
    if not user or user['role'] != '管理员':
        abort(403)
    return render_template('admin.html', user=user)

# 获取用户列表API
@app.route('/admin/bugs')
@login_required
@role_required('管理员')
def get_bugs():
    conn = sqlite3.connect('bugtracker.db')
    conn.row_factory = sqlite3.Row  # 设置行工厂为Row对象
    c = conn.cursor()
    c.execute('''
        SELECT b.id, b.title, b.status, b.project, b.created_at, u.username as creator_name, u2.username as assignee_name
        FROM bugs b
        LEFT JOIN users u ON b.created_by = u.id
        LEFT JOIN users u2 ON b.assigned_to = u2.id
        ORDER BY b.created_at DESC
    ''')
    bugs = [{
        'id': row[0],
        'title': row[1],
        'status': row[2],
        'created_at': row[3],
        'creator_name': row[4]
    } for row in c.fetchall()]
    conn.close()
    return jsonify(bugs)

@app.route('/admin/users')
@login_required
@role_required('管理员')
def get_users():
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    c.execute('SELECT id, username, role, team FROM users')
    users = [{'id': row[0], 'username': row[1], 'role': row[2], 'team': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(users)

# 添加用户API
@app.route('/admin/users', methods=['POST'])
@login_required
@role_required('管理员')
def add_user():
    username = request.form.get('username')
    password = request.form.get('password') or 'admin'
    role = request.form.get('role')
    team = request.form.get('team')
    
    if not username or not role:
        return jsonify({'success': False, 'message': '用户名和角色不能为空'})
        
    hashed_password = generate_password_hash(password)
    
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (username, password, role, team)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, role, team))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '用户名已存在'})
    finally:
        conn.close()

# 更新用户API
@app.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('管理员')
def update_user(user_id):
    role = request.form.get('role')
    team = request.form.get('team')
    password = request.form.get('password')
    
    conn = sqlite3.connect('bugtracker.db')
    c = conn.cursor()
    try:
        if password:
            hashed_password = generate_password_hash(password)
            c.execute('''
                UPDATE users SET role = ?, team = ?, password = ?
                WHERE id = ?
            ''', (role, team, hashed_password, user_id))
        else:
            c.execute('''
                UPDATE users SET role = ?, team = ?
                WHERE id = ?
            ''', (role, team, user_id))
            
        conn.commit()
        if c.rowcount == 0:
            return jsonify({'success': False, 'message': '用户不存在'})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新用户失败: {str(e)}'})
    finally:
        conn.close()

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
