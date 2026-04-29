"""
认证功能测试
"""
import pytest
from app.models.user import User


class TestAuth:
    """认证功能测试"""

    def test_login_page_loads(self, client):
        """测试登录页面可访问"""
        response = client.get('/auth/login')
        assert response.status_code in (200, 302)

    def test_login_success(self, client, app):
        """测试成功登录"""
        from app import db
        with app.app_context():
            user = User(name='测试用户', phone='13800138000', is_active=True)
            user.set_password('Test@123')
            db.session.add(user)
            db.session.commit()

        response = client.post('/auth/login', json={
            'phone': '13800138000',
            'password': 'Test@123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_login_invalid_password(self, client, app):
        """测试密码错误"""
        from app import db
        with app.app_context():
            user = User(name='测试', phone='13800138000', is_active=True)
            user.set_password('Test@123')
            db.session.add(user)
            db.session.commit()

        response = client.post('/auth/login', json={
            'phone': '13800138000',
            'password': 'Wrong@123'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    def test_login_nonexistent_user(self, client):
        """测试用户不存在"""
        response = client.post('/auth/login', json={
            'phone': '13900000000',
            'password': 'any'
        })
        assert response.status_code == 401

    def test_get_current_user(self, auth_client):
        """测试获取当前用户信息"""
        response = auth_client.get('/auth/me')
        assert response.status_code == 200
        data = response.get_json()
        assert 'id' in data
        assert 'name' in data

    def test_password_hashing(self, app):
        """测试密码哈希功能"""
        with app.app_context():
            user = User(name='测试', phone='13800138000')
            user.set_password('MyPassword@123')
            assert user.check_password('MyPassword@123') is True
            assert user.check_password('wrong') is False
