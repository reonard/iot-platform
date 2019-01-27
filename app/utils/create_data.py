from app import db


def db_data(app):

    with app.app_context():

        db.create_all()

