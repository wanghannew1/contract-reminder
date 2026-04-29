"""
管理员路由
GET /api/admin/config - 获取配置
PUT /api/admin/config - 更新配置
POST /api/admin/config/test - 测试钉钉连接
GET /api/admin/users - 用户列表
POST /api/admin/users - 创建用户
PUT /api/admin/users/{id} - 更新用户
PATCH /api/admin/users/{id}/status - 启用/停用
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from app.models.user import User
from app.models.system_config import SystemConfig
from app.services.dingtalk import DingTalkService
from app import db

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def superadmin_required(f):
    """超级管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        if not current_user.is_superadmin:
            return jsonify({'success': False, 'message': '需要超级管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


def mask_phone(phone):
    """手机号脱敏"""
    if not phone or len(phone) < 7:
        return phone or ''
    return phone[:3] + '****' + phone[-4:]


@bp.route('/config', methods=['GET'])
@login_required
@superadmin_required
def get_config():
    """获取系统配置"""
    configs = SystemConfig.query.all()
    config_dict = {c.key: c.value for c in configs}

    # 不返回明文AppSecret
    result = {
        'dingtalk_appkey': config_dict.get('dingtalk_appkey', ''),
        'dingtalk_appsecret_set': bool(config_dict.get('dingtalk_appsecret', '')),
        'reminder_days_before': int(config_dict.get('reminder_days_before', 60)),
        'reminder_frequency': config_dict.get('reminder_frequency', 'weekly'),
        'reminder_weekday': config_dict.get('reminder_weekday', 'TH'),
        'reminder_hour': int(config_dict.get('reminder_hour', 9)),
        'reminder_minute': int(config_dict.get('reminder_minute', 0)),
        'reminder_stop_days': int(config_dict.get('reminder_stop_days', 5))
    }

    return jsonify(result), 200


@bp.route('/config', methods=['PUT'])
@login_required
@superadmin_required
def update_config():
    """更新系统配置"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    allowed_keys = [
        'dingtalk_appkey', 'dingtalk_appsecret',
        'reminder_days_before', 'reminder_frequency',
        'reminder_weekday', 'reminder_hour',
        'reminder_minute', 'reminder_stop_days'
    ]

    for key, value in data.items():
        if key not in allowed_keys:
            continue

        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            config.value = str(value)
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(key=key, value=str(value))
            db.session.add(config)

    db.session.commit()
    return jsonify({'success': True}), 200


@bp.route('/config/test', methods=['POST'])
@login_required
@superadmin_required
def test_dingtalk_connection():
    """测试钉钉连接"""
    dingtalk_service = DingTalkService()
    try:
        access_token = dingtalk_service.get_access_token()
        if access_token:
            return jsonify({'success': True, 'message': '连接成功'}), 200
        else:
            return jsonify({'success': False, 'message': '获取access_token失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'连接失败: {str(e)}'}), 500


@bp.route('/users', methods=['GET'])
@login_required
@superadmin_required
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    search = request.args.get('search', '')

    query = User.query

    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                User.name.ilike(search_pattern),
                User.phone.ilike(search_pattern)
            )
        )

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    users = pagination.items

    items = []
    for user in users:
        items.append({
            'id': user.id,
            'name': user.name,
            'phone': mask_phone(user.phone),
            'unionid': user.unionid,
            'is_active': user.is_active,
            'is_superadmin': user.is_superadmin,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'created_at': user.created_at.isoformat() if user.created_at else None
        })

    return jsonify({
        'items': items,
        'total': pagination.total,
        'page': page,
        'limit': limit
    }), 200


@bp.route('/users', methods=['POST'])
@login_required
@superadmin_required
def create_user():
    """创建用户"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    unionid = data.get('unionid', '').strip()
    is_superadmin = data.get('is_superadmin', False)

    if not name or not phone:
        return jsonify({'success': False, 'message': '姓名和手机号不能为空'}), 400

    if not password:
        return jsonify({'success': False, 'message': '密码不能为空'}), 400

    # 检查手机号唯一性
    if User.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'message': '手机号已被注册'}), 400

    user = User(
        name=name,
        phone=phone,
        unionid=unionid if unionid else None,
        is_superadmin=is_superadmin,
        is_active=True
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'phone': mask_phone(user.phone)
        }
    }), 201


@bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@superadmin_required
def update_user(user_id):
    """更新用户信息（含重置密码）"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    if 'name' in data:
        user.name = data['name'].strip()

    if 'unionid' in data:
        user.unionid = data['unionid'].strip() if data['unionid'] else None

    if 'password' in data and data['password']:
        user.set_password(data['password'])

    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'phone': mask_phone(user.phone)
        }
    }), 200


@bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@login_required
@superadmin_required
def toggle_user_status(user_id):
    """启用/停用用户"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    # 防止停用自己
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能停用自己的账号'}), 400

    # 防止停用最后一个超级管理员
    if user.is_superadmin and user.is_active:
        superadmin_count = User.query.filter_by(is_superadmin=True, is_active=True).count()
        if superadmin_count <= 1:
            return jsonify({'success': False, 'message': '不能停用最后一个超级管理员'}), 400

    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'is_active': user.is_active
    }), 200
