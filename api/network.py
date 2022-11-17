from api.session import session
import threading

class network:
    maxnumconnect = None
    maxnumcache = None
    clientlist = None
    lock = None

    def __init__(self, maxnumconnect : int = 1, maxnumcache : int = 5) -> None:
        """
        构造函数
        :param maxnumconnect 最大连接数
        :param maxnumcache 最大缓存数
        """
        self.lock = threading.Lock()
        self.maxnumcache = maxnumcache
        self.maxnumconnect = maxnumconnect
        self.clientlist = []
        if self.maxnumcache < 0:
            self.maxnumcache = 1
        if self.maxnumconnect < 0:
            self.maxnumconnect = 1
        for i in range(self.maxnumconnect):
            self.clientlist.append(session(allotmaxnum=self.maxnumcache))

    def get(self, url, params=None, data=None, headers=None, timeout=None, json=None):
        """
        GET
        :param url
        :return p, err
        """
        p = None
        ret, num, err = self.__getclient__()
        if ret:
            p, err = self.clientlist[num].get(url=url, params=params, data=data, headers=headers, timeout=timeout, json=json)
            self.__releasecache__(num=num)
        return p, err

    def post(self, url, params=None, data=None, headers=None, timeout=None, json=None):
        """
        POST
        :param url
        :param data
        :param headers
        :return p, err
        """
        p = None
        ret, num, err = self.__getclient__()
        if ret:
            p, err = self.clientlist[num].post(url=url, params=params, data=data, headers=headers, timeout=timeout, json=json)
            self.__releasecache__(num=num)
        return p, err

    def __getclient__(self):
        """
        获取客户端
        :return True, num, err 成功返回True, 编号, None 失败返回False, None, 错误
        """
        #优先空闲连接
        for i in range(len(self.clientlist)):
            if self.clientlist[i].allotnum < self.clientlist[i].allotmaxnum and self.clientlist[i].allotnum == 0:
                self.clientlist[i].allotnum += 1
                return True, i, None
        
        #优先缓存数少的
        minallotnum = -1
        num = -1

        for i in range(len(self.clientlist)):
            if self.clientlist[i].allotnum < self.clientlist[i].allotmaxnum:
                if minallotnum == -1:
                    minallotnum = self.clientlist[i].allotnum
                    num = i
                elif minallotnum > self.clientlist[i].allotnum:
                    minallotnum = self.clientlist[i].allotnum
                    num = i

        if num > -1:
            self.clientlist[num].allotnum += 1
            return True, num, None
        
        return False, None, '连接缓存已满'


    def __releasecache__(self, num : int):
        """
        释放连接
        :param num 连接编号
        """
        self.clientlist[num].allotnum -= 1