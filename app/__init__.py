from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

# Logging
import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = "Please sign in to access this page."
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()

def create_app(config_class = Config) :
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    with app.app_context() :

        # Authentication Blueprint
        from app.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix = "/auth")

        # Profile Blueprint
        from app.profile import bp as profile_bp
        app.register_blueprint(profile_bp, url_prefix = "/profile")

        # Errors Blueprint
        from app.errors import bp as errors_bp
        app.register_blueprint(errors_bp, url_prefix = "/error")

        # Dash Blueprint
        from app.visualization import bp as viz_bp
        app.register_blueprint(viz_bp, url_prefix = "/visualization")

        # Main Blueprint
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)

        # Dash
        from dashboard.dash import create_dashboard
        app = create_dashboard(app)

        from app import models

        if not app.debug :
            if app.config["MAIL_SERVER"] :
                auth = None
                if app.config["MAIL_USERNAME"] and app.config["MAIL_PASSWORD"] :
                    auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                secure = None
                if app.config['MAIL_USE_TLS']:
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost = (app.config['MAIL_SERVER'], 
                    app.config['MAIL_PORT']),
                    fromaddr = 'no-reply@' + app.config['MAIL_SERVER'],
                    toaddrs = app.config['ADMINS'],
                    subject = 'Kanbanize Failure',
                    credentials = auth,
                    secure = secure
                )
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)

            if not os.path.exists('logs') :
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/kanbanize.log', maxBytes = 10240, backupCount = 10)
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('Kanbanize startup')

        return app