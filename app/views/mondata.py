from flask import Blueprint
from flask_restful import Resource, Api, reqparse
from app.models.device import Device
from app.models.device_model import DeviceModel
from app.utils.time_utils import format_unixtime, current_unixtime
from collections import defaultdict
from app.utils.http_utils import response
from app.lib.mongo import get_mongo_data
import datetime

mod = Blueprint('mondata', __name__)
mod_api = Api(mod)


class MonData(Resource):

    def get(self, device_id):

        parser = reqparse.RequestParser()
        parser.add_argument('metric_type', type=str)
        args = parser.parse_args()

        y_data, x_data = [], []

        dev = Device.query.filter_by(device_id=device_id).first()

        if not dev:
            return 'no such device found'

        metric_data = defaultdict(lambda: list())

        metric_configs = dev.metrics(args.get('metric_type'))

        for i in dev.mon_data():

            x_data.append(format_unixtime(int(i.get('timestamp'))))
            for mt in metric_configs:
                mon_data = i['data'][0].get(mt.metric_key, 0)
                metric_data[mt.metric_display_name].append(mon_data)

        for k, v in metric_data.items():
            y_data.append({'name': k, 'data': v})

        return response(data={'x_data': x_data, 'y_data': y_data})


class MonDataRealTime(Resource):

    def get(self, device_id):

        y_data, x_data = [], []

        dev = Device.query.filter_by(device_id=device_id).first()

        if not dev:
            return 'no such device found'

        metric_data = {}
        last_data = None

        metric_configs = dev.metrics()

        start_time = current_unixtime(datetime.timedelta(days=-300))

        for i in dev.mon_data(start=start_time, limit=12):

            x_data.append(format_unixtime(int(i.get('timestamp')), "%H:%M:%S"))

            last_data = i['data'][0]

            for mt in metric_configs:

                metric_type_name = mt.type.type_name

                mon_data = i['data'][0].get(mt.metric_key, 0)

                if metric_type_name not in metric_data:
                    metric_data[metric_type_name] = defaultdict(lambda: list())

                metric_data[metric_type_name][mt.metric_display_name].append(mon_data)

        for m_type, m_metric_configs in metric_data.items():

            m_type_data = {'name': m_type, 'legends': [], 'values': []}

            for metric, metric_data in m_metric_configs.items():
                m_type_data['legends'].append(metric)
                m_type_data['values'].append(metric_data)

            y_data.append(m_type_data)

        instrument = {"max": 1000, "rangeStart": 0.50, "data": []}

        if last_data:

            instrument["data"].append({
                "value": last_data.get('CA'),
                "name": "电流"
            })

        return response(data={'x_data': x_data, 'y_data': y_data, 'instrument': instrument})


class MonDataList(Resource):

    def get(self, device_model):

        tb_head = [{"label": "所属公司", "prop": "company"},
                   {"label": "网络状态", "prop": "network_status"},
                   {"label": "信号强度", "prop": "signal"}]

        dt = get_mongo_data(collection="last_metric", search={"device_model": device_model})

        dm = DeviceModel.get_one_device_model(device_model=device_model)

        if not dm:
            return response(code=404, error="设备类型不存在")

        for metric_config in dm.metrics:
            tb_head.append({"label": metric_config.metric_display_name,
                            "prop": metric_config.metric_key})

        tb_data_list = []
        for mon_data in dt:

            tb_data = dict()
            tb_data['company'] = mon_data.get('company')
            tb_data['network_status'] = mon_data.get('network_status')
            tb_data['signal'] = mon_data.get('signal')

            for metric_config in dm.metrics:
                m_key = metric_config.metric_key
                tb_data[m_key] = mon_data['data'][0].get(m_key)

            tb_data_list.append(tb_data)

        return response(data={
            "header": tb_head,
            "tableData": tb_data_list
        })


mod_api.add_resource(MonData, '/detail/<device_id>')
mod_api.add_resource(MonDataRealTime, '/realtime/<device_id>')
mod_api.add_resource(MonDataList, '/list/<device_model>')

