import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flaskr.utils.template_filters import replace_newline

login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysite'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # データベース変更の追跡管理 = off
    from flaskr.views import bp
    app.register_blueprint(bp)
    app.add_template_filter(replace_newline) # 改行文字を置き換える文字列を指定
    db.init_app(app) # db初期化
    migrate.init_app(app, db) # migrate初期化
    login_manager.init_app(app) # login_manager初期化
    return app