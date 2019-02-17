from flask import Blueprint
from flask_restful import Resource, Api
from app.models import DeviceModel
from app.models.metric_config import MetricConfigSchema
from app.utils.http_utils import obj_response, response
from app.lib.auth import check_login


mod = Blueprint('device_config', __name__)
mod.before_request(check_login)
mod_api = Api(mod)


class DeviceConfig(Resource):

    def get(self, model):

        device_model = DeviceModel.query.filter_by(name=model).first()

        if device_model:

            return obj_response(data=device_model.metrics,
                                schema=MetricConfigSchema(), many=True)
        else:

            return response(error="no model found")


mod_api.add_resource(DeviceConfig, '/metric/<string:model>')
