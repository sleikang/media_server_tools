import sqlite3
import os
from log import log
import threading

class sql:
    sqlconnect = None
    lock = None
    err = None

    def __init__(self) -> None:
        try:
            self.lock = threading.Lock()
            path = os.path.join(os.getcwd(), 'config', 'data.db')
            self.sqlconnect = sqlite3.connect(database=path, check_same_thread=False)
        except Exception as reuslt:
            err = '数据库异常错误, {}'.format(reuslt)

    def query(self, sql : str):
        """
        查询数据库
        :param sql 语句
        :return True or False, data
        """
        self.lock.acquire()
        done = False
        data = None
        try:
            cursor = self.sqlconnect.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            done = True
        except Exception as reuslt:
            self.err = '数据库异常错误, {}'.format(reuslt)
        self.lock.release()
        return done, data

    def execution(self, sql : str, data = None):
        """
        执行数据库
        :param sql 语句
        :return True or False
        """
        self.lock.acquire()
        done = False
        try:
            cursor = self.sqlconnect.cursor()
            if data:
                cursor.execute(sql, data)
            else:
                cursor.execute(sql)
            self.sqlconnect.commit()
            done = True
        except Exception as reuslt:
            self.err = '数据库异常错误, {}'.format(reuslt)
        self.lock.release()
        return done