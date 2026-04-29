"""
前端测试 - HTML模板和JS验证
"""
import os
import pytest


class TestFrontendTemplates:
    """前端模板测试"""

    @pytest.fixture
    def template_dir(self):
        """模板目录路径"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

    def test_login_template_exists(self, template_dir):
        """测试登录模板存在"""
        path = os.path.join(template_dir, 'login.html')
        assert os.path.exists(path), f"login.html not found at {path}"

    def test_login_template_has_form(self, template_dir):
        """测试登录模板包含表单"""
        path = os.path.join(template_dir, 'login.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '<form' in content, "login.html should contain a form"
        assert 'username' in content or 'phone' in content, "login form should have username/phone field"
        assert 'password' in content, "login form should have password field"

    def test_login_template_has_submit(self, template_dir):
        """测试登录模板有提交按钮"""
        path = os.path.join(template_dir, 'login.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'submit' in content.lower(), "login form should have submit button"

    def test_dashboard_template_exists(self, template_dir):
        """测试仪表盘模板存在"""
        path = os.path.join(template_dir, 'dashboard.html')
        assert os.path.exists(path), f"dashboard.html not found at {path}"

    def test_dashboard_template_has_nav(self, template_dir):
        """测试仪表盘有导航栏（继承自base.html）"""
        path = os.path.join(template_dir, 'dashboard.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 仪表盘继承base.html，导航在base中
        assert 'base.html' in content or 'extends' in content, "dashboard should extend base.html"

    def test_contracts_list_template_exists(self, template_dir):
        """测试合同列表模板存在"""
        path = os.path.join(template_dir, 'contracts', 'list.html')
        assert os.path.exists(path), f"contracts/list.html not found at {path}"

    def test_contracts_list_has_table(self, template_dir):
        """测试合同列表有表格"""
        path = os.path.join(template_dir, 'contracts', 'list.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '<table' in content.lower() or 'datatable' in content.lower(), "contracts list should have a table"

    def test_contracts_import_template_exists(self, template_dir):
        """测试合同导入模板存在"""
        path = os.path.join(template_dir, 'contracts', 'import.html')
        assert os.path.exists(path), f"contracts/import.html not found at {path}"

    def test_contracts_import_has_file_input(self, template_dir):
        """测试导入页面有文件输入"""
        path = os.path.join(template_dir, 'contracts', 'import.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'file' in content.lower() or 'upload' in content.lower(), "import page should have file upload input"

    def test_calendar_list_template_exists(self, template_dir):
        """测试日程列表模板存在"""
        path = os.path.join(template_dir, 'calendar', 'list.html')
        assert os.path.exists(path), f"calendar/list.html not found at {path}"

    def test_admin_users_template_exists(self, template_dir):
        """测试用户管理模板存在"""
        path = os.path.join(template_dir, 'admin', 'users.html')
        assert os.path.exists(path), f"admin/users.html not found at {path}"

    def test_admin_settings_template_exists(self, template_dir):
        """测试系统设置模板存在"""
        path = os.path.join(template_dir, 'admin', 'settings.html')
        assert os.path.exists(path), f"admin/settings.html not found at {path}"

    def test_base_template_exists(self, template_dir):
        """测试基础模板存在"""
        path = os.path.join(template_dir, 'base.html')
        assert os.path.exists(path), f"base.html not found at {path}"

    def test_base_template_has_block(self, template_dir):
        """测试基础模板有block"""
        path = os.path.join(template_dir, 'base.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '{% block' in content, "base.html should have jinja2 blocks"

    def test_base_template_has_csrf_token(self, template_dir):
        """测试表单有CSRF token"""
        # CSRF通过csrf_token()函数在表单中使用
        login_path = os.path.join(template_dir, 'login.html')
        with open(login_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'csrf_token' in content, "login form should use csrf_token()"


class TestStaticFiles:
    """静态文件测试"""

    @pytest.fixture
    def static_dir(self):
        """静态文件目录路径"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')

    def test_css_exists(self, static_dir):
        """测试CSS文件存在"""
        path = os.path.join(static_dir, 'css', 'style.css')
        assert os.path.exists(path), f"style.css not found at {path}"

    def test_css_has_content(self, static_dir):
        """测试CSS文件有内容"""
        path = os.path.join(static_dir, 'css', 'style.css')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 100, "style.css should have substantial content"

    def test_js_exists(self, static_dir):
        """测试JS文件存在"""
        path = os.path.join(static_dir, 'js', 'app.js')
        assert os.path.exists(path), f"app.js not found at {path}"

    def test_js_has_alpine(self, static_dir):
        """测试JS使用Alpine.js"""
        path = os.path.join(static_dir, 'js', 'app.js')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'alpine' in content.lower() or '$data' in content or 'x-data' in content, "app.js should use Alpine.js"

    def test_js_syntax_valid(self, static_dir):
        """测试JS语法有效"""
        path = os.path.join(static_dir, 'js', 'app.js')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 检查基本语法问题
        assert content.count('{') == content.count('}'), "JS braces should be balanced"
        assert content.count('(') == content.count(')'), "JS parentheses should be balanced"
        assert content.count('[') == content.count(']'), "JS brackets should be balanced"

    def test_all_templates_extend_base(self):
        """测试所有模板继承base"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_path, 'templates')
        templates = ['login.html', 'dashboard.html']
        for tmpl in templates:
            path = os.path.join(template_dir, tmpl)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                assert 'base.html' in content or 'extends' in content, f"{tmpl} should extend base.html"


class TestLoginPage:
    """登录页面功能测试"""

    def test_login_page_loads_with_client(self, client):
        """测试登录页面可以加载"""
        response = client.get('/auth/login')
        assert response.status_code == 200, "Login page should return 200"

    def test_login_page_content_type(self, client):
        """测试登录页面是HTML"""
        response = client.get('/auth/login')
        assert b'html' in response.content_type.lower().encode() or b'text/html' in response.content_type.encode()

    def test_login_form_action(self, client):
        """测试登录表单提交到正确地址"""
        response = client.get('/auth/login')
        content = response.data.decode('utf-8')
        # 表单action可能是 /auth/login 或 url_for('auth.login')
        assert '/auth/login' in content or "url_for('auth.login')" in content, "Login form action should be /auth/login"

    def test_login_has_username_field(self, client):
        """测试登录页有用户名/手机号字段"""
        response = client.get('/auth/login')
        content = response.data.decode('utf-8')
        assert 'username' in content.lower() or 'phone' in content.lower(), "Login should have username/phone field"

    def test_login_has_password_field(self, client):
        """测试登录页有密码字段"""
        response = client.get('/auth/login')
        content = response.data.decode('utf-8')
        assert 'password' in content.lower(), "Login should have password field"

    def test_login_has_csrf_token(self, client):
        """测试登录页有CSRF token"""
        response = client.get('/auth/login')
        content = response.data.decode('utf-8')
        assert 'csrf' in content.lower() or 'token' in content.lower(), "Login form should have CSRF protection"


class TestDashboardPage:
    """仪表盘页面测试"""

    def test_dashboard_template_exists(self):
        """测试仪表盘模板存在"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_path, 'templates')
        path = os.path.join(template_dir, 'dashboard.html')
        assert os.path.exists(path), "dashboard.html template should exist"

    def test_dashboard_has_stats_cards(self):
        """测试仪表盘有统计卡片"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_path, 'templates')
        path = os.path.join(template_dir, 'dashboard.html')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 仪表盘应该有合同统计相关元素
        assert 'contract' in content.lower() or '统计' in content or 'stats' in content.lower()


class TestContractsPage:
    """合同页面测试"""

    def test_contracts_api_requires_auth(self, client):
        """测试合同API需要认证"""
        response = client.get('/api/contracts/')
        assert response.status_code in (401, 302), "Contracts API should require authentication"

    def test_contracts_api_returns_json(self, auth_client):
        """测试合同API返回JSON"""
        response = auth_client.get('/api/contracts/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data or 'total' in data, "Contracts API should return items or total"

    def test_contracts_api_pagination(self, auth_client):
        """测试合同API分页"""
        response = auth_client.get('/api/contracts/?page=1&limit=10')
        assert response.status_code == 200
        data = response.get_json()
        assert 'page' in data, "Contracts API should return page info"
        assert 'limit' in data, "Contracts API should return limit info"


class TestCalendarPage:
    """日程页面测试"""

    def test_calendar_api_requires_auth(self, client):
        """测试日程API需要认证"""
        response = client.get('/api/calendar/events')
        assert response.status_code in (401, 302), "Calendar API should require authentication"

    def test_calendar_api_returns_json(self, auth_client):
        """测试日程API返回JSON"""
        response = auth_client.get('/api/calendar/events')
        assert response.status_code == 200
