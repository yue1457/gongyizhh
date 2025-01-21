from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 请更改为一个安全的密钥

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录后再访问此页面'

# 初始化定时任务
scheduler = BackgroundScheduler()
scheduler.start()

# 确保数据文件存在
def ensure_files_exist():
    if not os.path.exists('users.json'):
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists('posts.json'):
        with open('posts.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists('clicks.json'):
        with open('clicks.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists('daily_stats.json'):
        with open('daily_stats.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)

# 加载点击记录
def load_clicks():
    ensure_files_exist()
    with open('clicks.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存点击记录
def save_clicks(clicks):
    with open('clicks.json', 'w', encoding='utf-8') as f:
        json.dump(clicks, f, ensure_ascii=False, indent=2)

# 加载日活数据
def load_daily_stats():
    ensure_files_exist()
    with open('daily_stats.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存日活数据
def save_daily_stats(stats):
    with open('daily_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

# 检查账号是否被限制
def check_account_limit(post_id):
    clicks = load_clicks()
    post_clicks = clicks.get(str(post_id), {'count': 0, 'users': [], 'first_click': None, 'locked_until': None})
    
    # 如果有锁定时间且未过期，返回剩余时间
    if post_clicks.get('locked_until'):
        locked_until = datetime.strptime(post_clicks['locked_until'], '%Y-%m-%d %H:%M:%S')
        if locked_until > datetime.now():
            remaining = locked_until - datetime.now()
            return False, f"该账号已被限制访问，{int(remaining.total_seconds() / 60)}分钟后可重新查看"
    
    return True, None

# 记录点击并检查是否需要限制
def record_click(post_id, user_id):
    clicks = load_clicks()
    now = datetime.now()
    post_id = str(post_id)
    
    if post_id not in clicks:
        clicks[post_id] = {
            'count': 0,
            'users': [],
            'first_click': None,
            'locked_until': None
        }
    
    post_clicks = clicks[post_id]
    
    # 如果是新一轮的点击（之前的锁定已过期）
    if post_clicks.get('locked_until'):
        locked_until = datetime.strptime(post_clicks['locked_until'], '%Y-%m-%d %H:%M:%S')
        if locked_until <= now:
            post_clicks = clicks[post_id] = {
                'count': 0,
                'users': [],
                'first_click': None,
                'locked_until': None
            }
    
    # 如果是第一次点击，记录时间
    if not post_clicks['users']:
        post_clicks['first_click'] = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 如果用户未点击过
    if user_id not in post_clicks['users']:
        post_clicks['users'].append(user_id)
        post_clicks['count'] += 1
        
        # 如果达到10次点击，设置2小时限制
        if post_clicks['count'] >= 10:
            first_click = datetime.strptime(post_clicks['first_click'], '%Y-%m-%d %H:%M:%S')
            post_clicks['locked_until'] = (first_click + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    
    save_clicks(clicks)
    return post_clicks['count'] >= 10

# 记录用户访问
def record_user_visit(user_id):
    stats = load_daily_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today not in stats:
        stats[today] = {
            'total_visits': 0,
            'unique_users': []
        }
    
    stats[today]['total_visits'] += 1
    if user_id not in stats[today]['unique_users']:
        stats[today]['unique_users'].append(user_id)
    
    save_daily_stats(stats)

# 获取今日数据
def get_today_stats():
    stats = load_daily_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if today not in stats:
        return {
            'total_visits': 0,
            'unique_users': 0
        }
    
    return {
        'total_visits': stats[today]['total_visits'],
        'unique_users': len(stats[today]['unique_users'])
    }

# 获取最近7天的数据
def get_weekly_stats():
    stats = load_daily_stats()
    today = datetime.now()
    weekly_stats = []
    
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        if date in stats:
            weekly_stats.append({
                'date': date,
                'total_visits': stats[date]['total_visits'],
                'unique_users': len(stats[date]['unique_users'])
            })
        else:
            weekly_stats.append({
                'date': date,
                'total_visits': 0,
                'unique_users': 0
            })
    
    return weekly_stats

def format_remaining_time(expire_date_str):
    """格式化剩余时间"""
    expire_date = datetime.strptime(expire_date_str, '%Y-%m-%dT%H:%M')
    now = datetime.now()
    diff = expire_date - now
    
    if diff.total_seconds() <= 0:
        return "已过期"
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if days > 0:
        return f"剩余{days}天{hours}小时"
    else:
        return f"剩余{hours}小时{minutes}分钟"

def format_expired_time(expire_date_str):
    """格式化过期时长"""
    expire_date = datetime.strptime(expire_date_str, '%Y-%m-%dT%H:%M')
    now = datetime.now()
    diff = now - expire_date
    
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if days > 0:
        return f"已过期{days}天{hours}小时"
    else:
        return f"已过期{hours}小时{minutes}分钟"

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.password_hash = user_data['password']
        self.is_admin = user_data.get('is_admin', False)
        self.last_login = user_data.get('last_login', None)

# 加载用户数据
def load_users():
    ensure_files_exist()
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存用户数据
def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# 加载帖子数据
def load_posts():
    ensure_files_exist()
    with open('posts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存帖子数据
def save_posts(posts):
    with open('posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

# 检查并删除过期账号
def check_expired_posts():
    posts = load_posts()
    current_time = datetime.now()
    expired_posts = []
    valid_posts = []
    
    for post in posts:
        # 如果是旧数据没有过期时间，设置为24小时后过期
        if 'expire_date' not in post:
            created_at = datetime.strptime(post['created_at'], '%Y-%m-%d %H:%M:%S')
            expire_date = created_at + timedelta(days=1)
            post['expire_date'] = expire_date.strftime('%Y-%m-%dT%H:%M')
        
        expire_date = datetime.strptime(post['expire_date'], '%Y-%m-%dT%H:%M')
        if expire_date <= current_time:
            expired_posts.append(post)
        else:
            valid_posts.append(post)
    
    if expired_posts:
        save_posts(valid_posts)
        print(f"已删除 {len(expired_posts)} 个过期账号")
    elif len(valid_posts) != len(posts):
        # 如果有更新过期时间的旧数据，保存更新后的数据
        save_posts(valid_posts)

# 每小时检查一次过期账号
scheduler.add_job(check_expired_posts, 'interval', hours=1)

# 更新用户最后登录时间
def update_user_last_login(user_id):
    users = load_users()
    for user in users:
        if user['id'] == user_id:
            user['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    save_users(users)

# 检查并删除不活跃用户
def check_inactive_users():
    users = load_users()
    posts = load_posts()
    current_time = datetime.now()
    active_users = []
    deleted_users = []
    
    for user in users:
        # 跳过管理员
        if user.get('is_admin', False):
            active_users.append(user)
            continue
            
        # 如果没有最后登录时间记录，使用创建时间
        last_login = user.get('last_login')
        if not last_login and 'created_at' in user:
            last_login = user['created_at']
        
        # 如果既没有最后登录时间也没有创建时间，设置为当前时间
        if not last_login:
            last_login = current_time.strftime('%Y-%m-%d %H:%M:%S')
            user['last_login'] = last_login
        
        last_login_date = datetime.strptime(last_login, '%Y-%m-%d %H:%M:%S')
        days_inactive = (current_time - last_login_date).days
        
        if days_inactive <= 30:
            active_users.append(user)
        else:
            deleted_users.append(user['id'])
    
    # 如果有用户被删除
    if deleted_users:
        # 保存更新后的用户列表
        save_users(active_users)
        
        # 删除这些用户发布的账号
        active_posts = [post for post in posts if post['created_by'] not in deleted_users]
        save_posts(active_posts)
        
        print(f"已删除 {len(deleted_users)} 个不活跃用户")

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = next((user for user in users if str(user['id']) == str(user_id)), None)
    if user_data:
        return User(user_data)
    return None

@app.route('/')
def index():
    # 记录访问量
    if current_user.is_authenticated:
        record_user_visit(current_user.id)
    
    posts = load_posts()
    # 只显示已通过审核的账号，管理员可以看到所有账号
    if not current_user.is_authenticated or not current_user.is_admin:
        posts = [post for post in posts if post.get('status') == 'approved']
    
    # 删除过期的账号
    current_time = datetime.now()
    active_posts = []
    for post in posts:
        if 'expire_date' in post:
            expire_date = datetime.strptime(post['expire_date'], '%Y-%m-%dT%H:%M')
            if expire_date > current_time:
                # 添加剩余时间
                post['remaining_time'] = format_remaining_time(post['expire_date'])
                active_posts.append(post)
    
    # 获取统计数据（仅管理员可见）
    stats = None
    if current_user.is_authenticated and current_user.is_admin:
        stats = {
            'today': get_today_stats(),
            'weekly': get_weekly_stats()
        }
    
    return render_template('index.html', posts=active_posts, stats=stats)

@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        account_name = request.form.get('account_name')
        password = request.form.get('password')
        platform = request.form.get('platform', '一同看')
        expire_date = request.form.get('expire_date')
        content = request.form.get('content', '')
        
        # 验证账号是否存在
        posts = load_posts()
        if any(post['account_name'] == account_name for post in posts):
            flash('账号已存在，请使用其他账号', 'error')
            return redirect(url_for('new_post'))
            
        # 验证密码长度
        if len(password) < 4:
            flash('密码长度不能少于4位', 'error')
            return redirect(url_for('new_post'))
            
        # 如果没有设置到期时间，默认24小时后
        if not expire_date:
            expire_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
            
        post = {
            'id': len(posts) + 1,
            'account_name': account_name,
            'password': password,
            'platform': platform,
            'expire_date': expire_date,
            'content': content,
            'created_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'created_by': current_user.id,
            'status': 'pending' if not current_user.is_admin else 'approved',  # 管理员发布直接通过，普通用户需要审核
            'author': current_user.username
        }
        
        posts.append(post)
        save_posts(posts)
        
        if current_user.is_admin:
            flash('账号分享成功！', 'success')
        else:
            flash('账号已提交，等待管理员审核！', 'info')
        return redirect(url_for('index'))
        
    return render_template('post_form.html')

@app.route('/pending_posts')
@login_required
def pending_posts():
    if not current_user.is_admin:
        flash('只有管理员可以访问此页面', 'error')
        return redirect(url_for('index'))
        
    posts = load_posts()
    pending_posts = [post for post in posts if post.get('status') == 'pending']
    return render_template('pending_posts.html', posts=pending_posts)

@app.route('/approve_post/<int:post_id>', methods=['POST'])
@login_required
def approve_post(post_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '只有管理员可以审核账号'}), 403
        
    # 获取新的到期时间
    new_expire_date = request.json.get('expire_date')
    if not new_expire_date:
        return jsonify({'success': False, 'message': '请设置到期时间'}), 400
        
    try:
        # 验证日期格式
        datetime.strptime(new_expire_date, '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'success': False, 'message': '日期格式不正确'}), 400
        
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            post['status'] = 'approved'
            post['expire_date'] = new_expire_date
            post['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post['approved_by'] = current_user.id
            save_posts(posts)
            return jsonify({'success': True})
            
    return jsonify({'success': False, 'message': '账号不存在'}), 404

@app.route('/reject_post/<int:post_id>', methods=['POST'])
@login_required
def reject_post(post_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '只有管理员可以审核账号'}), 403
        
    posts = load_posts()
    posts = [post for post in posts if post['id'] != post_id]
    save_posts(posts)
    return jsonify({'success': True})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        
        if any(user['username'] == username for user in users):
            flash('用户名已存在', 'error')
            return redirect(url_for('register'))
        
        new_user = {
            'id': len(users) + 1,
            'username': username,
            'password': generate_password_hash(password),
            'is_admin': len(users) == 0,  # 第一个注册的用户自动成为管理员
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        users.append(new_user)
        save_users(users)
        
        user = User(new_user)
        login_user(user)
        
        flash('注册成功！', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        user_data = next((user for user in users if user['username'] == username), None)
        
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            
            # 更新最后登录时间
            update_user_last_login(user.id)
            
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        
        flash('用户名或密码错误', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'success')
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        flash('只有管理员才能删除帖子！', 'error')
        return redirect(url_for('index'))
        
    posts = load_posts()
    posts = [post for post in posts if post['id'] != post_id]
    save_posts(posts)
    flash('删除成功！', 'success')
    return redirect(url_for('index'))

@app.route('/users')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('只有管理员才能访问此页面！', 'error')
        return redirect(url_for('index'))
    users = load_users()
    return render_template('users.html', users=users)

@app.route('/expired_posts')
@login_required
def expired_posts():
    if not current_user.is_admin:
        flash('只有管理员才能访问此页面！', 'error')
        return redirect(url_for('index'))
        
    posts = load_posts()
    current_time = datetime.now()
    expired = []
    valid = []
    
    for post in posts:
        # 如果是旧数据没有过期时间，设置为24小时后过期
        if 'expire_date' not in post:
            created_at = datetime.strptime(post['created_at'], '%Y-%m-%d %H:%M:%S')
            expire_date = created_at + timedelta(days=1)
            post['expire_date'] = expire_date.strftime('%Y-%m-%dT%H:%M')
            
        expire_date = datetime.strptime(post['expire_date'], '%Y-%m-%dT%H:%M')
        if expire_date <= current_time:
            post['expired_time'] = format_expired_time(post['expire_date'])
            expired.append(post)
        else:
            post['remaining_time'] = format_remaining_time(post['expire_date'])
            valid.append(post)
    
    # 保存更新后的数据
    if any('expire_date' not in p for p in posts):
        save_posts(expired + valid)
            
    return render_template('expired_posts.html', expired_posts=expired, valid_posts=valid)

@app.route('/check_account/<int:post_id>')
@login_required
def check_account(post_id):
    if current_user.is_admin:
        return jsonify({'success': True})
        
    # 检查是否被限制
    allowed, message = check_account_limit(post_id)
    if not allowed:
        return jsonify({'success': False, 'message': message})
    
    # 记录点击
    is_limited = record_click(post_id, current_user.id)
    if is_limited:
        return jsonify({'success': False, 'message': '该账号已达到访问限制，2小时后可重新查看'})
    
    return jsonify({'success': True})

@app.route('/check_account_exists/<account_name>')
def check_account_exists(account_name):
    posts = load_posts()
    exists = any(post['account_name'] == account_name for post in posts)
    return jsonify({'exists': exists})

@app.route('/my_posts')
@login_required
def my_posts():
    posts = load_posts()
    # 获取用户发布的所有账号，包括待审核和已审核的
    my_posts = [post for post in posts if post['created_by'] == current_user.id]
    
    # 按状态分类
    pending_posts = []
    approved_posts = []
    rejected_posts = []
    
    for post in my_posts:
        if post['status'] == 'pending':
            pending_posts.append(post)
        elif post['status'] == 'approved':
            # 添加剩余时间信息
            post['remaining_time'] = format_remaining_time(post['expire_date'])
            approved_posts.append(post)
        elif post['status'] == 'rejected':
            rejected_posts.append(post)
    
    return render_template('my_posts.html', 
                         pending_posts=pending_posts,
                         approved_posts=approved_posts,
                         rejected_posts=rejected_posts)

if __name__ == '__main__':
    ensure_files_exist()
    # 启动时检查一次过期账号
    check_expired_posts()
    # 每天检查一次不活跃用户
    scheduler.add_job(check_inactive_users, 'interval', days=1)
    app.run(debug=True)
