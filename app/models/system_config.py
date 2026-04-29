"""
系统配置模型
"""
from datetime import datetime
from app import db


class SystemConfig(db.Model):
    """系统配置模型（键值对形式）"""
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(256))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_value(cls, key, default=None):
        """获取配置值"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default

    @classmethod
    def set_value(cls, key, value):
        """设置配置值"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
        else:
            config = cls(key=key, value=value)
            db.session.add(config)
        return config

    def __repr__(self):
        return f'<SystemConfig {self.key}={self.value}>'
