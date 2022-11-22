import json
from api.server.serverbase import serverbase, network

class emby(serverbase):
    host = None
    userid = None
    key = None
    headers = None
    err = None
    client = None


    def __init__(self, host : str, userid : str, key : str) -> None:
        """
        :param host
        :param userid
        :param key
        """
        self.host = host
        self.userid = userid
        self.key = key
        self.headers = {'Content-Type':'application/json'}
        self.client = network(maxnumconnect=10, maxnumcache=20)
    

    def get_items(self, parentid : str = ''):
        """
        获取项目列表
        :param parentid 父文件夹ID
        :return True or False, items
        """
        items = {}
        try:
            if len(parentid):
                url = '{}/emby/Users/{}/Items?ParentId={}&api_key={}'.format(self.host, self.userid, parentid, self.key)
            else:
                url = '{}/emby/Users/{}/Items?api_key={}'.format(self.host, self.userid, self.key)
            p, err = self.client.get(url=url)
            if not self.__get_status__(p=p, err=err):
                return False, items
            items = json.loads(p.text)
            return True, items
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False, items

    def get_items_count(self):
        """
        获取项目数量
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = '{}/emby/Items/Counts?api_key={}'.format(self.host, self.key)
            p, err = self.client.get(url=url)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False, iteminfo

    def get_item_info(self, itemid : str):
        """
        获取项目
        :param itemid 项目ID
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = '{}/emby/Users/{}/Items/{}?Fields=ChannelMappingInfo&api_key={}'.format(self.host, self.userid, itemid, self.key)
            p, err = self.client.get(url=url)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False, iteminfo

    def set_item_info(self, itemid : str, iteminfo):
        """
        更新项目
        :param iteminfo 项目信息
        :return True or False, iteminfo
        """
        try:
            url = '{}/emby/Items/{}?api_key={}'.format(self.host, itemid, self.key)
            data = json.dumps(iteminfo)
            p, err = self.client.post(url=url, headers=self.headers, data=data)
            if not self.__get_status__(p=p, err=err):
                return False
            return True
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False

    def set_item_image(self, itemid : str, imageurl : str):
        """
        更新项目图片
        :param imageurl 图片URL
        :return True or False
        """
        try:
            url = '{}/emby/Items/{}/Images/Primary/0/Url?api_key={}'.format(self.host, itemid, self.key)
            data = json.dumps({'Url': imageurl})
            p, err = self.client.post(url=url, headers=self.headers, data=data)
            if not self.__get_status__(p=p, err=err):
                return False
            return True
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False

    def search_movie(self, itemid, tmdbid):
        """
        搜索视频
        :param itemid 项目ID
        :param tmdbid TMDB ID
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            url = '{}/emby/Items/RemoteSearch/Movie?api_key={}'.format(self.host, self.key)
            data = json.dumps({'SearchInfo':{'ProviderIds':{'Tmdb':tmdbid}},'ItemId':itemid})
            p, err = self.client.post(url=url, headers=self.headers, data=data)
            if not self.__get_status__(p=p, err=err):
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False, iteminfo
    
    def apply_search(self, itemid, iteminfo):
        """
        应用搜索
        :param itemid 项目ID
        :param iteminfo 项目信息
        :return True or False
        """
        try:
            url = '{}/emby/Items/RemoteSearch/Apply/{}?ReplaceAllImages=true&api_key={}'.format(self.host, itemid, self.key)
            data = json.dumps(iteminfo)
            p, err = self.client.post(url=url, headers=self.headers, data=data)
            if not self.__get_status__(p=p, err=err):
                return False
            return True
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False
    
    def refresh(self, itemid):
        """
        刷新元数据
        :param itemid 项目ID
        :return True or False
        """
        try:
            url = '{}/emby/Items/{}/Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=true&api_key={}'.format(self.host, itemid, self.key)
            p, err = self.client.post(url=url, headers=self.headers)
            if not self.__get_status__(p=p, err=err):
                return False
            return True
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        return False

    def __get_status__(self, p, err):
        try:
            if p == None:
                self.err = err
                return False
            if p.status_code != 200 and p.status_code != 204:
                self.err = p.text
                return False
            return True
        except Exception as result:
            self.err = "异常错误：{}".format(result)
        
        return False