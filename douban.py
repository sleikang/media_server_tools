import requests
import json

class douban:
    host = None
    key = None
    useragent = None
    headers = None
    err = None

    def __init__(self, key : str) -> None:
        self.host = 'https://frodo.douban.com/api/v2'
        self.key = key
        self.useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.20(0x18001434) NetType/WIFI Language/en'
        self.headers = {'User-Agent':self.useragent, 'Referer': 'https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html', 'Accept-Encoding': 'gzip,compress,deflate', 'Content-Type': 'application/json'}

    """
    获取电影信息
    :param movieid 电影ID
    """
    def get_movie_info(self, movieid : str):
        iteminfo = {}
        try:
            url = '{}/movie/{}?apikey={}'.format(self.host, movieid, self.key)
            p = requests.get(url=url, headers=self.headers)
            if p.status_code != 200:
                self.err = p.text
                return False, iteminfo
            iteminfo = json.loads(p.text)
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo