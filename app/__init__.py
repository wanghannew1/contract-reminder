"""
合同到期钉钉提醒系统 - Flask应用
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    import os
    # 项目根目录
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_path, 'templates')
    static_path = os.path.join(base_path, 'static')

    app = Flask(__name__,
                template_folder=template_path,
                static_folder=static_path)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)

    # 豁免API路由的CSRF保护
    from app.routes import auth, contract, calendar, admin
    csrf.exempt(auth.bp)
    csrf.exempt(contract.bp)
    csrf.exempt(calendar.bp)
    csrf.exempt(admin.bp)

    from app.routes.pages import bp as pages_bp
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(contract.bp)
    app.register_blueprint(calendar.bp)
    app.register_blueprint(admin.bp)

    with app.app_context():
        db.create_all()

    return app
