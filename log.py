import logging
from logging.handlers import RotatingFileHandler
import os

class log:
    logger = None
    _init=False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_instance'):
            cls._instance=super(log, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        try:
            if not self._init:
                path = os.path.join(os.getcwd(), 'config', 'log.txt')
                self.logger = logging.getLogger(__name__)
                self.logger.setLevel(logging.INFO)
                handler = RotatingFileHandler(filename=path, maxBytes=10*1024*1024, backupCount=3, encoding='utf-8')
                handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s: %(message)s'))
                self.logger.addHandler(handler)
                streamhandler = logging.StreamHandler()
                streamhandler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s: %(message)s'))
                self.logger.addHandler(streamhandler)
                self._init = True
        except Exception as reuslt:
            print(reuslt)
    
    def debug(message):
        log().logger.debug(message)

    def info(message):
        log().logger.info(message)

    def warn(message):
        log().logger.warn(message)

    def error(message):
        log().logger.error(message)
    
