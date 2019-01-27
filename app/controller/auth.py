from flask import session, current_app
from app.models.user import User
from itsdangerous import want_bytes


def login_user(user_email, password):

    session_id = None

    user_info = User.get_user_info(email=user_email)

    if user_info and user_info.password == password:
        session['user_id'] = user_info.id

        if current_app.session_interface.use_signer:
            session_id = current_app.session_interface._get_signer(current_app).sign(want_bytes(session.sid))
        else:
            session_id = session.sid
    else:
        session.clear()

    return session_id


def logout_user():

    session.clear()
