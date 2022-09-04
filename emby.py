import requests
import json


class emby:
    host = None
    userid = None
    key = None
    err = None


    def __init__(self, host : str, userid : str, key : str) -> None:
        self.host = host
        self.userid = userid
        self.key = key
    

    """
    获取项目列表
    :param parentid 父文件夹ID
    :return True or False, items
    """
    def get_items(self, parentid : str = ''):
        items = {}
        try:
            if len(parentid):
                url = '{}/emby/Users/{}/Items?ParentId={}&api_key={}'.format(self.host, self.userid, parentid, self.key)
            else:
                url = '{}/emby/Users/{}/Items?api_key={}'.format(self.host, self.userid, self.key)
            p = requests.get(url)
            if p.status_code != 200:
                self.err = p.text
                return False, items
            items = json.loads(p.text)
            return True, items
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, items

    """
    获取项目
    :param itemid 项目ID
    :return True or False, iteminfo
    """
    def get_item_info(self, itemid : str):
        iteminfo = {}
        try:
            url = '{}/emby/Users/{}/Items/{}?Fields=ChannelMappingInfo&api_key={}'.format(self.host, self.userid, itemid, self.key)
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
    更新项目
    :param iteminfo 项目信息
    :return True or False, iteminfo
    """
    def set_item_info(self, itemid : str, iteminfo):
        try:
            url = '{}/emby/Items/{}?api_key={}'.format(self.host, itemid, self.key)
            headers = {'Content-Type':'application/json'}
            data = json.dumps(iteminfo)
            p = requests.post(url=url, headers=headers, data=data)
            if p.status_code != 200 and p.status_code != 204:
                self.err = p.text
                return False
            return True
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False