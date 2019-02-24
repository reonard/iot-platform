from flask import Blueprint, request
from flask_restful import Resource, Api, current_app
from app.models.issue_config import *
from app.models import Device, DeviceModel, User, MetricType
from app.models.customer import Customer
from app.utils.http_utils import obj_response, response, get_req_param
from app.lib.auth import check_login, login_required
from app.lib.auth import current_user_info
from app.lib.const import IssueStatusCN

import json

mod = Blueprint('issue', __name__)
mod.before_request(check_login)
mod_api = Api(mod)


class CreateIssueConfig(Resource):
    @login_required
    def post(self):
        name = get_req_param("name")
        model = get_req_param("model")
        m = DeviceModel.query.filter_by(name=model).first()
        metrics = m.metrics
        threshold = {
            "PID": 0
        }
        for metric in metrics:
            value = get_req_param(metric.metric_alarm_config_key)
            if value is None:
                return response(error="%s不能为空" % metric.metric_display_name)
            threshold[metric.metric_alarm_config_key] = value

        msg = {
            "RequestPush": False,
            "IsReset": False,
            "IsSelfCheck": False,
            "ProbeData": [threshold]
        }

        user_id = current_user_info.id
        device_config = DeviceConfig.create_device_config(name, json.dumps(msg), user_id, m.name)

        return response(data={
            "id": device_config.id,
            "name": device_config.name
        })


class UpdateIssueConfig(Resource):
    @login_required
    def post(self, config_id):
        name = get_req_param("name")
        model = get_req_param("model")
        m = DeviceModel.query.filter_by(name=model).first()
        metrics = m.metrics
        threshold = {
            "PID": 0
        }
        for metric in metrics:
            value = get_req_param(metric.metric_alarm_config_key)
            if value is None:
                return response(error="%s不能为空" % metric.metric_display_name)
            threshold[metric.metric_alarm_config_key] = value

        msg = {
            "RequestPush": False,
            "IsReset": False,
            "IsSelfCheck": False,
            "ProbeData": [threshold]
        }

        user_id = current_user_info.id
        flag = DeviceConfig.update_device_config(config_id, name, json.dumps(msg), user_id, m.name)
        if flag == 1:
            return response(data="Success")
        else:
            return response(error="Failure")


class IssueConfigList(Resource):

    @login_required
    def get(self):

        name = request.args.get("name")
        if not name:
            conf_list = DeviceConfig.query.all()
        else:
            conf_list = DeviceConfig.query.filter(DeviceConfig.name.ilike("%%%s%%" % name)).all()

        exclude = ()
        return obj_response(data=conf_list, schema=DeviceConfigSchema(exclude=exclude), many=True)


class ConfigInfo(Resource):
    @login_required
    def get(self, config_id):
        obj = DeviceConfig.query.filter_by(id=config_id).first()
        configs = json.loads(obj.configs)
        threshold_value = configs["ProbeData"][0]
        m = DeviceModel.query.filter_by(name=obj.model_name).first()
        metrics = m.metrics

        probe_data = {}
        for metric in metrics:
            if metric.type.type_name not in probe_data:
                probe_data[metric.type.type_name] = []

            item = {}
            value = threshold_value.get(metric.metric_alarm_config_key)
            item["metric_unit"] = metric.type.type_unit
            item["metric_alarm_config_key"] = metric.metric_alarm_config_key
            item["metric_key"] = metric.metric_key
            item["metric_id"] = metric.metric_id
            item["metric_display_name"] = metric.metric_display_name
            item["value"] = value
            probe_data[metric.type.type_name].append(item)
        configs["ProbeData"] = [{"name": type_name, "list": probe_data[type_name]} for type_name in probe_data]

        obj.configs = configs

        exclude = ()
        return obj_response(data=obj, schema=DeviceConfigSchema(exclude=exclude), many=False)


class IssueConfig(Resource):
    @login_required
    def post(self):

        config_id = get_req_param('config_id', '')
        project = get_req_param('project', '')
        action_type = get_req_param('action_type')
        devices = get_req_param('devices',[])

        user_id = current_user_info.id
        device_config = DeviceConfig.query.filter_by(id=config_id).first()
        issue_msg = IssueMsg.create_issue_msg(device_config.id, action_type, user_id)
        if devices:
            for device_id in devices:
                if Device.get_one_device(device_id):
                    IssueStatus.create_device_config(device_id, issue_msg.id)
                    Device.update_device({"device_id": device_id}, {"config_id": device_config.id})
        else:
            for obj in Customer.query.filter_by(id=project).first().children:
                for device in (Device.get_more_device(obj.id)):
                    device_id = device.device_id
                    if Device.get_one_device(device_id):
                        IssueStatus.create_device_config(device_id, issue_msg.id)
                        Device.update_device({"device_id": device_id}, {"config_id": device_config.id})

        return response("Issued by the successful.")


class IssueHistory(Resource):
    @login_required
    def get(self):
        page = request.args.get("Page", 1)
        pagesize = request.args.get("PageSize", 10)

        q = {}
        for key, v in request.args.items():
            if key in dir(Device):
                q[key] = v
        base_query = IssueMsg.query.filter_by(**q)

        total = base_query.count()

        issue = base_query.order_by(IssueMsg.create_time.desc()).paginate(int(page), int(pagesize))

        result = []
        for obj in issue.items:
            item = {}
            item["id"] = obj.id
            item["action_type"] = obj.action_type
            item["create_time"] = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")
            item["created_by"] = obj.user.name
            item["config_name"] = obj.config.name
            result.append(item)

        return response(data={"result": result,
                              "totalPage": issue.pages, "total": total})


class IssueDetail(Resource):
    @login_required
    def get(self, msg_id):

        issue = IssueMsg.query.filter_by(id=msg_id).first()
        data = issue.statuses
        result = []
        for obj in data:
            item = {}
            item["id"] = obj.id
            device = obj.device
            item["device_name"] = device.device_name
            item["location"] = device.location
            item["issue_status"] = IssueStatusCN.get(obj.issue_status,"")
            if obj.success is True:
                item["success"] = "成功"
            elif obj.success is False:
                item["success"] = "失败"
            else:
                item["success"] = "等待"
            item["status_time"] = obj.status_time.strftime("%Y-%m-%d %H:%M:%S") if obj.status_time else ""
            item["create_time"] = obj.create_time.strftime("%Y-%m-%d %H:%M:%S")

            result.append(item)

        return response(data=result)


mod_api.add_resource(CreateIssueConfig, '/config/create/')
mod_api.add_resource(UpdateIssueConfig, '/config/update/<int:config_id>/')
mod_api.add_resource(IssueConfigList, '/config/list/')
mod_api.add_resource(ConfigInfo, '/config/<int:config_id>/')
mod_api.add_resource(IssueConfig, '/config/')
mod_api.add_resource(IssueHistory, '/history/')
mod_api.add_resource(IssueDetail, '/history/<int:msg_id>/')
