from app import db
from marshmallow import Schema, fields


class Project(db.Model):

    name = db.Column(db.String(128), primary_key=True)
    customer = db.Column(db.ForeignKey("customer.name"))
    description = db.Column(db.String(256))
    devices = db.relationship("Device")

    def __str__(self):
        return self.name


class ProjectSchema(Schema):

    name = fields.Str()
    description = fields.Str()
