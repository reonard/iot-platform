from app import db
from marshmallow import Schema, fields
from app.lib.const import CustomerType
from app.models.customer import Customer

class User(db.Model):

    __tablename__ = "t_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(255))
    password = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)

    permission = db.relationship("UserPermission", uselist=False)

    @classmethod
    def get_user_info(cls, **kwargs):

        return db.session.query(User).filter_by(**kwargs).first()

    def __str__(self):
        return self.name

    @property
    def customer(self):

        return self.permission.customer

    @property
    def viewable_projects(self):

        if not self.permission:
            return None

        if self.permission.customer.type == CustomerType.Super:
            return [obj.name for obj in Customer.query.filter_by(type=CustomerType.Project)]

        if self.permission.customer.type == CustomerType.Vendor:
            return [obj.name for obj in Customer.query.filter_by(type=CustomerType.Project,
                                                                 parent=self.permission.customer)]

        if self.permission.customer.type == CustomerType.Project:
            return [self.permission.customer.name, ]

    @property
    def role(self):

        return self.permission.role.name


class UserSchema(Schema):

    name = fields.Str()
    description = fields.Str()


# def get_all_children(customer):
#     """
#     递归查询，支持无限层级，但是效率堪忧。。。
#     :param customer:
#     :return:
#     """
#
#     children = []
#
#     if customer.children:
#
#         for i in [get_all_children(c) for c in customer.children]:
#             children.extend(i)
#
#         return children
#     else:
#
#         return [customer.name, ]
