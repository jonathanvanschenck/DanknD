from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from config import Config

#Setup extras
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
bootstrap = Bootstrap()
socketio = SocketIO()

def create_app(configclass = Config):
    app = Flask(__name__)
    app.config.from_object(configclass)

    #Register extras
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    socketio.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.front import bp as front_bp
    app.register_blueprint(front_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/u')

    from app.game import bp as game_bp
    app.register_blueprint(game_bp, url_prefix='/g')

    return app

from app import models
