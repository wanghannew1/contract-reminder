"""
页面渲染路由
提供所有前端页面的渲染
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('pages', __name__)


@bp.route('/')
def index():
    """首页重定向到登录页或Dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('pages.dashboard'))
    return redirect(url_for('auth.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """主面板页面"""
    return render_template('dashboard.html')


@bp.route('/contracts')
@login_required
def contracts():
    """合同列表页面"""
    return render_template('contracts/list.html')


@bp.route('/contracts/import')
@login_required
def import_contracts():
    """合同导入页面"""
    return render_template('contracts/import.html')


@bp.route('/calendar')
@login_required
def calendar():
    """日程管理页面"""
    return render_template('calendar/list.html')


@bp.route('/admin/users')
@login_required
def admin_users():
    """用户管理页面"""
    if not current_user.is_superadmin:
        return redirect(url_for('pages.dashboard'))
    return render_template('admin/users.html')


@bp.route('/admin/settings')
@login_required
def admin_settings():
    """系统设置页面"""
    if not current_user.is_superadmin:
        return redirect(url_for('pages.dashboard'))
    return render_template('admin/settings.html')
