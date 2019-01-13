import cgi
from flask import request
import json

HTTP_JSON_CONTENT = {'Content-type': 'application/json'}


def get_req_param(key, default=None):

    req_data = request.get_data()

    if not req_data:
        return default

    return json.loads(req_data).get(key, default)


def response(error=None, data=None, code=200):

    if code != 200:
        return None, code, HTTP_JSON_CONTENT

    success = True if not error else False

    resp = {
        "success": success,
        "data": data,
        "msg": error
    }

    return resp, 200, HTTP_JSON_CONTENT


def obj_response(data, schema, many=False):

    dump_res = schema.dump(data, many=many)

    if dump_res.errors:
        return response(error='invalid obj')

    return response(data=dump_res.data)
