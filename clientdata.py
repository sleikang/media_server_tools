import requests
import threading

class clientdata(object):
    client = None
    allotnum = None
    allotmaxnum = None
    lock = None

    def __init__(self, allotnum : int = 0, allotmaxnum : int = 3):
        self.lock = threading.Lock()
        self.allotnum = allotnum
        self.allotmaxnum = allotmaxnum
        self.client = requests.Session()

    def get(self, url):
        """
        GET
        :param url
        :return p, err
        """
        self.lock.acquire()
        p = None 
        err = None
        try:
            p = self.client.get(url=url)
        except Exception as result:
            err = "异常错误：{}".format(result)
        self.lock.release()
        return p, err

    def post(self, url, data = None, headers = None):
        """
        GET
        :param url
        :return p, err
        """
        self.lock.acquire()
        p = None 
        err = None
        try:
            p = self.client.post(url=url, headers=headers, data=data)
        except Exception as result:
            err = "异常错误：{}".format(result)
        self.lock.release()
        return p, err

        
    