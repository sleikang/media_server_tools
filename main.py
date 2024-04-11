import os
import time
import shutil
from media import media
from system.config import config
from system.log import log

if __name__ == "__main__":
    try:
        if not os.path.exists(os.path.join(os.getcwd(), "config", "config.yaml")):
            log().logger.info(
                "配置文件不存在, 拷贝默认配置文件[config.default.yaml]->[/config/config.yaml]"
            )
            shutil.copy("config.default.yaml", "config/config.yaml")

        if not os.path.exists(
            os.path.join(os.getcwd(), "config", "config.default.yaml")
        ):
            log().logger.info(
                "默认配置文件不存在, 拷贝默认配置文件[config.default.yaml]->[/config/config.default.yaml]"
            )
            shutil.copy("config.default.yaml", "config/config.default.yaml")

        path = os.path.join(os.getcwd(), "config", "config.yaml")
        configinfo = config(path=path)
        mediaclient = media(configinfo=configinfo)
        while True:
            try:
                log().logger.info("开始刷新媒体库元数据")
                mediaclient.start_scan_media()
                log().logger.info("刷新媒体库元数据完成")
                time.sleep(configinfo.systemdata["updatetime"] * 3600)
            except Exception as result:
                log().logger.info(result)
    except Exception as result:
        log().logger.info(
            "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        )
