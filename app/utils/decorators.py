"""
装饰器 - 登录验证、超级管理员权限
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def login_required(func):
    """
    登录验证装饰器（Flask-Login提供@login_required，
    此处为兼容项目风格保留，实际使用flask_login.login_required）
    """
    from flask_login import login_required as fl_login_required
    return fl_login_required(func)


def superadmin_required(func):
    """
    超级管理员权限装饰器
    要求用户已登录且is_superadmin=True
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_superadmin:
            flash('权限不足，需要超级管理员权限', 'danger')
            return redirect(url_for('contract.index'))

        return func(*args, **kwargs)
    return decorated_function


def admin_required(func):
    """
    管理员权限装饰器
    要求用户已登录且is_active=True
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_active:
            flash('账号已被停用，请联系管理员', 'danger')
            return redirect(url_for('auth.login'))

        return func(*args, **kwargs)
    return decorated_function
