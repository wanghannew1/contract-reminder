"""
用户模型 - 合同管理员与超级管理员
"""
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)                    # 管理员姓名
    phone = db.Column(db.String(32), unique=True, nullable=False)      # 手机号（登录名）
    password_hash = db.Column(db.String(256), nullable=False)          # 密码哈希
    unionid = db.Column(db.String(64))                                 # 钉钉unionId
    is_active = db.Column(db.Boolean, default=True)                   # 账号启用状态
    is_superadmin = db.Column(db.Boolean, default=False)              # 是否超级管理员
    last_login_at = db.Column(db.DateTime)                            # 最后登录时间
    login_fail_count = db.Column(db.Integer, default=0)               # 连续失败次数
    locked_until = db.Column(db.DateTime)                             # 锁定到期时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    contracts = db.relationship('Contract', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    calendar_events = db.relationship('CalendarEvent', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    import_logs = db.relationship('ImportLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def __repr__(self):
        return f'<User {self.name} ({self.phone})>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
