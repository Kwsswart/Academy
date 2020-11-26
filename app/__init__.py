import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager() 
login.login_view = 'auth.login' 
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap()
dropzone = Dropzone()
mail = Mail()
csrf = CSRFProtect()
moment = Moment()
 

def create_app(config_class=Config):
    """ Create application context """

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    dropzone.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, prefix='/auth')

    from app.staff import bp as staff_bp
    app.register_blueprint(staff_bp)

    from app.classes import bp as class_bp
    app.register_blueprint(class_bp)

    from app.students import bp as student_bp
    app.register_blueprint(student_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # file based logger    
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/academy.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '€(asctime)s €(levelname)s: €(message)s [in €pathnames:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
    
        app.logger.setLevel(logging.INFO)
        app.logger.info('Academy startup')
                    
    return app 

from app import models