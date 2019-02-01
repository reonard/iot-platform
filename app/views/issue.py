from flask import Blueprint, request
from flask_restful import Resource, Api, current_app
from app.models.issue_config import *
from app.models.device import Device
from app.models.customer import Customer
from app.utils.http_utils import obj_response, response, get_req_param
from app.lib.auth import check_login,login_required
from app.lib.auth import current_user_info

import json

mod = Blueprint('issue', __name__)
mod.before_request(check_login)
mod_api = Api(mod)

class IssueConfig(Resource):
    @login_required
    def post(self):

        action_type = request.form.get('action_type','')
        project = request.form.get('project','')
        try:
            devices = json.loads(request.form.get('devices','[]'))
        except:
            devices = []

        threshold = {
            "PID":0,
            "LA":request.form.get('LA',0),
            "TA1":request.form.get('TA1',0),
            "TA2":request.form.get('TA2',0),
            "TA3":request.form.get('TA3',0),
            "TA4":request.form.get('TA4',0),
            "CAA":request.form.get('CAA',0),
            "CAB":request.form.get('CAB',0),
            "CAC":request.form.get('CAC',0)
        }

        msg = {
        "RequestPush":False,
        "IsReset":False,
        "IsSelfCheck":False,
        "ProbeData":[threshold]
        }

        if action_type == "config":
            pass
        elif action_type == "push":
            msg["RequestPush"] = True
        elif action_type == "reset":
            msg["IsReset"] = True
        elif action_type == "check":
            msg["IsSelfCheck"] = True
        else:
            return response(error = "Missing action")

        user_id = current_user_info.id
        device_config = Config.create_device_config(json.dumps(msg))
        issuemsg = IssueMsg.create_issue_msg(device_config.id, action_type, user_id)
        if devices:
            for device_id in devices:
                if Device.get_one_device(device_id):
                    IssueStatus.create_device_config(device_id, issuemsg.id)
                    Device.update_device({"device_id":device_id},{"config_id":device_config.id})
                    #Device.query.filter_by(device_id=device_id).update({"config_id":device_config.id})
        else:
            for obj in  (Customer.query.filter_by(id=project).first().children):
                for device in (Device.get_more_device(obj.id)):
                    device_id = device.device_id
                    if Device.get_one_device(device_id):
                        IssueStatus.create_device_config(device_id, issuemsg.id)
                        Device.update_device({"device_id": device_id}, {"config_id": device_config.id})

        return response("Issued by the successful.")

class IssueHistory(Resource):
    @login_required
    def get(self):
        data = IssueMsg.query.filter_by(**request.args).all()

        exclude = ()
        return obj_response(data=data, schema=IssueMsgSchema(exclude=exclude), many=True)

class IssueDetail(Resource):
    @login_required
    def get(self, id):

        obj = IssueMsg.query.filter_by(id = id).first()
        data = obj.statuss

        IssueStatusSchema
        exclude = ()
        return obj_response(data=data, schema=IssueStatusSchema(exclude=exclude), many=True)

mod_api.add_resource(IssueConfig, '/config/')
mod_api.add_resource(IssueHistory, '/history/')
mod_api.add_resource(IssueDetail, '/history/<id>/')
