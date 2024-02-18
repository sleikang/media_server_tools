import logging
from logging.handlers import RotatingFileHandler
import os
from system.singleton import singleton


@singleton
class log(object):
    logger = None

    def __init__(self) -> None:
        try:
            path = os.path.join(os.getcwd(), "log", "log.txt")
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            handler = RotatingFileHandler(
                filename=path,
                maxBytes=10 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            handler.setFormatter(
                logging.Formatter("%(asctime)s\t%(levelname)s: %(message)s")
            )
            self.logger.addHandler(handler)
            streamhandler = logging.StreamHandler()
            streamhandler.setFormatter(
                logging.Formatter("%(asctime)s\t%(levelname)s: %(message)s")
            )
            self.logger.addHandler(streamhandler)
        except Exception as result:
            print(result)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)
