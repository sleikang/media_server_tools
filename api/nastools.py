import json
from urllib import parse

from api.network import network


class nastools:
    client = None
    host = None
    username = None
    passwd = None
    headers = None
    token = None
    err = None

    def __init__(self, host : str, username : str, passwd : str) -> None:
        self.client = network(maxnumconnect=10, maxnumcache=20)
        self.host = host
        self.username = username
        self.passwd = passwd
        self.headers = {'accept':'application/json', 'Content-Type':'application/x-www-form-urlencoded'}

    def name_test(self, name):
        """
        名称识别测试
        :param name 媒体名称
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            if not self.__login__():
                return False
            url = "{}/api/v1/service/name/test".format(self.host)
            data = "name={}".format(parse.quote(name))
            p, err = self.client.post(url=url, data=data, headers=self.headers)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)['data']['data']
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False, iteminfo
    
    def media_info(self, name, year = None, type = 'MOV'):
        """
        媒体识别
        :param name 媒体名称
        :param year 年代
        :param type 媒体类型 电影MOV 剧集TV
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            if not self.__login__():
                return False, iteminfo
            url = "{}/api/v1/media/info".format(self.host)
            if year:
                data = "type={}&title={}&year=".format(type, parse.quote(name), year)
            else:
                data = "type={}&title={}".format(type, parse.quote(name))
            p, err = self.client.post(url=url, data=data, headers=self.headers)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)['data']
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False, iteminfo

    def __login__(self):
        try:
            if self.token:
                url = "{}/api/v1/user/info".format(self.host)
                data = "username={}".format(self.username, self.passwd)
                p, err = self.client.post(url=url, data=data, headers=self.headers)
                if self.__get_status__(p=p, err=err):
                    return True
            url = "{}/api/v1/user/login".format(self.host)
            data = "username={}&password={}".format(self.username, self.passwd)
            p, err = self.client.post(url=url, data=data, headers=self.headers)
            if not self.__get_status__(p=p, err=err):
                return False
            rootobject = json.loads(p.text)
            self.token = rootobject['data']['token']
            self.headers['Authorization'] = self.token
            return True
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False

    def __get_status__(self, p, err):
        try:
            if p == None:
                self.err = err
                return False
            if p.status_code != 200:
                self.err = p.text
                return False
            rootobject = json.loads(p.text)
            if rootobject['code'] != 0:
                self.err = rootobject['message']
                return False
            return True
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        
        return False

    