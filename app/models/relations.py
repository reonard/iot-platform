from app import db


# class DeviceModelMetricConfig(db.Model):
#     device_model_name = db.Column(db.ForeignKey('device_model.name'))
#     metric_config_id = db.Column(db.ForeignKey('metric_config.metric_id'))

# device_model_metric = db.Table(
#     'device_model_metric',
#     db.Column('device_model', db.String(64), db.ForeignKey('device_model.name'), primary_key=True),
#     db.Column('metric_config', db.Integer, db.ForeignKey('metric_config.metric_id'), primary_key=True)
# )
