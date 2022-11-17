import requests
import threading

class session(object):
    client = None
    allotnum = None
    allotmaxnum = None
    lock = None

    def __init__(self, allotnum : int = 0, allotmaxnum : int = 3):
        self.lock = threading.Lock()
        self.allotnum = allotnum
        self.allotmaxnum = allotmaxnum
        self.client = requests.Session()

    def get(self, url, params=None, data=None, headers=None, timeout=None, json=None):
        """
        GET
        :param url
        :return p, err
        """
        self.lock.acquire()
        p = None 
        err = None
        try:
            p = self.client.get(url=url, params=params, data=data, headers=headers, timeout=timeout, json=json)
        except Exception as result:
            err = "异常错误：{}".format(result)
        self.lock.release()
        return p, err

    def post(self, url, params=None, data=None, headers=None, timeout=None, json=None):
        """
        GET
        :param url
        :return p, err
        """
        self.lock.acquire()
        p = None 
        err = None
        try:
            p = self.client.post(url=url, params=params, data=data, headers=headers, timeout=timeout, json=json)
        except Exception as result:
            err = "异常错误：{}".format(result)
        self.lock.release()
        return p, err

        
    