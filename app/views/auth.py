from flask import Blueprint
from flask_restful import Resource, Api
from app.utils.http_utils import response
from app.lib.auth import login_required
from app.utils.http_utils import get_req_param
from app.controller.auth import login_user, logout_user
from app.lib.auth import current_user_info
from app.lib.message import ResponseCode


mod = Blueprint('auth', __name__)
mod_api = Api(mod)


class Login(Resource):

    def post(self):

        user_email = get_req_param("username")
        password = get_req_param("password")

        session_id = login_user(user_email, password)

        if session_id:
            return response(data={"token": str(session_id, encoding="utf-8")})
        else:
            return response(error="账号不存在或密码错误", biz_code=ResponseCode.ERROR_LOGIN)


class Logout(Resource):

    @login_required
    def post(self):
        logout_user()
        return response(data="已登出")


class UserInfo(Resource):

    @login_required
    def get(self):

        return response(data={
            "username": current_user_info.name,
            "role": current_user_info.role
        })


mod_api.add_resource(Login, '/login/')
mod_api.add_resource(Logout, '/logout/')
mod_api.add_resource(UserInfo, '/userinfo/')
