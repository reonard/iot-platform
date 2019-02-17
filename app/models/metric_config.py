from app import db
from marshmallow import Schema, fields


class MetricConfig(db.Model):

    __tablename__ = "t_metric_config"

    metric_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    metric_key = db.Column(db.String(32))
    metric_status_key = db.Column(db.String(32))
    metric_alarm_config_key = db.Column(db.String(32))
    metric_display_name = db.Column(db.String(128))
    metric_type = db.Column(db.ForeignKey("t_metric_type.type_name"))
    device_model = db.Column(db.ForeignKey("t_device_model.name"))

    def __str__(self):
        return self.key


class MetricConfigSchema(Schema):

    metric_id = fields.Integer()
    metric_key = fields.Str()
    metric_alarm_config_key = fields.Str()
    metric_display_name = fields.Str()
    metric_unit = fields.Function(lambda obj: obj.type.type_unit)


