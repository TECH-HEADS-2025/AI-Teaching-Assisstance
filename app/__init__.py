from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
load_dotenv()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-hackathon')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///teacher_assistant.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from app.models import db, User
    db.init_app(app)
    
    login_manager.init_app(app)
    Migrate(app, db)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    
    # Add a root route
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    return app