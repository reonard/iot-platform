from app import db


class MetricType(db.Model):

    __tablename__ = "t_metric_type"

    type_name = db.Column(db.String(64), primary_key=True)
    type_description = db.Column(db.String(128))
    type_unit = db.Column(db.String(64))
    metrics = db.relationship("MetricConfig", backref="type", lazy="joined")

    def __str__(self):
        return self.type_name
