from app import db


class MetricStatusConfig(db.Model):

    __tablename__ = "t_metric_status_config"

    metric_id = db.Column(db.ForeignKey("t_metric_config.metric_id"))
    metric_status_value = db.Column(db.Integer)
    metric_status_description = db.Column(db.String(64))

    def __str__(self):
        return self.metric_status_value


