"""
合同到期钉钉提醒系统 - Flask应用
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


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

    from app.routes import auth, contract, calendar, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(contract.bp)
    app.register_blueprint(calendar.bp)
    app.register_blueprint(admin.bp)

    with app.app_context():
        db.create_all()

    return app
