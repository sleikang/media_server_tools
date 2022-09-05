import time
from media import media
import yaml
import os
from log import log


if __name__ == '__main__':
    try:
        path = os.path.join(os.getcwd(), 'config', 'config.yaml')
        # 打开文件
        file = open(path, "r", encoding="utf-8")
        if file:
            config_data = yaml.load(file,Loader=yaml.FullLoader)
        if not config_data:
            log.info('打开配置文件[{}]失败'.format(path))
        else:
            system_config = config_data['system']
            mediaclient = media(embyhost=system_config['embyhost'], embyuserid=system_config['embyuserid'], embykey=system_config['embykey'], tmdbkey=system_config['tmdbkey'], doubankey=system_config['doubankey'], threadnum=system_config['threadnum'], updatepeople=system_config['updatepeople'], updateoverview=system_config['updateoverview'])
            while True:
                try:
                    log.info('开始刷新媒体库元数据')
                    mediaclient.start_scan_media()
                    log.info('刷新媒体库元数据完成')
                    time.sleep(system_config['updatetime'] * 3600)
                except Exception as reuslt:
                    log.info(reuslt)
    except Exception as reuslt:
        log.info(reuslt)