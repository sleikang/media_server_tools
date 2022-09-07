import requests
import json
import html2text
import re

class douban:
    host = None
    key = None
    useragent = None
    headers = None
    err = None

    def __init__(self, key : str) -> None:
        self.host = 'https://frodo.douban.com/api/v2'
        self.key = key
        self.useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.27(0x18001b33) NetType/WIFI Language/zh_CN'
        self.headers = {'User-Agent':self.useragent, 'Referer': 'https://servicewechat.com/wx2f9b06c1de1ccfca/85/page-frame.html', 'content-type': 'application/json', 'Authorization': 'Bearer 4c287a1f8cbc64b3e4796e5ea6352e19', 'Connection': 'keep-alive'}

    def get_movie_info(self, movieid : str):
        """
        获取电影信息
        :param movieid 电影ID
        """
        iteminfo = {}
        try:
            url = '{}/movie/{}?apikey={}'.format(self.host, movieid, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            url = iteminfo['info_url']
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            text = html2text.html2text(html=p.text)
            text = text.replace('/\n', '/ ').replace('# 影片信息\n\n', '')
            infolist = re.findall(pattern='([\s\S]+?)\s*\|\s*([\s\S]+?)\n', string=text)
            iteminfo['info'] = {}
            for info in infolist:
                if info[0] == '---':
                    continue
                valuelist = info[1].split(' / ')
                if len(valuelist) > 1:
                    iteminfo['info'][info[0]] = []
                    for value in valuelist:
                        iteminfo['info'][info[0]].append(re.sub(pattern='\s+', repl='', string=value))
                else:
                    iteminfo['info'][info[0]] = re.sub(pattern='\s+', repl='', string=info[1])
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def get_movie_celebrities_info(self, movieid : str):
        """
        获取演员信息
        :param movieid 电影ID
        """
        iteminfo = {}
        try:
            url = '{}/movie/{}/celebrities?apikey={}'.format(self.host, movieid, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def get_tv_info(self, tvid : str):
        """
        获取电视剧信息
        :param tvid 电影ID
        """
        iteminfo = {}
        try:
            url = '{}/tv/{}?apikey={}'.format(self.host, tvid, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            url = iteminfo['info_url']
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            text = html2text.html2text(html=p.text)
            text = text.replace('/\n', '/ ').replace('# 影片信息\n\n', '')
            infolist = re.findall(pattern='([\s\S]+?)\s*\|\s*([\s\S]+?)\n', string=text)
            iteminfo['info'] = {}
            for info in infolist:
                if info[0] == '---':
                    continue
                valuelist = info[1].split(' / ')
                if len(valuelist) > 1:
                    iteminfo['info'][info[0]] = []
                    for value in valuelist:
                        iteminfo['info'][info[0]].append(re.sub(pattern='\s+', repl='', string=value))
                else:
                    iteminfo['info'][info[0]] = re.sub(pattern='\s+', repl='', string=info[1])
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def get_tv_celebrities_info(self, tvid : str):
        """
        获取演员信息
        :param tvid 电影ID
        """
        iteminfo = {}
        try:
            url = '{}/tv/{}/celebrities?apikey={}'.format(self.host, tvid, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def get_celebrity_info(self, celebrityid : str):
        """
        获取人物信息
        :param celebrityid 人物ID
        :param True of False, celebrityinfo
        """
        iteminfo = {}
        try:
            url = '{}/celebrity/{}?apikey={}'.format(self.host, celebrityid, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def search_movie(self, title : str):
        """
        搜索电影信息
        :param title 标题
        """
        iteminfo = {}
        try:
            url = '{}/search/movie?q={}&start=0&count=2&apikey={}'.format(self.host, title, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def search_media(self, title : str):
        """
        搜索媒体信息
        :param title 标题
        """
        iteminfo = {}
        try:
            url = '{}/search/weixin?q={}&start=0&count=3&apikey={}'.format(self.host, title, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = json.loads(p.text)['localized_message']
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo