from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models.device import Device
from collections import defaultdict
from app.utils.http_utils import response
from app.utils.time_utils import format_unixtime
from app.lib.mongo import get_mongo_data, update_mongo_data
from app.lib.const import MONGO_ALARM_COLLECTION, DeviceStatusCN
from bson import ObjectId
import json

mod = Blueprint('alarm_data', __name__)
mod_api = Api(mod)


class AlarmList(Resource):

    def get(self, device_id=None):

        device = Device.get_one_device(device_id=device_id)

        if not device:
            return response(data=[])

        alarms = []

        for m in device.alarm_data():
            alarms.append({
                "alarm_id": str(m.get("_id")),
                "alarm_time": format_unixtime(int(m.get('timestamp'))),
                "alarm_status": m.get('alarmhandlestatus', 0),
                "alarm_msg": "/".join(m.get('alarmdescription')),
                "alarm_handle": m.get('alarmhandle')
            })

        return response(data=alarms)


class AlarmHandle(Resource):

    def get(self, alarm_id):

        alarm = get_mongo_data(collection=MONGO_ALARM_COLLECTION, search={"_id": ObjectId(alarm_id)})

        resp = {
            "alarm_id": str(alarm[0].get("_id")),
            "alarm_time": format_unixtime(int(alarm[0].get('timestamp'))),
            "alarm_status": alarm[0].get('alarmhandlestatus', 0),
            "alarm_msg": "/".join(alarm[0].get('alarmdescription')),
            "alarm_handle": alarm[0].get('alarmhandle')
        }

        return response(data=resp)


    def post(self, alarm_id):

        alarm_handle = json.loads(request.get_data()).get('alarm_handle')
        alarm_handle_status = json.loads(request.get_data()).get('alarm_handle_status')

        update_mongo_data("alarm_data",
                          alarm_id,
                          alarmhandle=alarm_handle,
                          alarmhandlestatus=alarm_handle_status)

        return response()


class AlarmLatest(Resource):

    def get(self, device_id):

        device = Device.get_one_device(device_id)
        if not device:
            return response(code=404)

        return response(data=device.latest_alarm().get('alarmdescription'))


class AlarmLatestInfo(Resource):

    def get(self, device_id):

        device = Device.get_one_device(device_id)
        if not device:
            return response(code=404)

        alarm = device.latest_alarm().get('data')[0]

        alarm_detail = defaultdict(lambda: list())

        for mt in device.metrics():

            if mt.metric_status_key in alarm:

                alarm_detail[mt.metric_type].append({
                    'name': mt.metric_display_name,
                    'alarm': DeviceStatusCN[alarm.get(mt.metric_status_key)],
                    'status': alarm.get(mt.metric_status_key),
                    'value': alarm.get(mt.metric_key),
                    'unit': mt.type.type_unit
                })

        res = [alarm_detail.get(metric_type, []) for metric_type in device.metric_types]

        print(res)

        return response(data=res)


mod_api.add_resource(AlarmList, '/list/<device_id>')
mod_api.add_resource(AlarmHandle, '/handle/<alarm_id>')
mod_api.add_resource(AlarmLatest, '/latest/<device_id>')
mod_api.add_resource(AlarmLatestInfo, '/info/<device_id>')



