from flask import Blueprint
from flask_restful import Resource, Api, request, current_app
from app.utils.http_utils import response
from app.lib.auth import login_required
from app.utils.http_utils import get_req_param
from app.controller.auth import login_user, logout_user
from app.lib.auth import current_user_info
from app.lib.message import ResponseCode
from app.utils.public_utils import api_request
from app.models.user import User

import qrcode
import os
from urllib.parse import quote


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
        qr_code_path = os.path.join(current_app.config.get("QR_CODE_DIR"), "%s.png" % current_user_info.id)
        if not os.path.exists(qr_code_path):
            if not os.path.exists(current_app.config.get("QR_CODE_DIR")):
                os.makedirs(current_app.config.get("QR_CODE_DIR"))
            qr_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s" \
                     "&redirect_uri=http://www.idevice-cloud.cn/auth/wechatbind/?user_id=1" \
                     "&response_type=code&scope=snsapi_userinfo&state=1&connect_redirect=1" \
                     "#wechat_redirect" % current_app.config.get("APPID")
            img = qrcode.make(qr_url)
            img.save(qr_code_path)
        return response(data={
            "username": current_user_info.name,
            "role": current_user_info.role,
            "qr_code":"/qr_codes/%s.png" % current_user_info.id
        })


class WechatBind(Resource):

    def get(self):
        user_id = request.args.get("user_id")
        code = request.args.get("code")

        appid = current_app.config.get("APPID")
        secret = current_app.config.get("SECRET")
        auth_url = "https://api.weixin.qq.com/sns/oauth2/access_token" \
                   "?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appid, secret, code)
        data = api_request(auth_url)
        if data:
            openid = data.get("openid")
        flag = User.update_user_info({"id": user_id}, {"openid": openid})

        return "Binding success"


mod_api.add_resource(Login, '/login/')
mod_api.add_resource(Logout, '/logout/')
mod_api.add_resource(UserInfo, '/userinfo/')
mod_api.add_resource(WechatBind, '/wechatbind/')
