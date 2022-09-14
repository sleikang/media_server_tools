import yaml
from log import log
import os

class config:
    path = None
    configdata = None
    systemdata = None

    def __init__(self, path : str) -> None:
        try:
            # 打开文件
            self.path = path
            if not os.path.exists(path=self.path):
                log.info('配置文件[{}]不存在, 开始生成默认配置文件'.format(self.path))
                file = open(self.path, "w", encoding="utf-8")
                data = {'system':{'embyhost':'', 'embyuserid':'', 'embykey':'', 'tmdbkey':'', 'doubankey':'0ac44ae016490db2204ce0a042db2916', 'doubancookie':'', 'threadnum':1, 'updatepeople':True, 'updateoverview':True, 'updateseasongroup':False, 'updatetime':1, 'taskdonespace':1, 'delnotimagepeople':False, 'tmdbmediacachefailtime':1, 'tmdbpeoplecachefailtime':10, 'doubanmediacachefailtime':30, 'doubanpeoplecachefailtime':120, 'seasongroup':['纸房子|62ed7ac87d5504007e4ab046']}}
                yaml.dump(data=data, stream=file)
                log.info('生成默认配置文件[{}]完成'.format(self.path))
                file.close()
            file = open(self.path, "r", encoding="utf-8")
            self.configdata = yaml.load(file, Loader=yaml.FullLoader)
            self.systemdata = self.configdata['system']

            self.__config_check__('embyhost', '')
            self.__config_check__('embyuserid', '')
            self.__config_check__('embykey', '')
            self.__config_check__('tmdbkey', '')
            self.__config_check__('doubankey', '0ac44ae016490db2204ce0a042db2916')
            self.__config_check__('doubancookie', '')
            self.__config_check__('threadnum', 1)
            self.__config_check__('updatepeople', True)
            self.__config_check__('updateoverview', True)
            self.__config_check__('updateseasongroup', False)
            self.__config_check__('updatetime', 1)
            self.__config_check__('taskdonespace', 1)
            self.__config_check__('delnotimagepeople', False)
            self.__config_check__('tmdbmediacachefailtime', 1)
            self.__config_check__('tmdbpeoplecachefailtime', 10)
            self.__config_check__('doubanmediacachefailtime', 30)
            self.__config_check__('doubanpeoplecachefailtime', 120)
            self.__config_check__('seasongroup', ['纸房子|62ed7ac87d5504007e4ab046'])
        except Exception as reuslt:
            log.info('配置异常错误, {}'.format(reuslt))


    def __config_check__(self, key, defaultvalue):
        try:
            if key not in self.systemdata:
                log.info('配置项[{}]不存在, 创建默认值[{}]'.format(key, defaultvalue))
                self.systemdata[key] = defaultvalue
                with open(file=self.path, mode='w') as file:
                    yaml.safe_dump(self.configdata, file, default_flow_style=False)
        except Exception as reuslt:
            log.info('配置异常错误, {}'.format(reuslt))