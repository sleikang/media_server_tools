import requests
import json

class tmdb:
    host = None
    key = None
    err = None

    def __init__(self, key : str) -> None:
        self.host = 'https://api.themoviedb.org/3'
        self.key = key

    """
    获取电影信息
    :param movieid
    :return True or False, iteminfo
    """
    def getmoveinfo(self, movieid : str, language : str = 'zh-CN'):
        iteminfo = {}
        try:
            url = '{}/movie/{}?api_key={}&language={}&append_to_response=alternative_titles'.format(self.host, movieid, self.key, language)
            p = requests.get(url)
            if p.status_code != 200:
                self.err = p.text
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    """
    获取tv信息
    :param tvid
    :return True or False, iteminfo
    """
    def gettvinfo(self, tvid : str, language : str = 'zh-CN'):
        iteminfo = {}
        try:
            url = '{}/tv/{}?api_key={}&language={}&append_to_response=alternative_titles'.format(self.host, tvid, self.key, language)
            p = requests.get(url)
            if p.status_code != 200:
                self.err = p.text
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo
    
    """
    获取人物信息
    :param personid 人物ID
    :return True or False, personinfo
    """
    def getpersoninfo(self, personid : str, language : str = 'zh-CN'):
        personinfo = {}
        try:
            url = '{}/person/{}?api_key={}&language={}&append_to_response=alternative_titles'.format(self.host, personid, self.key, language)
            p = requests.get(url)
            if p.status_code != 200:
                self.err = p.text
                return False, personinfo
            personinfo = json.loads(p.text)
            return True, personinfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, personinfo