from flask import Flask, request, make_response
from app.lib.logger import Logger
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy

mongo = PyMongo()
db = SQLAlchemy()


def create_app():

    app = Flask(__name__)
    app.config.from_pyfile('../configs.py')

    Logger.init(app, log_level='DEBUG')

    mongo.init_app(app)
    db.init_app(app)

    configure_blueprint(app)

    @app.after_request
    def option_request_handler(response):

        db.session.close()

        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    return app


def configure_blueprint(app):
    from app.views import mondata, device, alarm_data

    app.register_blueprint(mondata.mod, url_prefix='/mondata')
    app.register_blueprint(device.mod, url_prefix='/device')
    app.register_blueprint(alarm_data.mod, url_prefix='/alarm')
