"""
Pytest配置和fixtures
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['TESTING'] = '1'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret-key'


@pytest.fixture(scope='function')
def app():
    """创建测试用Flask应用"""
    from app import create_app, db

    application = create_app()
    application.config['TESTING'] = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """创建数据库会话"""
    from app import db
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()


@pytest.fixture
def mock_dingtalk_service():
    """Mock钉钉服务"""
    with patch('app.services.dingtalk.requests.post') as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'accessToken': 'test_token', 'expireIn': 7200}
        mock_post.return_value = mock_resp
        yield mock_post


@pytest.fixture
def auth_client(client, app):
    """创建已认证的测试客户端"""
    from app import db
    from app.models.user import User

    with app.app_context():
        user = User(
            name='测试管理员',
            phone='13800138000',
            is_active=True,
            is_superadmin=True,
            unionid='test_unionid'
        )
        user.set_password('Test@123')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = '1'

    return client


@pytest.fixture
def sample_contract_data():
    """示例合同数据（按实际模型）"""
    return {
        'employee_name': '张三',
        'id_number': '220102199001011234',
        'contract_start_date': '2024-01-01',
        'contract_end_date': '2027-01-01',
        'unit_name': '测试单位',
        'employee_phone': '13900139000'
    }


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        'name': '测试用户',
        'phone': '13900139000',
        'password': 'Test@123456'
    }
