from flask import Blueprint, request
from flask_restful import Resource, Api, current_app
from app.models.device import Device, DeviceSchema
from app.models.device_model import DeviceModel, DeviceModelSchema
from app.models.customer import Customer
from app.lib.mongo import get_mongo_data
from app.utils.http_utils import obj_response, response, get_req_param
from app.utils.public_utils import xls2dict
from app.lib.const import DeviceStatus, DeviceStatusCN,MONGO_ALARM_COLLECTION,USERNAME,PASSWORD
from sqlalchemy import func
from app import db
from app.lib.auth import check_login,login_required
from app.lib.auth import current_user_info

import datetime
import hashlib
import os
import time

mod = Blueprint('device', __name__)
mod.before_request(check_login)
mod_api = Api(mod)


class DeviceRegister(Resource):

    def post(self):

        device_sim = get_req_param('SimCode','')
        once = get_req_param('Once','')
        sign = get_req_param('Sign','')

        if sign != hashlib.md5((USERNAME+PASSWORD+once).encode("utf8")).hexdigest():
            return response("unknown device")

        device = Device.query.filter_by(device_sim=device_sim).first()

        if not device_sim or not device:
            return response("Missing SimCode")

        registry_time = datetime.datetime.now()

        try:
            flag = Device.update_device({"device_sim":device_sim,"device_status":-1}, {"device_status":0,"registry_time":registry_time})
            if flag != 1:
                return response(error='fail to register')
            #device = Device.create_device(device_sim, 'model911', 2)
        except Exception as ex:
            print(ex)
            return response(error='Could not create device')

        return response(data={
            "SimID": device.device_id,
            "SimCode": device.device_sim,
            "HostURL": "http://"+current_app.config.get("HOST_URL")})


class DeviceList(Resource):
    @login_required
    def get(self):

        Page = request.args.get("Page",1)
        PageSize = request.args.get("PageSize",10)

        q = {}
        for key,v in request.args.items():
            if key in dir(Device):
                if v:
                    q[key] = v
        BaseQuery = Device.query.filter_by(**q)

        total = BaseQuery.count()

        devices = BaseQuery.order_by(Device.registry_time.desc()).paginate(int(Page),int(PageSize))

        exclude = ('metric_types',)
        return response(data={"result":DeviceSchema(exclude=exclude).dump(devices.items, many=True).data,"totalPage":devices.pages, "total":total})


class DeviceModelList(Resource):

    def get(self):

        device_models = DeviceModel.query.filter_by(**request.args)

        return obj_response(data=device_models, schema=DeviceModelSchema(), many=True)


class DeviceDetail(Resource):

    def get(self, device_id):

        device = Device.get_one_device(device_id)

        if not device:
            return response(code=404)

        current_mon_data = []

        mon_data = device.last_mon_data()
        if mon_data:
            for metric_config in device.metrics():
                m_key = metric_config.metric_key
                current_mon_data.append({
                    "metric_name": metric_config.metric_display_name,
                    "metric_unit": metric_config.type.type_unit,
                    "metric_value": mon_data['data'][0].get(m_key)})

        device_info = DeviceSchema().dump(device).data

        return response(data={
            "mon_data": current_mon_data,
            "device_detail": device_info
        })


class DeviceAlarmList(Resource):

    def get(self):

        query = {}
        for k, v in request.args.items():
            if v:
                query[k] = v

        devices = Device.query.\
            filter(Device.device_status != DeviceStatus.STATUS_NORMAL).\
            filter_by(**query)

        exclude = ('metric_types',)
        return obj_response(data=devices, schema=DeviceSchema(exclude=exclude), many=True)


class DeviceStatusCount(Resource):
    def get(self):
        exclude = ('metric_types',)
        # data = Device.query(func.count("device_id"))#.group_by("device_status")

        data = []

        objs = db.session.query(Device.device_status, func.Count(Device.device_id)).\
            group_by(Device.device_status).all()

        for obj in objs:
            data.append({DeviceStatusCN.get(obj[0], u"未知"): obj[1]})
        return response(data=data)


class DeviceOverview(Resource):
    @login_required
    def get(self):
        exclude = ('metric_types',)

        # data = Device.query(func.count("device_id"))#.group_by("device_status")
        data = {}
        print ("================")
        print (current_user_info.viewable_projects)

        alarm_sum = len(get_mongo_data(collection=MONGO_ALARM_COLLECTION))

        # project_sum = Project.query.filter_by(customer = customer_name).count()

        breakdown_device_sum = Device.query.filter_by(device_status=4).count()
        # for p in Customer.query.filter_by(name = customer_name).one().projects:

        device_sum = Device.query.count()
        data["alarm_sum"] = alarm_sum
        data["project_sum"] = len(current_user_info.viewable_projects)
        data["device_sum"] = device_sum
        data["breakdown_device_sum"] = breakdown_device_sum

        return response(data=data)


class DeviceArea(Resource):
    @login_required
    def get(self):
        exclude = ('metric_types',)

        # data = Device.query(func.count("device_id"))#.group_by("device_status")
        data = []
        objs = db.session.query(Device.city_name, func.Count(Device.device_id)). \
            group_by(Device.city_name).all()

        for obj in objs:
            data.append({"name": obj[0], "value": obj[1]})

        return response(data=data)


class DeviceImportOne(Resource):
    @login_required
    def post(self):

        device_sim = get_req_param('device_sim','')
        device_name = get_req_param('device_name','未命名设备')
        location = get_req_param('location','')
        project = get_req_param('project','')

        if not device_sim or not device_name or not project or not location:
            return response(error="Required parameter missing")

        if project not in current_user_info.viewable_projects:
            return response(error="project do not exist")

        project = Customer.get_project_by_name(project)
        try:
            device = Device.create_device(device_sim, device_name, location, "model911", project.id)
        except Exception as ex:
            print(ex)
            return response(error='Could not create device')

        return response(data={"device_id": device.device_id})


class DeviceImportMore(Resource):
    @login_required
    def post(self):
        # SIM卡号	设备名	设备地址	项目

        data = request.files['file']
        filepath = r"/tmp/devices_%s_%s.xlsx"%(current_user_info.id,time.time())
        data.save(filepath)
        if not os.path.exists(filepath):
            return response(error = "Could not create device")

        viewable_projects = current_user_info.viewable_projects
        devices = xls2dict(filepath)
        for device in devices:
            device_sim = device.get("SIM卡号")
            device_name = device.get("设备名")
            location = device.get("设备地址")
            project = device.get("项目")
            if not device_sim or not device_name or not project or not location:
                return response(error="Required parameter missing")
            if project not in viewable_projects:
                return response(error="project %s do not exist"%project)

            project = Customer.get_project_by_name(project)
            try:
                device = Device.create_device(device_sim, device_name, location, "model911", project.id)
            except Exception as ex:
                print(ex)
                return response(error='Could not create device, simCode is %s'%device_sim)

        return response("ok")


mod_api.add_resource(DeviceRegister, '/register/')
mod_api.add_resource(DeviceList, '/list/')
mod_api.add_resource(DeviceArea, '/area/')
mod_api.add_resource(DeviceModelList, '/device_model/list/')
mod_api.add_resource(DeviceDetail, '/detail/<device_id>/')
mod_api.add_resource(DeviceAlarmList, '/list/alarm/')
mod_api.add_resource(DeviceStatusCount, '/status/count')
mod_api.add_resource(DeviceOverview, '/overview')
mod_api.add_resource(DeviceImportOne, '/import/one')
mod_api.add_resource(DeviceImportMore, '/import/more')
