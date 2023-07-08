import requests
import threading


class ClientData(object):
    client = None
    allotnum = None
    allotmaxnum = None
    lock = None

    def __init__(self, allotnum: int = 0, allotmaxnum: int = 3, proxy: str = None):
        self.lock = threading.Lock()
        self.allotnum = allotnum
        self.allotmaxnum = allotmaxnum
        self.client = requests.Session()

        # 设置代理
        if proxy:
            self.client.proxies = {"http": proxy, "https": proxy}

    def get(self, url, **kwargs):
        """
        GET
        :param url
        :return p, err
        """
        self.lock.acquire()
        p = None
        err = None
        try:
            p = self.client.get(url=url, **kwargs)
        except Exception as result:
            err = "异常错误：{}".format(result)
        self.lock.release()
        return p, err

    def post(self, url, **kwargs):
        """
        GET
        :param url
        :return p, err
        """
        self.lock.acquire()
        p = None
        err = None
        try:
            p = self.client.post(url=url, **kwargs)
        except Exception as result:
            err = "异常错误：{}".format(result)
        self.lock.release()
        return p, err
