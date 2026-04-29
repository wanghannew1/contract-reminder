"""
合同模型 - 62列CSV数据映射
"""
from datetime import datetime
from app import db


class Contract(db.Model):
    """合同模型"""
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # 员工基本信息
    id_number = db.Column(db.String(32))                # 公民身份号码（列0）
    employee_name = db.Column(db.String(128), nullable=False)   # 姓名（列1）
    gender = db.Column(db.String(4))                   # 性别（列2）
    birth_date = db.Column(db.Date)                    # 出生日期（列3）
    employee_phone = db.Column(db.String(32))          # 联系电话（列50）

    # 合同信息
    contract_start_date = db.Column(db.Date)           # 合同开始日期（列12）
    contract_end_date = db.Column(db.Date, nullable=False)  # 合同终止日期（列13）★
    contract_type = db.Column(db.String(64))           # 合同签订类型（列40）

    # 五险一金状态
    social_security_status = db.Column(db.String(32))  # 社保状态（列15）
    medical_insurance_status = db.Column(db.String(32))  # 医保状态（列21）
    housing_fund_status = db.Column(db.String(32))     # 公积金状态（列27）
    work_injury_status = db.Column(db.String(32))      # 工伤状态（列33）

    # 停保年月
    salary_end_month = db.Column(db.Date)              # 工资结束年月（列41）
    social_security_stop_month = db.Column(db.Date)   # 社保停保年月（列42）
    housing_fund_stop_month = db.Column(db.Date)       # 公积金停保年月（列43）
    medical_insurance_stop_month = db.Column(db.Date)  # 医保停保年月（列44）
    work_injury_stop_month = db.Column(db.Date)        # 工伤停保年月（列45）

    # 单位信息
    unit_name = db.Column(db.String(256))              # 单位名称（列47）
    billing_unit_name = db.Column(db.String(256))      # 结算单元名称（列48）
    employment_type = db.Column(db.String(64))         # 用工性质（列49）

    # 经办信息
    admin_name = db.Column(db.String(128))             # 经办人（列56）
    admin_org = db.Column(db.String(256))              # 经办机构（列57）
    handle_date = db.Column(db.Date)                   # 经办日期（列58）

    # 终止信息
    terminator = db.Column(db.String(128))             # 终止解除经办人（列59）
    terminator_date = db.Column(db.Date)               # 终止解除经办日期（列61）★

    # 元数据
    source_file = db.Column(db.String(256))             # 来源文件名
    deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一约束：同一管理员下，员工姓名+身份证号联合唯一
    __table_args__ = (
        db.UniqueConstraint('user_id', 'employee_name', 'id_number', name='uq_user_employee_id'),
        db.Index('idx_contracts_user_end', 'user_id', 'contract_end_date'),
        db.Index('idx_contracts_deleted', 'deleted'),
    )

    @property
    def is_expired(self):
        """是否已过期（终止日期小于今天）"""
        if self.contract_end_date is None:
            return True
        return self.contract_end_date < datetime.now().date()

    @property
    def is_terminated(self):
        """是否已提前终止（terminator_date非空）"""
        return self.terminator_date is not None

    @property
    def days_until_expiry(self):
        """距离到期天数"""
        if self.contract_end_date is None:
            return None
        delta = self.contract_end_date - datetime.now().date()
        return delta.days

    def __repr__(self):
        return f'<Contract {self.employee_name} ({self.contract_end_date})>'
