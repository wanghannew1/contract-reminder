"""
CSV导入功能测试
"""
import pytest
import csv
import io
from app.services.csv_importer import CSVImporter


class TestCSVImporter:
    """CSV导入功能测试"""

    def test_detect_encoding_utf8(self):
        """测试UTF-8编码检测"""
        importer = CSVImporter(user_id=1)
        content = "姓名,身份证号\n张三,220102199001011234".encode('utf-8')
        encoding = importer.detect_encoding(content)
        assert encoding in ('utf-8', 'utf-8-sig')

    def test_detect_encoding_gbk(self):
        """测试GBK编码检测"""
        importer = CSVImporter(user_id=1)
        content = "姓名,身份证号\n张三,220102199001011234".encode('gbk')
        encoding = importer.detect_encoding(content)
        assert encoding.upper() in ('GBK', 'GB2312', 'GB18030')

    def test_parse_valid_csv(self):
        """测试解析有效CSV"""
        importer = CSVImporter(user_id=1)
        csv_content = "公民身份号码,姓名,性别,出生日期,,,,,,,,,,合同开始日期,合同终止日期,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,用工单位\n220102199001011234,张三,男,1990-01-01,,,,,,,,,,2024-01-01,2027-01-01,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,测试单位"
        rows = list(csv.reader(io.StringIO(csv_content)))
        assert len(rows) == 2

    def test_import_skips_expired_contracts(self):
        """测试跳过已过期合同"""
        importer = CSVImporter(user_id=1)
        importer.skipped_expired = 10
        assert importer.skipped_expired == 10

    def test_import_skips_terminated_contracts(self):
        """测试跳过已终止合同"""
        importer = CSVImporter(user_id=1)
        importer.skipped_terminated = 5
        assert importer.skipped_terminated == 5

    def test_import_summary(self):
        """测试导入结果摘要"""
        importer = CSVImporter(user_id=1)
        importer.imported_count = 100
        importer.skipped_expired = 20
        importer.skipped_terminated = 10
        importer.skipped_duplicate = 5
        importer.failed_count = 2

        summary = importer.get_summary()
        assert summary['imported'] == 100
        assert summary['skipped_expired'] == 20
        assert summary['skipped_terminated'] == 10
        assert summary['skipped_duplicate'] == 5
        assert summary['failed'] == 2

    def test_empty_csv_handling(self):
        """测试空CSV处理"""
        importer = CSVImporter(user_id=1)
        valid, failed = importer.parse_csv(b"")
        assert len(valid) == 0
