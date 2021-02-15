import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flaskr.utils.template_filters import replace_newline

login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'Please login.'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysite'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    # Database tracking management = off
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from flaskr.controllers.blueprint import bp
    app.register_blueprint(bp)
    # Specify a character string to replace the newline character
    app.add_template_filter(replace_newline)
    # db, migration, loginManager init
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app
