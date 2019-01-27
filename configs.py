
LOGFILE = '/tmp/iot.log'

# DB Setting
MONGO_URI = 'mongodb://127.0.0.1:27017/pilot'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://a:b@localhost/iot?charset=utf8'
SQLALCHEMY_ECHO = False
HOST_URL = '127.0.0.1'

# Session Setting
SESSION_TYPE = "sqlalchemy"
SESSION_SQLALCHEMY_TABLE = 't_session'
SESSION_PERMANENT = True
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'x-token:'
PERMANENT_SESSION_LIFETIME = 3600
SESSION_COOKIE_NAME = 'x-token'
