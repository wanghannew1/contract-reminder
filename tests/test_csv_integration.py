"""
CSV导入集成测试 - 完整上传流程
"""
import pytest
import os
import json
from app.services.csv_importer import CSVImporter
from app.models.contract import Contract
from app.models.import_log import ImportLog
from app import db


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestCSVImportIntegration:
    """CSV导入完整集成测试"""

    def test_import_valid_csv_with_db(self, app, db_session):
        """测试完整CSV导入流程（含数据库）"""
        sample_csv = os.path.join(FIXTURES_DIR, 'sample_contracts.csv')

        with open(sample_csv, 'rb') as f:
            file_content = f.read()

        with app.app_context():
            importer = CSVImporter(user_id=1, source_file='sample_contracts.csv')
            result = importer.import_contracts(file_content)

            # 验证结果摘要
            assert result['total'] == 3, f"Expected 3 total rows, got {result['total']}"
            assert result['imported'] == 1, f"Expected 1 imported, got {result['imported']}"
            assert result['skipped_expired'] == 1, f"Expected 1 skipped (expired), got {result['skipped_expired']}"
            assert result['skipped_terminated'] == 1, f"Expected 1 skipped (terminated), got {result['skipped_terminated']}"
            assert result['skipped_duplicate'] == 0
            assert result['failed'] == 0
            assert result['import_log_id'] is not None

            # 验证合同已入库
            contracts = Contract.query.filter_by(user_id=1, deleted=False).all()
            assert len(contracts) == 1, f"Expected 1 contract, got {len(contracts)}"

            contract = contracts[0]
            assert contract.employee_name == '张三'
            assert contract.id_number == '220102199001011234'
            assert contract.unit_name == '测试单位甲'
            assert contract.contract_type == '固定期限'
            assert contract.contract_end_date is not None
            # 2027-06-30 > today (2026-05-08) so not expired
            assert not contract.is_expired
            assert not contract.is_terminated

            # 验证导入日志
            import_log = ImportLog.query.filter_by(id=result['import_log_id']).first()
            assert import_log is not None
            assert import_log.filename == 'sample_contracts.csv'
            assert import_log.total_rows == 3
            assert import_log.imported_count == 1
            assert import_log.skipped_expired == 1
            assert import_log.skipped_terminated == 1
            assert import_log.failed_count == 0

    def test_get_summary_includes_all_keys(self, app, db_session):
        """测试get_summary返回所有必需字段"""
        sample_csv = os.path.join(FIXTURES_DIR, 'sample_contracts.csv')

        with open(sample_csv, 'rb') as f:
            file_content = f.read()

        with app.app_context():
            importer = CSVImporter(user_id=1)
            result = importer.import_contracts(file_content)

            # 确认所有key存在
            required_keys = ['total', 'imported', 'skipped_expired', 'skipped_terminated',
                           'skipped_duplicate', 'failed', 'failed_detail', 'import_log_id']
            for key in required_keys:
                assert key in result, f"Missing key '{key}' in get_summary()"

    def test_duplicate_detection(self, app, db_session):
        """测试重复合同去重逻辑"""
        sample_csv = os.path.join(FIXTURES_DIR, 'sample_contracts.csv')

        with open(sample_csv, 'rb') as f:
            file_content = f.read()

        with app.app_context():
            # 第一次导入
            importer1 = CSVImporter(user_id=1)
            result1 = importer1.import_contracts(file_content)
            assert result1['imported'] == 1

            # 第二次导入相同文件 → 应该跳过重复
            importer2 = CSVImporter(user_id=1)
            result2 = importer2.import_contracts(file_content)
            # 张三的记录已存在且合同结束日期相同 → 跳过
            assert result2['imported'] == 0, f"Expected 0 new imports on duplicate, got {result2['imported']}"
            assert result2['skipped_duplicate'] == 1, f"Expected 1 duplicate, got {result2['skipped_duplicate']}"
            assert result2['skipped_expired'] == 1
            assert result2['skipped_terminated'] == 1

    def test_empty_csv_returns_zero_summary(self, app, db_session):
        """测试空CSV返回正确的空结果"""
        with app.app_context():
            importer = CSVImporter(user_id=1)
            result = importer.import_contracts(b"")
            assert result['total'] == 0
            assert result['imported'] == 0
            assert result['failed'] == 0

    def test_csv_with_only_header(self, app, db_session):
        """测试只有表头的CSV"""
        sample_csv = os.path.join(FIXTURES_DIR, 'sample_contracts.csv')

        with open(sample_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        header_only = lines[0].encode('utf-8')

        with app.app_context():
            importer = CSVImporter(user_id=1)
            result = importer.import_contracts(header_only)
            assert result['total'] == 0
            assert result['imported'] == 0
            assert result['failed'] == 0
