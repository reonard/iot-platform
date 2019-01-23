from app import db
from marshmallow import Schema, fields
from app.models.device import Device


class Alarm(db.Model):
    __tablename__ = 'alarm_item'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    device_id = db.Column(db.ForeignKey("device.device_id"))
    timestamp = db.Column(db.TIMESTAMP)
    alarm_item = db.Column(db.String(20))    #告警指标CSA。。
    alarm_value = db.Column(db.String(20))   #告警数值18
    device = db.relationship("Device")

    def __str__(self):
        return self.alarm_item

