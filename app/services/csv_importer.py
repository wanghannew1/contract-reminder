"""
CSV合同数据导入服务
"""
import csv
import io
import json
import chardet
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from app import db
from app.models.contract import Contract
from app.models.import_log import ImportLog
from app.utils.helpers import parse_date


# CSV列索引映射（基于PRD 6.3.2）
COLUMN_MAPPING = {
    'id_number': 0,           # 公民身份号码
    'employee_name': 1,       # 姓名
    'gender': 2,              # 性别
    'birth_date': 3,          # 出生日期
    'contract_start_date': 12,  # 合同开始日期
    'contract_end_date': 13,    # 合同终止日期 ★
    'social_security_status': 15,  # 社保状态
    'medical_insurance_status': 21,  # 医保状态
    'housing_fund_status': 27,  # 公积金状态
    'work_injury_status': 33,  # 工伤状态
    'contract_type': 40,      # 合同签订类型
    'salary_end_month': 41,   # 工资结束年月
    'social_security_stop_month': 42,  # 社保停保年月
    'housing_fund_stop_month': 43,  # 公积金停保年月
    'medical_insurance_stop_month': 44,  # 医保停保年月
    'work_injury_stop_month': 45,  # 工伤停保年月
    'unit_name': 47,          # 单位名称
    'billing_unit_name': 48,  # 结算单元名称
    'employment_type': 49,    # 用工性质
    'employee_phone': 50,     # 联系电话
    'admin_name': 56,         # 经办人
    'admin_org': 57,          # 经办机构
    'handle_date': 58,        # 经办日期
    'terminator': 59,         # 终止解除经办人
    'terminator_date': 61,    # 终止解除经办日期 ★
}


