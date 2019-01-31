from app import db
from app.utils.collection_mapping import get_collection
from marshmallow import Schema, fields
from app.lib.mongo import get_mongo_data
from app.lib.const import MONGO_ALARM_COLLECTION, MONGO_ORDER_DESC, MONGO_ORDER_ASC
from sqlalchemy.orm.exc import NoResultFound
import datetime


class Device(db.Model):
    '''
    CREATE TABLE `t_device` (
  `device_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `device_model` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `device_sim` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `project` int(11) DEFAULT NULL,
  `config_id` int(11) DEFAULT NULL,
  `secret` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mongo_slice` int(11) DEFAULT NULL,
  `longitude` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `latitude` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `registry_time` timestamp NULL DEFAULT NULL,
  `network_status` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `device_status` int(11) DEFAULT NULL,
  `status_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`device_id`),
  UNIQUE KEY `device_sim` (`device_sim`),
  KEY `device_model` (`device_model`),
  KEY `project` (`project`),
  KEY `config_id` (`config_id`),
  CONSTRAINT `t_device_ibfk_1` FOREIGN KEY (`device_model`) REFERENCES `t_device_model` (`name`),
  CONSTRAINT `t_device_ibfk_2` FOREIGN KEY (`project`) REFERENCES `t_customer` (`id`),
  CONSTRAINT `t_device_ibfk_3` FOREIGN KEY (`config_id`) REFERENCES `t_device_config` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
    '''

    __tablename__ = "t_device"

    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_name = db.Column(db.String(128))
    device_model = db.Column(db.ForeignKey("t_device_model.name"))
    device_sim = db.Column(db.String(128), unique=True)
    model = db.relationship("DeviceModel")
    project = db.Column(db.ForeignKey("t_customer.id"))
    secret = db.Column(db.String(128))
    mongo_slice = db.Column(db.INTEGER)
    longitude = db.Column(db.String(32))
    latitude = db.Column(db.String(32))
    location = db.Column(db.String(256))
    registry_time = db.Column(db.TIMESTAMP)
    network_status = db.Column(db.String(64))
    device_status = db.Column(db.INTEGER)
    status_time = db.Column(db.TIMESTAMP)
    config_id = db.Column(db.ForeignKey("t_device_config.id"))

    def __str__(self):
        return self.device_id

    def metrics(self, metric_type=None):

        if not metric_type:
            return self.model.metrics

        return [mt for mt in self.model.metrics if mt.metric_type == metric_type]

    @property
    def metric_types(self):

        metric_types = []

        for mt in self.model.metrics:

            if mt.metric_type not in metric_types:
                metric_types.append(mt.metric_type)

        return metric_types

    def mon_data(self, start=None, end=None, interval=None, limit=None, **search):

        criteria = search if search else {}
        criteria["deviceid"] = self.device_id

        res = get_mongo_data(collection=get_collection(interval),
                             search=criteria,
                             start=start,
                             end=end,
                             limit=limit,
                             order=[('timestamp', MONGO_ORDER_DESC)])

        res.reverse()

        return res

    def last_mon_data(self):

        criteria = {"deviceid": self.device_id}

        res = get_mongo_data(collection="last_metric",
                             search=criteria,
                             limit=1,
                             order=[('timestamp', MONGO_ORDER_ASC)])
        if res:
            return res[0]

    def alarm_data(self, start=None, end=None, **search):

        criteria = search if search else {}
        criteria["deviceid"] = self.device_id

        res = get_mongo_data(collection=MONGO_ALARM_COLLECTION,
                             search=criteria,
                             start=start,
                             end=end,
                             order=[('timestamp', MONGO_ORDER_DESC)])
        return res

    def latest_alarm(self):

        criteria = {"deviceid": self.device_id}

        res = get_mongo_data(collection=MONGO_ALARM_COLLECTION,
                             search=criteria,
                             limit=1, order=[('timestamp', MONGO_ORDER_DESC)])

        if res:
            return res[0]

        return None

    @classmethod
    def get_one_device(cls, device_id):

        device = None

        try:
            device = Device.query.filter_by(device_id=device_id).one()
        except NoResultFound:
            print("Device  %d Not Found", device_id)

        return device

    @staticmethod
    def get_more_device(project):

        devices = []

        try:
            devices = Device.query.filter_by(project=project).all()
        except NoResultFound:
            print("Project %s device Not Found", project)

        return devices

    @staticmethod
    def create_device(device_sim, device_model, project):

        device = Device(
            device_name='未命名设备',
            device_model=device_model,
            device_sim=device_sim,
            secret="12345",
            registry_time=datetime.datetime.now(),
            location="",
            longitude="",
            latitude="",
            project=project,
            mongo_slice=0,
            network_status='online',
            device_status=0,
            status_time=datetime.datetime.now()
        )

        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def update_device(q, v):
        flag = Device.query.filter_by(**q).update(v)
        db.session.commit()
        return flag


class DeviceSchema(Schema):

    device_id = fields.String()
    device_name = fields.String()
    device_model = fields.String()
    project = fields.String()
    secret = fields.String()
    longitude = fields.String()
    latitude = fields.String()
    location = fields.String()
    registry_time = fields.DateTime()
    device_status = fields.String()
    network_status = fields.String()
    metric_types = fields.List(fields.String())
    status_time = fields.DateTime()
    config_id = fields.String()


if __name__ == '__main__':

    from app import create_app, db
    app = create_app()
    with app.app_context():
        dev = Device.query.filter_by(device_id='device1').first()
