import yaml
from log import log

class config:
    configdata = None
    systemdata = None

    def __init__(self, path : str) -> None:
        try:
            # 打开文件
            file = open(path, "r", encoding="utf-8")
            if file:
                self.configdata = yaml.load(file,Loader=yaml.FullLoader)
            if not self.configdata:
                log.info('打开配置文件[{}]失败'.format(path))
            self.systemdata = self.configdata['system']
        except Exception as reuslt:
            log.info('配置异常错误, {}'.format(reuslt))