class CSVImporter:
    """CSV合同数据导入器"""

    def __init__(self, user_id: int, source_file: str = None):
        self.user_id = user_id
        self.source_file = source_file or "unknown.csv"
        self.today = datetime.now().date()

        # 统计
        self.imported_count = 0
        self.skipped_expired = 0
        self.skipped_terminated = 0
        self.skipped_duplicate = 0
        self.failed_count = 0
        self.failed_detail: List[Dict[str, Any]] = []

    def detect_encoding(self, file_content: bytes) -> str:
        """自动检测文件编码（GBK/UTF-8/UTF-8-BOM）"""
        result = chardet.detect(file_content)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)

        # chardet可能返回utf-8-with-signature
        if encoding and 'sig' in encoding.lower():
            return 'utf-8-sig'
        if encoding and confidence < 0.7:
            # 置信度低时默认用GBK（中文Windows导出常用）
            return 'gbk'
        return encoding or 'utf-8'

    def parse_csv(self, file_content: bytes) -> Tuple[List[Dict[str, Any]], List[int]]:
        """
        解析CSV文件内容

        Returns:
            (valid_rows, failed_rows) - 有效行列表和失败行号列表
        """
        encoding = self.detect_encoding(file_content)
        try:
            text = file_content.decode(encoding)
        except UnicodeDecodeError:
            # 尝试备用编码
            text = file_content.decode('gbk', errors='replace')

        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            return [], []

        # 第一行是表头，跳过
        data_rows = rows[1:] if len(rows) > 1 else []
        valid_rows = []
        failed_rows = []

        for i, row in enumerate(data_rows):
            line_num = i + 2  # CSV行号（1基，减去表头）
            row_data = self._parse_row(row, line_num)
            if row_data:
                valid_rows.append(row_data)
            else:
                failed_rows.append(line_num)

        return valid_rows, failed_rows

    def _parse_row(self, row: List[str], line_num: int) -> Optional[Dict[str, Any]]:
        """解析单行数据"""
        try:
            # 检查必填字段
            if len(row) <= COLUMN_MAPPING['employee_name']:
                self._add_failure(line_num, "行数据列数不足")
                return None

            name = row[COLUMN_MAPPING['employee_name']].strip()
            if not name:
                self._add_failure(line_num, "姓名为空")
                return None

            # 合同终止日期（必填）
            end_date_str = row[COLUMN_MAPPING['contract_end_date']].strip() if len(row) > COLUMN_MAPPING['contract_end_date'] else ""
            if not end_date_str:
                self._add_failure(line_num, "合同终止日期为空")
                return None

            end_date = parse_date(end_date_str)
            if not end_date:
                self._add_failure(line_num, f"合同终止日期格式无法解析：'{end_date_str}'")
                return None

            # 检查是否已过期（终止日期 <= 今天）
            if end_date <= self.today:
                self.skipped_expired += 1
                return None

            # 终止解除经办日期（非空=已提前终止）
            term_date_str = row[COLUMN_MAPPING['terminator_date']].strip() if len(row) > COLUMN_MAPPING['terminator_date'] else ""
            if term_date_str:
                term_date = parse_date(term_date_str)
                if term_date:
                    self.skipped_terminated += 1
                    return None

            # 身份证号
            id_number = row[COLUMN_MAPPING['id_number']].strip() if len(row) > COLUMN_MAPPING['id_number'] else ""

            return {
                'user_id': self.user_id,
                'id_number': id_number,
                'employee_name': name,
                'gender': row[COLUMN_MAPPING['gender']].strip() if len(row) > COLUMN_MAPPING['gender'] else "",
                'birth_date': parse_date(row[COLUMN_MAPPING['birth_date']].strip()) if len(row) > COLUMN_MAPPING['birth_date'] else None,
                'employee_phone': row[COLUMN_MAPPING['employee_phone']].strip() if len(row) > COLUMN_MAPPING['employee_phone'] else "",
                'contract_start_date': parse_date(row[COLUMN_MAPPING['contract_start_date']].strip()) if len(row) > COLUMN_MAPPING['contract_start_date'] else None,
                'contract_end_date': end_date,
                'contract_type': row[COLUMN_MAPPING['contract_type']].strip() if len(row) > COLUMN_MAPPING['contract_type'] else "",
                'social_security_status': row[COLUMN_MAPPING['social_security_status']].strip() if len(row) > COLUMN_MAPPING['social_security_status'] else "",
                'medical_insurance_status': row[COLUMN_MAPPING['medical_insurance_status']].strip() if len(row) > COLUMN_MAPPING['medical_insurance_status'] else "",
                'housing_fund_status': row[COLUMN_MAPPING['housing_fund_status']].strip() if len(row) > COLUMN_MAPPING['housing_fund_status'] else "",
                'work_injury_status': row[COLUMN_MAPPING['work_injury_status']].strip() if len(row) > COLUMN_MAPPING['work_injury_status'] else "",
                'salary_end_month': parse_date(row[COLUMN_MAPPING['salary_end_month']].strip()) if len(row) > COLUMN_MAPPING['salary_end_month'] else None,
                'social_security_stop_month': parse_date(row[COLUMN_MAPPING['social_security_stop_month']].strip()) if len(row) > COLUMN_MAPPING['social_security_stop_month'] else None,
                'housing_fund_stop_month': parse_date(row[COLUMN_MAPPING['housing_fund_stop_month']].strip()) if len(row) > COLUMN_MAPPING['housing_fund_stop_month'] else None,
                'medical_insurance_stop_month': parse_date(row[COLUMN_MAPPING['medical_insurance_stop_month']].strip()) if len(row) > COLUMN_MAPPING['medical_insurance_stop_month'] else None,
                'work_injury_stop_month': parse_date(row[COLUMN_MAPPING['work_injury_stop_month']].strip()) if len(row) > COLUMN_MAPPING['work_injury_stop_month'] else None,
                'unit_name': row[COLUMN_MAPPING['unit_name']].strip() if len(row) > COLUMN_MAPPING['unit_name'] else "",
                'billing_unit_name': row[COLUMN_MAPPING['billing_unit_name']].strip() if len(row) > COLUMN_MAPPING['billing_unit_name'] else "",
                'employment_type': row[COLUMN_MAPPING['employment_type']].strip() if len(row) > COLUMN_MAPPING['employment_type'] else "",
                'admin_name': row[COLUMN_MAPPING['admin_name']].strip() if len(row) > COLUMN_MAPPING['admin_name'] else "",
                'admin_org': row[COLUMN_MAPPING['admin_org']].strip() if len(row) > COLUMN_MAPPING['admin_org'] else "",
                'handle_date': parse_date(row[COLUMN_MAPPING['handle_date']].strip()) if len(row) > COLUMN_MAPPING['handle_date'] else None,
                'terminator': row[COLUMN_MAPPING['terminator']].strip() if len(row) > COLUMN_MAPPING['terminator'] else "",
                'terminator_date': parse_date(term_date_str) if term_date_str else None,
                'source_file': self.source_file,
            }

        except Exception as e:
            self._add_failure(line_num, str(e))
            return None

    def _add_failure(self, line_num: int, reason: str):
        """记录解析失败"""
        self.failed_count += 1
        self.failed_detail.append({"row": line_num, "reason": reason})

    def import_contracts(self, file_content: bytes) -> Dict[str, Any]:
        """
        执行导入

        Returns:
            导入结果统计 dict
        """
        valid_rows, failed_rows = self.parse_csv(file_content)

        for row_data in valid_rows:
            # 检查重复：同一用户下employee_name + id_number联合唯一
            existing = Contract.query.filter_by(
                user_id=self.user_id,
                employee_name=row_data['employee_name'],
                id_number=row_data.get('id_number', '')
            ).first()

            if existing:
                # 对比合同终止日期：新记录更晚则更新，否则跳过
                if existing.contract_end_date < row_data['contract_end_date']:
                    # 更新已有记录
                    for key, value in row_data.items():
                        setattr(existing, key, value)
                    db.session.add(existing)
                    self.imported_count += 1
                else:
                    self.skipped_duplicate += 1
            else:
                # 新增
                contract = Contract(**row_data)
                db.session.add(contract)
                self.imported_count += 1

        # 记录导入日志
        import_log = ImportLog(
            user_id=self.user_id,
            filename=self.source_file,
            total_rows=self.imported_count + self.skipped_expired + self.skipped_terminated + self.skipped_duplicate + self.failed_count,
            imported_count=self.imported_count,
            skipped_expired=self.skipped_expired,
            skipped_terminated=self.skipped_terminated,
            skipped_duplicate=self.skipped_duplicate,
            failed_count=self.failed_count,
            failed_detail=json.dumps(self.failed_detail) if self.failed_detail else None
        )
        db.session.add(import_log)
        db.session.commit()

        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """获取导入结果摘要"""
        return {
            "imported": self.imported_count,
            "skipped_expired": self.skipped_expired,
            "skipped_terminated": self.skipped_terminated,
            "skipped_duplicate": self.skipped_duplicate,
            "failed": self.failed_count,
            "failed_detail": self.failed_detail,
            "import_log_id": None  # 导入后填充
        }

    def import_file(self, file) -> Dict[str, Any]:
        """
        从 Flask 文件对象导入

        Args:
            file: Flask 文件对象 (werkzeug.datastructures.FileStorage)

        Returns:
            导入结果统计 dict
        """
        # 读取文件内容
        file_content = file.read()
        self.source_file = file.filename or "unknown.csv"

        # 调用现有的导入方法
        return self.import_contracts(file_content)
