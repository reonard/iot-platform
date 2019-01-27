from flask import Blueprint, request
from flask_restful import Resource, Api, current_app
from app.models.device import Device, DeviceSchema
from app.models.device_model import DeviceModel, DeviceModelSchema
from app.models.customer import Customer
from app.lib.mongo import get_mongo_data
from app.utils.http_utils import obj_response, response, get_req_param
from app.lib.const import DeviceStatus, DeviceStatusCN,MONGO_ALARM_COLLECTION
from sqlalchemy import func
from app import db
from app.lib.auth import check_login

mod = Blueprint('device', __name__)
mod.before_request(check_login)
mod_api = Api(mod)


class DeviceRegister(Resource):

    def post(self):

        device_sim = get_req_param('SimCode')
        if not device_sim:
            return response("Missing SimCode")

        try:
            device = Device.create_device(device_sim, 'model911', 2)
        except Exception as ex:
            print(ex)
            return response(error='Could not create device')

        return response(data={
            "SimID": device.device_id,
            "SimCode": device.device_sim,
            "HostURL": "http://"+current_app.config.get("HOST_URL")})


class DeviceList(Resource):

    def get(self):

        devices = Device.query.filter_by(**request.args)

        exclude = ('metric_types',)
        return obj_response(data=devices, schema=DeviceSchema(exclude=exclude), many=True)


class DeviceModelList(Resource):

    def get(self):

        device_models = DeviceModel.query.filter_by(**request.args)

        return obj_response(data=device_models, schema=DeviceModelSchema(), many=True)


class DeviceDetail(Resource):

    def get(self, device_id):

        device = Device.get_one_device(device_id)

        if not device:
            return response(code=404)

        return obj_response(data=device, schema=DeviceSchema())


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

        #data = Device.query(func.count("device_id"))#.group_by("device_status")
        customer_name = "pilot"
        data = []
        for p in Customer.query.filter_by(name = customer_name).one().projects:
            project_name = p.name
            objs = db.session.query(Device.device_status, func.Count(Device.device_id)).filter(Device.project == project_name)\
                .group_by(Device.device_status).all()
            for obj in objs:
                data.append({DeviceStatusCN.get(obj[0],u"未知"):obj[1]})
        return response(data=data)

class DeviceOverview(Resource):
    def get(self):
        exclude = ('metric_types',)

        #data = Device.query(func.count("device_id"))#.group_by("device_status")
        customer_name = "pilot"
        data = {}

        alarm_sum = len(get_mongo_data(collection=MONGO_ALARM_COLLECTION, search={"customer": customer_name}))

        # project_sum = Project.query.filter_by(customer = customer_name).count()

        device_sum = 0
        for p in Customer.query.filter_by(name = customer_name).one().projects:
            project_name = p.name
            device_sum += Device.query.filter_by(project=project_name).count()
        data["alarm_sum"] = alarm_sum
        # data["project_sum"] = project_sum
        data["device_sum"] = device_sum
        print (data)
        return response(data=data)


mod_api.add_resource(DeviceRegister, '/register/')
mod_api.add_resource(DeviceList, '/list/')
mod_api.add_resource(DeviceModelList, '/device_model/list/')
mod_api.add_resource(DeviceDetail, '/detail/<device_id>/')
mod_api.add_resource(DeviceAlarmList, '/list/alarm/')
mod_api.add_resource(DeviceStatusCount, '/status/count')
mod_api.add_resource(DeviceOverview, '/overview')
