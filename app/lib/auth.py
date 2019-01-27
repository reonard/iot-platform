from werkzeug.local import LocalProxy
from flask.globals import _request_ctx_stack, _lookup_req_object
from functools import wraps
from app.utils.http_utils import response
from flask_restful import output_json
from flask import session
from functools import partial
from app.models.user import User
from app.lib.message import ResponseCode

# Local Proxy 代理， 直接引用获取当前用户实例
current_user_info = LocalProxy(partial(_lookup_req_object, "current_user_info"))


def set_current_user_info(user_id):

    ctx = _request_ctx_stack.top

    ctx.current_user_info = user_id


def check_login(*args, func=None, **kwargs):

    user_id = session.get('user_id')

    if user_id:
        user_info = User.get_user_info(id=user_id)
        set_current_user_info(user_info)

        if func:
            return func(*args, **kwargs)
    else:
        session.clear()
        return output_json(*response(error="无效Token", biz_code=ResponseCode.ERROR_NO_AUTH))


def login_required(func):
    """
    对需要登陆的视图应用此装饰器
    :param function:
    :return:
    """
    @wraps(func)
    def wrap(*args, **kwargs):

        return check_login(*args, func=func, **kwargs)

    return wrap

