import yaml
from system.log import log
import os

class config:
    path = None
    configdata = None
    apidata = None
    systemdata = None

    def __init__(self, path : str) -> None:
        try:
            # 打开文件
            self.path = path
            if not os.path.exists(path=self.path):
                log().info('配置文件[{}]不存在, 开始生成默认配置文件'.format(self.path))
                file = open(self.path, "w", encoding="utf-8")
                data = {'api':{'nastools':{'host':'http://127.0.0.1:3000', 'username':'', 'passwd':''},'emby':{'host':'http://127.0.0.1:8096', 'userid':'', 'key':''},'jellyfin':{'host':'http://127.0.0.1:8096', 'userid':'', 'key':''},'tmdb':{'key':'', 'mediacachefailtime':1, 'peoplecachefailtime':10},'douban':{'key':'0ac44ae016490db2204ce0a042db2916', 'cookie':'', 'mediacachefailtime':1, 'peoplecachefailtime':10}}, 'system':{'threadnum':1, 'updatepeople':True, 'updateoverview':True, 'updateseasongroup':False, 'updatetime':1, 'taskdonespace':1, 'delnotimagepeople':False, 'checkmediasearch': False, 'seasongroup':['纸房子|62ed7ac87d5504007e4ab046']}}
                yaml.dump(data=data, stream=file)
                log().info('生成默认配置文件[{}]完成'.format(self.path))
                file.close()
            file = open(self.path, "r", encoding="utf-8")
            self.configdata = yaml.load(file, Loader=yaml.FullLoader)
            self.systemdata = self.configdata['system']
            self.apidata = self.configdata['api']

            self.__config_check__(self.apidata['nastools'], 'host', 'http://127.0.0.1:3000')
            self.__config_check__(self.apidata['nastools'], 'username', '')
            self.__config_check__(self.apidata['nastools'], 'passwd', '')
            self.__config_check__(self.apidata['emby'], 'host', 'http://127.0.0.1:8096')
            self.__config_check__(self.apidata['emby'], 'userid', '')
            self.__config_check__(self.apidata['emby'], 'key', '')
            self.__config_check__(self.apidata['jellyfin'], 'host', 'http://127.0.0.1:8096')
            self.__config_check__(self.apidata['jellyfin'], 'userid', '')
            self.__config_check__(self.apidata['jellyfin'], 'key', '')
            self.__config_check__(self.apidata['tmdb'], 'key', '')
            self.__config_check__(self.apidata['tmdb'], 'mediacachefailtime', 1)
            self.__config_check__(self.apidata['tmdb'], 'peoplecachefailtime', 10)
            self.__config_check__(self.apidata['douban'], 'key', '0ac44ae016490db2204ce0a042db2916')
            self.__config_check__(self.apidata['douban'], 'cookie', '')
            self.__config_check__(self.apidata['douban'], 'mediacachefailtime', 1)
            self.__config_check__(self.apidata['douban'], 'peoplecachefailtime', 10)
            self.__config_check__(self.systemdata, 'mediaserver', 'Emby')
            self.__config_check__(self.systemdata, 'threadnum', 1)
            self.__config_check__(self.systemdata, 'updatepeople', True)
            self.__config_check__(self.systemdata, 'updateoverview', True)
            self.__config_check__(self.systemdata, 'updateseasongroup', False)
            self.__config_check__(self.systemdata, 'updatetime', 1)
            self.__config_check__(self.systemdata, 'taskdonespace', 1)
            self.__config_check__(self.systemdata, 'delnotimagepeople', False)
            self.__config_check__(self.systemdata, 'checkmediasearch', False)
            self.__config_check__(self.systemdata, 'seasongroup', ['纸房子|5eb730dfca7ec6001f7beb51'])
        except Exception as reuslt:
            log().info('配置异常错误, {}'.format(reuslt))


    def __config_check__(self, config, key, defaultvalue):
        try:
            if key not in config:
                log().info('配置项[{}]不存在, 创建默认值[{}]'.format(key, defaultvalue))
                config[key] = defaultvalue
                with open(file=self.path, mode='w') as file:
                    yaml.safe_dump(self.configdata, file, default_flow_style=False)
        except Exception as reuslt:
            log().info('配置异常错误, {}'.format(reuslt))