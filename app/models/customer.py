from app import db
from marshmallow import Schema, fields
from sqlalchemy.orm import relationship


class Customer(db.Model):
    """
    合并project和customer
    """

    __tablename__ = "t_customer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    type = db.Column(db.String(64))
    parent_id = db.Column(db.ForeignKey("t_customer.id"))

    parent = relationship("Customer", lazy='joined', join_depth=1, remote_side=[id], uselist=False)
    children = relationship("Customer", lazy='joined', join_depth=1)

    user_permissions = relationship("UserPermission", lazy='joined')

    def __repr__(self):

        return self.name

    @staticmethod
    def get_project_by_name(name):
        project = Customer.query.filter_by(name = name).first()
        return project


class CustomerSchema(Schema):

    name = fields.Str()
    description = fields.Str()
