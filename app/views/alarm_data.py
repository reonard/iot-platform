from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models.device import Device
from app.models.alarm import Alarm
from app.models.customer import Customer
from app.models.metric_config import MetricConfig
from collections import defaultdict
from app.utils.http_utils import response,get_req_param
from app.utils.time_utils import format_unixtime
from app.lib.mongo import get_mongo_data, update_mongo_data
from app.lib.const import MONGO_ALARM_COLLECTION, DeviceStatusCN
from sqlalchemy import func
from app import db
from bson import ObjectId
import json
import datetime
from dateutil.relativedelta import relativedelta
import time
from app.lib.auth import check_login

mod = Blueprint('alarm_data', __name__)
mod.before_request(check_login)
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

        alarm = []

        latest_alarm = device.latest_alarm()
        if latest_alarm:
            alarm = latest_alarm.get('data')[0]

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

        return response(data=res)


class AlarmCount(Resource):

    def get(self):
        now = datetime.datetime.now()
        startDate = request.args.get("startDate")
        endDate = request.args.get("endDate")
        unit = request.args.get("unit")

        res = []

        if unit == "month":
            today = datetime.datetime.today()
            zeroh = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
            for i in range(6, 0, -1):
                startDate = (zeroh - relativedelta(months=i-1))
                endDate = (startDate + relativedelta(months=1))
                print (startDate, endDate)
                value = len(get_mongo_data(collection=MONGO_ALARM_COLLECTION, start=str(time.mktime(startDate.timetuple())*1000), \
                                           end = str(time.mktime(endDate.timetuple())*1000)))
                res.append({"name": startDate.strftime("%Y-%m"),"value": value})

        elif unit == "day":
            zerod = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
            for i in range(0, now.day):
                startDate = (zerod + datetime.timedelta(days=i))
                endDate = (startDate + datetime.timedelta(days=1))
                print (startDate, endDate)
                value = len(
                    get_mongo_data(collection=MONGO_ALARM_COLLECTION, start=str(time.mktime(startDate.timetuple()) * 1000),\
                                   end=str(time.mktime(endDate.timetuple()) * 1000)))
                res.append({"name": startDate.strftime("%Y-%m-%d"), "value": value})
        print (res)
        return response(data=res)


class AlarmItemCount(Resource):

    def get(self):
        #todo 当前用户所属客户
        data = []

        objs = db.session.query(Alarm.alarm_item, func.Count(Alarm.id)).group_by(Alarm.alarm_item).all()
        for obj in objs:
            data.append({"name": MetricConfig.query.filter_by(metric_key=obj[0]).one().metric_display_name, "value": obj[1]})
        print (data)
        return response(data=data)


class AlarmCarousel(Resource):

    def get(self):
        data = []
        now = datetime.datetime.today()
        today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)

        alarm_list = get_mongo_data(collection=MONGO_ALARM_COLLECTION, start=str(time.mktime(today.timetuple()) * 1000))
        for alarm in alarm_list:
            item = {}
            item["alarmdescription"] = alarm.get("alarmdescription")
            item["alarm_name"] = Device.query.filter(Device.device_id==alarm.get("deviceid")).one().device_name
            data.append(item)
        print (data)
        return response(data=data)


class AlarmArea(Resource):

    def get(self):
        data = []

        objs = db.session.query(Device.province_name, func.Count(Alarm.id)).join(Alarm). \
            group_by(Device.province_name).all()
        objs = sorted(objs, key=lambda x: (x[1], x[0]), reverse=True)[:6]
        for obj in objs:
            data.append({"name": obj[0], "value": obj[1]})

        return response(data=data)


mod_api.add_resource(AlarmList, '/list/<device_id>')
mod_api.add_resource(AlarmHandle, '/handle/<alarm_id>')
mod_api.add_resource(AlarmLatest, '/latest/<device_id>')
mod_api.add_resource(AlarmLatestInfo, '/info/<device_id>')
mod_api.add_resource(AlarmCount, '/count')
mod_api.add_resource(AlarmItemCount, '/itemcount')
mod_api.add_resource(AlarmCarousel, '/carousel')
mod_api.add_resource(AlarmArea, '/area')
