from flask import Blueprint, request
from flask_restful import Resource, Api
from app.utils.http_utils import obj_response, response
from app.lib.auth import current_user_info, check_login
from app.models.customer import CustomerSchema
from app.models.user import UserSchema, User
from app.models.user_permission import UserPermission
from app.lib.message import ResponseCode

mod = Blueprint('customer', __name__)
mod.before_request(check_login)
mod_api = Api(mod)


class CustomerList(Resource):

    def get(self):
        """
        有点绕，后面优化
        :return:
        """
        parent_hierarchy = request.args.getlist("hierarchy")

        children = current_user_info.customer

        if not parent_hierarchy:
            return obj_response([children], schema=CustomerSchema(), many=True)

        for p in parent_hierarchy:

            if children and children.id == int(p):
                continue

            if not hasattr(children, "children"):
                break

            children = getattr(children, "children").filter_by(id=p).first()

        data = children.children if hasattr(children, "children") else []

        return obj_response(data, schema=CustomerSchema(), many=True)


class CustomerUser(Resource):

    def get(self, cid):

        if not current_user_info.role_for(cid):
            return response(error="没有权限查看", biz_code=ResponseCode.ERROR_NO_AUTH)

        users = User.query.join(UserPermission).filter(UserPermission.customer_id == cid)

        return obj_response(data=users, schema=UserSchema(), many=True)


class CustomerProject(Resource):

    def get(self):

        viewable_projects = current_user_info.viewable_projects

        return response(data=viewable_projects)


mod_api.add_resource(CustomerList, '/list/')
mod_api.add_resource(CustomerUser, '/user/<int:cid>')
mod_api.add_resource(CustomerProject, '/project/')
