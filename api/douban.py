import json
import re

import html2text

from network.network import Network


class douban:
    host = None
    key = None
    mobileheaders = None
    pcheaders = None
    cookie = None
    client = None
    err = None

    def __init__(self, key: str, cookie: str) -> None:
        self.host = "https://frodo.douban.com/api/v2"
        self.key = key
        self.cookie = cookie
        self.mobileheaders = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.27(0x18001b33) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx2f9b06c1de1ccfca/85/page-frame.html",
            "content-type": "application/json",
            "Connection": "keep-alive",
        }
        self.pcheaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27",
            "Referer": "https://movie.douban.com/",
            "Cookie": self.cookie,
            "Connection": "keep-alive",
        }
        self.client = Network(maxnumconnect=10, maxnumcache=20)

    def get_movie_info(self, movieid: str):
        """
        获取电影信息
        :param movieid 电影ID
        """
        iteminfo = {}
        try:
            url = "{}/movie/{}?apikey={}".format(self.host, movieid, self.key)
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            url = iteminfo["info_url"]
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            text = html2text.html2text(html=p.text)
            text = text.replace("/\n", "/ ").replace("# 影片信息\n\n", "")
            infolist = re.findall(pattern="([\s\S]+?)\s*\|\s*([\s\S]+?)\n", string=text)
            iteminfo["info"] = {}
            for info in infolist:
                if info[0] == "---":
                    continue
                valuelist = info[1].split(" / ")
                if len(valuelist) > 1:
                    iteminfo["info"][info[0]] = []
                    for value in valuelist:
                        iteminfo["info"][info[0]].append(
                            re.sub(pattern="\s+", repl="", string=value)
                        )
                else:
                    iteminfo["info"][info[0]] = re.sub(
                        pattern="\s+", repl="", string=info[1]
                    )
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def get_movie_celebrities_info(self, movieid: str):
        """
        获取演员信息
        :param movieid 电影ID
        """
        iteminfo = {}
        try:
            url = "{}/movie/{}/celebrities?apikey={}".format(
                self.host, movieid, self.key
            )
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def get_tv_info(self, tvid: str):
        """
        获取电视剧信息
        :param tvid 电影ID
        """
        iteminfo = {}
        try:
            url = "{}/tv/{}?apikey={}".format(self.host, tvid, self.key)
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            if "info_url" not in iteminfo:
                self.err = "获取电视剧信息失败"
                return False, iteminfo
            url = iteminfo["info_url"]
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            text = html2text.html2text(html=p.text)
            text = text.replace("/\n", "/ ").replace("# 影片信息\n\n", "")
            infolist = re.findall(pattern="([\s\S]+?)\s*\|\s*([\s\S]+?)\n", string=text)
            iteminfo["info"] = {}
            for info in infolist:
                if info[0] == "---":
                    continue
                valuelist = info[1].split(" / ")
                if len(valuelist) > 1:
                    iteminfo["info"][info[0]] = []
                    for value in valuelist:
                        iteminfo["info"][info[0]].append(
                            re.sub(pattern="\s+", repl="", string=value)
                        )
                else:
                    iteminfo["info"][info[0]] = re.sub(
                        pattern="\s+", repl="", string=info[1]
                    )
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def get_tv_celebrities_info(self, tvid: str):
        """
        获取演员信息
        :param tvid 电影ID
        """
        iteminfo = {}
        try:
            url = "{}/tv/{}/celebrities?apikey={}".format(self.host, tvid, self.key)
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def get_celebrity_info(self, celebrityid: str):
        """
        获取人物信息
        :param celebrityid 人物ID
        :param True of False, celebrityinfo
        """
        iteminfo = {}
        try:
            url = "{}/celebrity/{}?apikey={}".format(self.host, celebrityid, self.key)
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def search_media_pc(self, title: str):
        """
        搜索电影信息
        :param title 标题
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "https://movie.douban.com/j/subject_suggest?q={}".format(title)
            p, err = self.client.get(url=url, headers=self.pcheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            medialist = json.loads(p.text)
            for media in medialist:
                if (
                    re.search(pattern="第[\s\S]+季", string=media["title"])
                    or len(media["episode"]) > 1
                ):
                    media["target_type"] = "tv"
                else:
                    media["target_type"] = "movie"
                media["target_id"] = media["id"]
            iteminfo["items"] = medialist
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def search_media(self, title: str):
        """
        搜索电影信息
        :param title 标题
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "{}/search/movie?q={}&start=0&count=2&apikey={}".format(
                self.host, title, self.key
            )
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def search_media_weixin(self, title: str):
        """
        搜索媒体信息
        :param title 标题
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "{}/search/weixin?q={}&start=0&count=3&apikey={}".format(
                self.host, title, self.key
            )
            p, err = self.client.get(url=url, headers=self.mobileheaders)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, iteminfo

    def __get_status__(self, p, err):
        try:
            if p == None:
                self.err = err
                return False
            if p.status_code != 200:
                rootobject = json.loads(p.text)
                if "localized_message" in rootobject:
                    self.err = rootobject["localized_message"]
                else:
                    self.err = p.text
                return False
            return True
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )

        return False
