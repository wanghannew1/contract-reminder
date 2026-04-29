"""
路由蓝本导出
"""
from .auth import bp as auth_bp
from .contract import bp as contract_bp
from .calendar import bp as calendar_bp
from .admin import bp as admin_bp

__all__ = ['auth_bp', 'contract_bp', 'calendar_bp', 'admin_bp']
