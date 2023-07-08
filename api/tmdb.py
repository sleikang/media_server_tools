import json

from network.network import Network


class tmdb:
    host = None
    key = None
    err = None
    client = None

    def __init__(
        self, key: str, host: str = "https://api.themoviedb.org/3", proxy: str = None
    ) -> None:
        """
        :param key apikey
        """
        self.host = host
        self.key = key
        self.client = Network(maxnumconnect=10, maxnumcache=20, proxy=proxy)

    def get_movie_info(self, movieid: str, language: str = "zh-CN"):
        """
        获取电影信息
        :param movieid
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "{}/movie/{}?api_key={}&language={}&append_to_response=alternative_titles".format(
                self.host, movieid, self.key, language
            )
            p, err = self.client.get(url=url)
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

    def get_tv_info(self, tvid: str, language: str = "zh-CN"):
        """
        获取tv信息
        :param tvid
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "{}/tv/{}?api_key={}&language={}&append_to_response=alternative_titles,episode_groups".format(
                self.host, tvid, self.key, language
            )
            p, err = self.client.get(url=url)
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

    def get_tv_season_group(self, groupid: str, language: str = "zh-CN"):
        """
        获取tv季组
        :param groupid 组id
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "{}/tv/episode_group/{}?api_key={}&language={}&append_to_response=alternative_titles".format(
                self.host, groupid, self.key, language
            )
            p, err = self.client.get(url=url)
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

    def get_tv_season_info(self, tvid: str, seasonid: str, language: str = "zh-CN"):
        """
        获取tv季信息
        :param tvid
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = "{}/tv/{}/season/{}?api_key={}&language={}&append_to_response=alternative_titles".format(
                self.host, tvid, seasonid, self.key, language
            )
            p, err = self.client.get(url=url)
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

    def get_person_info(self, personid: str, language: str = "zh-CN"):
        """
        获取人物信息
        :param personid 人物ID
        :return True or False, personinfo
        """
        personinfo = {}
        try:
            url = "{}/person/{}?api_key={}&language={}".format(
                self.host, personid, self.key, language
            )
            p, err = self.client.get(url=url)
            if not self.__get_status__(p=p, err=err):
                return False, personinfo
            personinfo = json.loads(p.text)
            return True, personinfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(
                result.__traceback__.tb_frame.f_globals["__file__"],
                result.__traceback__.tb_lineno,
                result,
            )
        return False, personinfo

    def __get_status__(self, p, err):
        try:
            if p == None:
                self.err = err
                return False
            if p.status_code != 200:
                rootobject = json.loads(p.text)
                if "status_message" in rootobject:
                    self.err = rootobject["status_message"]
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
