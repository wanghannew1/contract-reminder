"""
认证路由
POST /auth/login - 登录
POST /auth/logout - 退出
GET /auth/me - 获取当前登录用户信息
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 账号锁定配置
MAX_LOGIN_FAILS = 5
LOCKOUT_MINUTES = 15


def mask_phone(phone):
    """手机号脱敏"""
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + '****' + phone[-4:]


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录 - GET显示登录页，POST处理登录"""
    # GET请求返回登录页面
    if request.method == 'GET':
        from flask import render_template
        return render_template('login.html')

    # POST处理登录
    if request.is_json:
        data = request.get_json()
        phone = data.get('phone', '').strip() if data else ''
        password = data.get('password', '') if data else ''
    else:
        phone = request.form.get('username', '').strip()  # 表单用username字段
        password = request.form.get('password', '')

    if not phone or not password:
        return jsonify({'success': False, 'message': '手机号和密码不能为空'}), 400

    # 查找用户
    user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({'success': False, 'message': '手机号或密码错误'}), 401

    # 检查账号是否被锁定
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = max(1, (user.locked_until - datetime.utcnow()).seconds // 60 + 1)
        return jsonify({
            'success': False,
            'message': f'账号已锁定，请{remaining}分钟后再试'
        }), 403

    # 验证密码
    if not user.check_password(password):
        # 增加失败计数
        user.login_fail_count += 1
        if user.login_fail_count >= MAX_LOGIN_FAILS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            user.login_fail_count = 0
        db.session.commit()
        return jsonify({'success': False, 'message': '手机号或密码错误'}), 401

    # 登录成功，重置失败计数
    user.login_fail_count = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # 使用Flask-Login记住用户
    login_user(user, remember=True)

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'phone': mask_phone(user.phone)
        },
        'redirect': '/dashboard'
    }), 200


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """退出登录"""
    logout_user()
    return jsonify({'success': True}), 200


@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前登录用户信息"""
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'phone': mask_phone(current_user.phone),
        'has_unionid': bool(current_user.unionid)
    }), 200
