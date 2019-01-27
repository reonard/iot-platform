from flask import request
import json
from app.lib.message import ResponseCode

HTTP_JSON_CONTENT = {'Content-type': 'application/json'}


def get_req_param(key, default=None):

    req_data = request.get_data()

    if not req_data:
        return default

    return json.loads(req_data).get(key, default)


def response(data=None, error=None, code=200, biz_code=ResponseCode.OK):

    success = True if not error else False

    resp = {
        "code": biz_code,
        "success": success,
        "data": data,
        "msg": error
    }

    return resp, code, HTTP_JSON_CONTENT


def obj_response(data, schema, many=False):

    dump_res = schema.dump(data, many=many)

    if dump_res.errors:
        return response(error='invalid obj')

    return response(data=dump_res.data)


def redirect(redirect_url, code=301):

    headers = {}

    headers.update({"location": redirect_url})
    headers.update(HTTP_JSON_CONTENT)

    return None, code, headers

