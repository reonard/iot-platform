from flask import Flask, request, make_response
from app.lib.logger import Logger
from app.lib.mysql import register_filter
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import session

mongo = PyMongo()
db = SQLAlchemy()


def create_app():

    app = Flask(__name__)
    app.config.from_pyfile('../configs.py')

    Logger.init(app, log_level='DEBUG')

    # 初始化数据库
    mongo.init_app(app)
    db.init_app(app)

    # Session 设置
    app.secret_key = '1qazxsw2'
    app.config['SESSION_SQLALCHEMY'] = db
    Session(app)

    # 注册蓝图
    configure_blueprint(app)

    # 注册查询过滤器
    register_filter()

    @app.after_request
    def option_request_handler(response):

        db.session.close()
        # 如果没有设置用户，清除session/cookie
        if not session.get('user_id'):
            session.clear()

        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    return app


def configure_blueprint(app):

    from app.views import mondata, device, alarm_data, auth, issue, customer, device_config

    app.register_blueprint(mondata.mod, url_prefix='/mondata')
    app.register_blueprint(device.mod, url_prefix='/device')
    app.register_blueprint(alarm_data.mod, url_prefix='/alarm')
    app.register_blueprint(auth.mod, url_prefix='/auth')
    app.register_blueprint(issue.mod, url_prefix='/issue')
    app.register_blueprint(customer.mod, url_prefix='/customer')
    app.register_blueprint(device_config.mod, url_prefix='/configs')
