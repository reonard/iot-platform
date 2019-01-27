from app import db


class Alarm(db.Model):

    __tablename__ = 't_alarm_item'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    device_id = db.Column(db.ForeignKey("t_device.device_id"))
    timestamp = db.Column(db.TIMESTAMP)
    alarm_item = db.Column(db.String(20))
    alarm_value = db.Column(db.String(20))
    device = db.relationship("Device")

    def __str__(self):
        return self.alarm_item

