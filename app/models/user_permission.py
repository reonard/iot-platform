from app import db
from marshmallow import Schema, fields


class UserPermission(db.Model):

    __tablename__ = "t_user_permission"

    user_id = db.Column(db.ForeignKey("t_user.id"), primary_key=True)
    customer_id = db.Column(db.ForeignKey("t_customer.id"))
    role_name = db.Column(db.ForeignKey("t_role.name"))

    role = db.relationship("Role", uselist=False)
    customer = db.relationship("Customer", uselist=False)

    def __repr__(self):
        return self.role.name