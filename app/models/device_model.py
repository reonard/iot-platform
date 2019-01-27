from app import db
from marshmallow import Schema, fields
from sqlalchemy.orm.exc import NoResultFound


class DeviceModel(db.Model):

    __tablename__ = "t_device_model"

    name = db.Column(db.String(64), primary_key=True)
    description = db.Column(db.String(256))

    metrics = db.relationship("MetricConfig")

    def __str__(self):
        return self.name

    @classmethod
    def get_one_device_model(cls, device_model=None):

        try:
            device_model = DeviceModel.query.filter_by(name=device_model).one()
        except NoResultFound:
            print("Device  %s Not Found" % device_model)

        return device_model


class DeviceModelSchema(Schema):

    name = fields.Str()
    description = fields.Str()
