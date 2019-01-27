from app import db
from marshmallow import Schema, fields
from app.lib.const import CustomerType


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
    def viewable_projects(self):

        if not self.permission:
            return None

        if self.permission.customer.type == CustomerType.Vendor:
            return [obj.name for obj in self.permission.customer.children]

        if self.permission.customer.type == CustomerType.Project:
            return [self.permission.customer.name, ]

    @property
    def role(self):

        return self.permission.role.name


class UserSchema(Schema):

    name = fields.Str()
    description = fields.Str()
