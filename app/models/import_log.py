"""
导入日志模型
"""
from datetime import datetime
from app import db


class ImportLog(db.Model):
    """CSV导入日志模型"""
    __tablename__ = 'import_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(256))
    total_rows = db.Column(db.Integer, default=0)
    imported_count = db.Column(db.Integer, default=0)
    skipped_expired = db.Column(db.Integer, default=0)
    skipped_terminated = db.Column(db.Integer, default=0)
    skipped_duplicate = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    failed_detail = db.Column(db.Text)                    # JSON格式的失败明细
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def failed_detail_list(self):
        """解析失败明细JSON"""
        import json
        if self.failed_detail:
            try:
                return json.loads(self.failed_detail)
            except json.JSONDecodeError:
                return []
        return []

    def __repr__(self):
        return f'<ImportLog {self.id} - {self.filename}>'
