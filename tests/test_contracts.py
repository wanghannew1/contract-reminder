"""
合同管理功能测试
"""
import pytest
from datetime import datetime, timedelta
from app.models.contract import Contract


class TestContracts:
    """合同管理功能测试"""

    def test_contract_list_requires_auth(self, client):
        """测试合同列表需要认证"""
        response = client.get('/api/contracts/')
        assert response.status_code in (401, 302)

    def test_contract_list_authenticated(self, auth_client):
        """测试已认证用户可以访问合同列表"""
        response = auth_client.get('/api/contracts/')
        assert response.status_code == 200

    def test_contract_create(self, auth_client, app):
        """测试创建合同"""
        from app import db
        with app.app_context():
            contract = Contract(
                user_id=1,
                employee_name='张三',
                id_number='220102199001011234',
                contract_end_date=datetime.now().date() + timedelta(days=365)
            )
            db.session.add(contract)
            db.session.commit()

        response = auth_client.get('/api/contracts/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1

    def test_contract_delete(self, auth_client, app):
        """测试删除合同"""
        from app import db
        with app.app_context():
            contract = Contract(
                user_id=1,
                employee_name='李四',
                id_number='220102199001022345',
                contract_end_date=datetime.now().date() + timedelta(days=180)
            )
            db.session.add(contract)
            db.session.commit()
            contract_id = contract.id

        response = auth_client.delete(f'/api/contracts/{contract_id}')
        assert response.status_code == 200

    def test_contract_search(self, auth_client, app):
        """测试合同搜索"""
        from app import db
        with app.app_context():
            contract = Contract(
                user_id=1,
                employee_name='王五',
                id_number='220102199001033456',
                contract_end_date=datetime.now().date() + timedelta(days=365),
                unit_name='测试单位'
            )
            db.session.add(contract)
            db.session.commit()

        response = auth_client.get('/api/contracts/?search=王五')
        assert response.status_code == 200

    def test_contract_filter_by_expiry(self, auth_client, app):
        """测试按到期天数筛选"""
        response = auth_client.get('/api/contracts/?expire_within=30')
        assert response.status_code == 200

    def test_contract_days_until_expiry(self, app):
        """测试合同到期天数计算"""
        with app.app_context():
            contract = Contract(
                user_id=1,
                employee_name='测试',
                contract_end_date=datetime.now().date() + timedelta(days=100)
            )
            assert contract.days_until_expiry == 100
            assert contract.is_expired is False

    def test_contract_is_expired(self, app):
        """测试合同是否过期"""
        with app.app_context():
            contract = Contract(
                user_id=1,
                employee_name='测试',
                contract_end_date=datetime.now().date() - timedelta(days=1)
            )
            assert contract.is_expired is True
