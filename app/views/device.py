from flask import Blueprint, request
from flask_restful import Resource, Api, current_app
from app.models.device import Device, DeviceSchema
from app.models.device_model import DeviceModel, DeviceModelSchema
from app.utils.http_utils import obj_response, response, get_req_param
from app.lib.const import DeviceStatus

mod = Blueprint('device', __name__)
mod_api = Api(mod)


class DeviceRegister(Resource):

    def post(self):

        device_sim = get_req_param('SimCode')
        if not device_sim:
            return response("Missing SimCode")

        try:
            device = Device.create_device(device_sim, 'model911', 'pilot')
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


mod_api.add_resource(DeviceRegister, '/register/')
mod_api.add_resource(DeviceList, '/list/')
mod_api.add_resource(DeviceModelList, '/device_model/list/')
mod_api.add_resource(DeviceDetail, '/detail/<device_id>/')
mod_api.add_resource(DeviceAlarmList, '/list/alarm/')
