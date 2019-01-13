import sys
import logging
import logging.handlers


class Logger:

    info, error, debug = None, None, None

    @classmethod
    def init(cls, app, log_level):

        logfile_handler = logging.handlers.TimedRotatingFileHandler(
            app.config.get("LOGFILE"), "midnight", 1, 30
        )
        stdout_handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter('%(asctime)12s %(filename)s[line:%(lineno)4d] [%(levelname)s]: %(message)s')
        logfile_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)

        logger = logging.getLogger('mylog')
        logger.addHandler(logfile_handler)
        logger.addHandler(stdout_handler)
        logger.setLevel(log_level)

        cls.info = logger.info
        cls.error = logger.error
        cls.debug = logger.debug
