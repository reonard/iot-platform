from app import db
from marshmallow import Schema, fields


class Alarm(db.Model):

    deviceid = db.Column(db.ForeignKey("device.device_id"))
    timestamp = db.Column(db.TIMESTAMP)
    alarmhandlestatus = db.Column(db.INTEGER) #告警处理状态
    alarmsendstatus = db.Column(db.INTEGER)  # 告警发送状态0 未发送   1已发送
    alarmdescription = db.Column(db.String(500))
    alarm_item = db.Column(db.String(20))    #告警指标CSA。。
    alarm_value = db.Column(db.String(20))   #告警数值18
    project = db.Column(db.String(20))
    customer = db.Column(db.String(20))

    def __str__(self):
        return self.alarmdescription

