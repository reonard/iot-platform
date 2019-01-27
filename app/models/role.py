from app import db


class Role(db.Model):

    __tablename__ = "t_role"

    name = db.Column(db.String(32), primary_key=True)
    description = db.Column(db.String(128))

    def __repr__(self):
        return self.name

