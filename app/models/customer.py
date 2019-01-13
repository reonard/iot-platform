from app import db
from marshmallow import Schema, fields


class Customer(db.Model):

    name = db.Column(db.String(128), primary_key=True)
    description = db.Column(db.String(256))
    devices = db.relationship("Device")

    def __str__(self):
        return self.name


class CustomerSchema(Schema):

    name = fields.Str()
    description = fields.Str()
