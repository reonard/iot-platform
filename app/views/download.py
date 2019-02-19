from flask import send_file, send_from_directory, Blueprint
from flask_restful import Resource, Api
from app.lib.auth import check_login
import os
from flask import make_response

mod = Blueprint('download', __name__)
mod.before_request(check_login)
mod_api = Api(mod)


class DownTemplate(Resource):

    def get(self, filename):

        directory = os.getcwd()

        response = make_response(send_from_directory(os.path.join(directory, "app", "files"), filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
        return response


mod_api.add_resource(DownTemplate, '/<string:filename>')