from app import db
from marshmallow import Schema, fields
import datetime
import hashlib

class Config(db.Model):
    __tablename__ = "t_device_config"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    configs = db.Column(db.Text)
    version = db.Column(db.String(32))

    create_time = db.Column(db.TIMESTAMP)
    hash = db.Column(db.String(32))
    devices = db.relationship("Device")

    @staticmethod
    def create_device_config(msg):
        now = datetime.datetime.now()
        hash = hashlib.md5(msg.encode("utf8")).hexdigest()
        config = Config.query.filter_by(hash = hash).first()
        if config:
            return config

        config = Config(configs=msg, create_time=now, version=now.strftime("%Y%m%d%H%M%S"), hash = hash)
        db.session.add(config)
        db.session.commit()
        return config

class IssueMsg(db.Model):
    __tablename__ = "t_issue_msg"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_type = db.Column(db.Enum("push","reset","check","config"))
    config = db.Column(db.ForeignKey("t_device_config.id"))
    created_by = db.Column(db.ForeignKey("t_user.id"))
    statuss = db.relationship("IssueStatus")

    @staticmethod
    def create_issue_msg(config_id, action_type, user_id):
        issuemsg = IssueMsg(config=config_id, action_type=action_type, created_by=user_id)
        db.session.add(issuemsg)
        db.session.commit()
        return issuemsg

class IssueMsgSchema(Schema):
    id = fields.String()
    action_type = fields.String()
    config = fields.String()
    created_by = fields.String()


class IssueStatus(db.Model):
    __tablename__ = "t_issue_status"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.ForeignKey("t_device.device_id"))
    issue_msg_id = db.Column(db.ForeignKey("t_issue_msg.id"))
    issue_status = db.Column(db.Integer, index=True)
    status_time = db.Column(db.TIMESTAMP)
    create_time =  db.Column(db.TIMESTAMP, nullable = False)

    @staticmethod
    def create_device_config(device_id, issue_msg_id):
        now = datetime.datetime.now()
        status = IssueStatus(device_id = device_id, issue_msg_id = issue_msg_id, issue_status=0, create_time=now)
        db.session.add(status)
        db.session.commit()
        return status

class IssueStatusSchema(Schema):
    id = fields.String()
    device_id = fields.String()
    issue_msg_id = fields.String()
    issue_status = fields.String()
    status_time = fields.Date()
    create_time = fields.Date()

if __name__ == '__main__':

    from app import create_app, db

    app = create_app()
    with app.app_context():
        dev = Device.query.filter_by(device_id='device1').first()
