import time
import datetime


def format_unixtime(unixtime, fmt=None):

    time_local = time.localtime(int(unixtime)/1000)
    if not fmt:
        fmt = "%Y-%m-%d %H:%M:%S"
    dt = time.strftime(fmt, time_local)
    return dt


def current_unixtime(timedelta):

    dt = datetime.datetime.now() + timedelta

    return time.mktime(dt.timetuple()) * 1000
