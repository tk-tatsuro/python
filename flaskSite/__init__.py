# flaskPj/__init__.py
from flask import Flask


def create_app():
    app = Flask(__name__)
    from mysite1.views import mysite1_bp
    from mysite2.views import mysite2_bp

    app.register_blueprint(mysite1_bp)
    app.register_blueprint(mysite2_bp)
    return app

