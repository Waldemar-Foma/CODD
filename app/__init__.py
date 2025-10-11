from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    app.config.from_object(config_class)
    
    uploads_dir = os.path.join(basedir, 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.routes import main_bp
    from app.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    with app.app_context():
        try:
            db.create_all()
            from app.models import User
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', email='admin@codd-smolensk.ru', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print('Создан администратор по умолчанию: admin/admin123')
        except Exception as e:
            print(f'Ошибка при создании таблиц: {e}')
    
    return app