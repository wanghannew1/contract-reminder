"""
钉钉日历事件模型
"""
from datetime import datetime
from app import db


class CalendarEvent(db.Model):
    """日历事件模型"""
    __tablename__ = 'calendar_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))

    # 钉钉日程信息
    event_id = db.Column(db.String(128), nullable=False)   # 钉钉返回的eventId
    summary = db.Column(db.String(256))                     # 日程标题
    description = db.Column(db.Text)                        # 日程描述
    start_time = db.Column(db.DateTime)                    # 首次触发时间
    end_time = db.Column(db.DateTime)                      # 首次触发结束时间
    recurrence = db.Column(db.String(512))                 # RRULE字符串

    # 元数据
    source = db.Column(db.String(16), default='created')   # 来源标记
    deleted = db.Column(db.Boolean, default=False)
    sync_time = db.Column(db.DateTime)                     # 最后同步时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    contract = db.relationship('Contract', backref='calendar_events')

    # 唯一约束：每份合同只允许一条有效日程
    __table_args__ = (
        db.UniqueConstraint('user_id', 'contract_id', name='uq_user_contract_event'),
    )

    def __repr__(self):
        return f'<CalendarEvent {self.summary} ({self.event_id})>'
