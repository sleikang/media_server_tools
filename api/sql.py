import sqlite3
import os
import threading

class sql:
    sqlconnect = None
    lock = None
    err = None

    def __init__(self) -> None:
        try:
            self.lock = threading.Lock()
            path = os.path.join(os.environ['EMBYCH_CONFIG'], 'data.db')
            self.sqlconnect = sqlite3.connect(database=path, check_same_thread=False)
            self.execution(sql='CREATE TABLE IF NOT EXISTS "douban_movie" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"media_id" text,"media_name" TEXT,"media_brief" TEXT,"media_data" TEXT,"media_celebrities" TEXT,"update_time" TEXT);')
            self.execution(sql='CREATE TABLE IF NOT EXISTS "douban_people" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"people_id" text,"people_name" TEXT,"people_data" TEXT,"update_time" TEXT);')
            self.execution(sql='CREATE TABLE IF NOT EXISTS "douban_tv" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"media_id" text,"media_name" TEXT,"media_brief" TEXT,"media_data" TEXT,"media_celebrities" TEXT,"update_time" TEXT);')
            self.execution(sql='CREATE TABLE IF NOT EXISTS "tmdb_movie" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"media_id" text,"media_name" TEXT,"media_data_zh_cn" TEXT,"media_data_zh_sg" TEXT,"media_data_zh_tw" TEXT,"media_data_zh_hk" TEXT,"update_time" TEXT);')
            self.execution(sql='CREATE TABLE IF NOT EXISTS "tmdb_people" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"people_id" text,"people_name" TEXT,"people_data_zh_cn" TEXT,"people_data_zh_sg" TEXT,"people_data_zh_tw" TEXT,"people_data_zh_hk" TEXT,"update_time" TEXT);')
            self.execution(sql='CREATE TABLE IF NOT EXISTS "tmdb_tv" ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"media_id" text,"media_name" TEXT,"media_data_zh_cn" TEXT,"media_data_zh_sg" TEXT,"media_data_zh_tw" TEXT,"media_data_zh_hk" TEXT,"season_data_zh_cn" TEXT,"season_data_zh_sg" TEXT,"season_data_zh_tw" TEXT,"season_data_zh_hk" TEXT,"update_time" TEXT);')
        except Exception as reuslt:
            self.err = '数据库异常错误, {}'.format(reuslt)

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