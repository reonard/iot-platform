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
    openid = db.Column(db.String(255), default="")

    permission = db.relationship("UserPermission", lazy="joined", uselist=False)
    issue_version = db.relationship("IssueMsg", backref="user", lazy="joined")
    configs = db.relationship("DeviceConfig", backref="user", lazy="joined")

    @classmethod
    def get_user_info(cls, **kwargs):

        return db.session.query(User).filter_by(**kwargs).first()

    def __str__(self):
        return self.name

    @property
    def customer(self):

        return self.permission.customer

    @property
    def is_super(self):

        return self.permission.customer.type == CustomerType.Super

    @property
    def is_vendor(self):

        return self.permission.customer.type == CustomerType.Vendor

    @property
    def is_project(self):

        return self.permission.customer.type == CustomerType.Vendor

    @property
    def viewable_projects(self):

        if not self.permission:
            return None

        # 先不用get_children的递归方法
        if self.is_super:
            return [obj.name for obj in Customer.query.filter_by(type=CustomerType.Project)]

        elif self.is_vendor:
            return [obj.name for obj in Customer.query.filter_by(type=CustomerType.Project,
                                                                 parent=self.permission.customer)]
        elif self.is_project:
            return [self.permission.customer.name, ]

    @property
    def viewable_projects_id(self):

        if not self.permission:
            return None

        if self.is_super:
            return [obj.id for obj in Customer.query.filter_by(type=CustomerType.Project)]

        elif self.is_vendor:
            return [obj.id for obj in Customer.query.filter_by(type=CustomerType.Project,
                                                                   parent=self.permission.customer)]
        elif self.is_project:
            return [self.permission.customer.id, ]

    @property
    def role(self):

        return self.permission.role.name

    def role_for(self, customer_id):

        if self.is_super:
            return self.role

        customer = search_customer(self.customer, customer_id)
        if customer:
            return self.role

        return None

    @staticmethod
    def update_user_info(q, v):
        flag = User.query.filter_by(**q).update(v)
        db.session.commit()
        return flag


class UserSchema(Schema):

    name = fields.Str()
    phone = fields.Str()
    email = fields.Str()
    description = fields.Str()
    role = fields.Function(lambda obj: obj.role, dump_only=True)


def get_children(customer):
    """
    递归查询customer下的所有叶节点（项目），支持无限层级，但是效率可能一般。。。
    :param customer:
    :return:
    """

    children = []

    if hasattr(customer, "children"):

        for i in [get_children(c) for c in customer.children]:
            children.extend(i)

        return children
    else:

        return [customer.name, ]


def search_customer(start_customer, customer_id):
    """
    递归查询start_customer下是否有customer_id，支持无限层级，但是效率可能一般。。。
    :param start_customer:
    :param customer_id:
    :return:
    """

    if start_customer.id == customer_id:
        return start_customer

    if start_customer.children:
        for i in start_customer.children:
            if search_customer(i, customer_id):
                return i
    else:
        return None
