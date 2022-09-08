from sql import sql
import json
import datetime

class mediasql(sql):

    def search_douban_media(self, mediatype : int, title : str):
        """
        搜索豆瓣媒体
        :param mediatype 媒体类型 1TV 2电影
        :param titel 媒体标题
        :return True or False, iteminfo
        """
        iteminfo = {'items':[]}
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from douban_tv where media_name like '%{}%';".format(title))
            else:
                ret, datalist = self.query(sql="select * from douban_movie where media_name like '%{}%';".format(title))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                iteminfo['items'].append(json.loads(data[3]))
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def write_douban_media(self, mediatype : int, id : str, iteminfo):
        """
        写入豆瓣媒体
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :param iteminfo 媒体信息
        :return True or False
        """
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from douban_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from douban_movie where media_id = '{}';".format(id))
            if not ret:
                return False
            for data in datalist:
                if mediatype == 1:
                    ret = self.execution(sql="update douban_tv set media_brief = ?, update_time = ? where media_id = ?;", data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                else:
                    ret = self.execution(sql="update douban_movie set media_brief = ?, update_time = ? where media_id = ?;", data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                return ret
            
            if mediatype == 1:
                ret = self.execution(sql="insert into douban_tv(id, media_id, media_name, media_brief, media_data, media_celebrities, update_time) values(null, ?, ?, ?, '', '', ?);", data=(id, iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                ret = self.execution(sql="insert into douban_movie(id, media_id, media_name, media_brief, media_data, media_celebrities, update_time) values(null, ?, ?, ?, '', '', ?);", data=(id, iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False

    def get_douban_media_info(self, mediatype : int, id : str):
        """
        获取豆瓣媒体信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from douban_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from douban_movie where media_id = '{}';".format(id))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                iteminfo = json.loads(data[4])
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def write_douban_media_info(self, mediatype : int, id : str, iteminfo):
        """
        写入豆瓣媒体信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :param iteminfo  媒体信息
        :return True or False
        """
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from douban_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from douban_movie where media_id = '{}';".format(id))
            if not ret:
                return False
            for data in datalist:
                if mediatype == 1:
                    ret = self.execution(sql="update douban_tv set media_data = ?, update_time = ? where media_id = ?;", data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                else:
                    ret = self.execution(sql="update douban_movie set media_data = ?, update_time = ? where media_id = ?;", data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                return ret
            
            if mediatype == 1:
                ret = self.execution(sql="insert into douban_tv(id, media_id, media_name, media_brief, media_data, media_celebrities, update_time) values(null, ?, ?, '', ?, '', ?);", data=(id, iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                ret = self.execution(sql="insert into douban_movie(id, media_id, media_name, media_brief, media_data, media_celebrities, update_time) values(null, ?, ?, '', ?, '', ?);", data=(id, iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False

    def get_douban_celebrities_info(self, mediatype : int, id : str):
        """
        获取豆瓣媒体演员信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from douban_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from douban_movie where media_id = '{}';".format(id))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                iteminfo = json.loads(data[5])
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def write_douban_celebrities_info(self, mediatype : int, id : str, iteminfo):
        """
        写入豆瓣媒体演员信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :param iteminfo 演员信息
        :return True or False
        """
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from douban_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from douban_movie where media_id = '{}';".format(id))
            if not ret:
                return False
            for data in datalist:
                if mediatype == 1:
                    ret = self.execution(sql="update douban_tv set media_celebrities = ?, update_time = ? where media_id = ?;", data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                else:
                    ret = self.execution(sql="update douban_movie set media_celebrities = ?, update_time = ? where media_id = ?;", data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                return ret
            
            if mediatype == 1:
                ret = self.execution(sql="insert into douban_tv(id, media_id, media_name, media_brief, media_data, media_celebrities, update_time) values(null, ?, '', '', '', ?, ?);", data=(id, json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                ret = self.execution(sql="insert into douban_movie(id, media_id, media_name, media_brief, media_data, media_celebrities, update_time) values(null, ?, '', '', '', ?, ?);", data=(id, json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False

    def get_douban_people_info(self, id : str):
        """
        获取豆瓣演员信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 人物ID
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            ret, datalist = self.query(sql="select * from douban_people where people_id = '{}';".format(id))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                iteminfo = json.loads(data[3])
            return True, iteminfo
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, iteminfo

    def write_douban_people_info(self, id : str, iteminfo):
        """
        写入豆瓣演员信息
        :param id 人物ID
        :param name 人物姓名
        :param iteminfo 人物信息
        :return True or False
        """
        try:
            ret, datalist = self.query(sql="select * from douban_people where people_id = '{}';".format(id))
            if not ret:
                return False
            for data in datalist:
                ret = self.execution(sql="update douban_people set people_name = ?, people_data = ?, update_time = ? where people_id = ?;", data=(iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[2]))
                return ret
            ret = self.execution(sql="insert into douban_people(id, people_id, people_name, people_data, update_time) values(null, ?, ?, ?, ?)", data=(id, iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False


    def get_tmdb_media_info(self, mediatype : int, id : str, language):
        """
        读取TMDB媒体信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :param language 语言
        :returen True or False, iteminfo
        """
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from tmdb_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from tmdb_movie where media_id = '{}';".format(id))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                item = None
                if language == 'zh-CN':
                    item = data[3]
                elif language == 'zh-SG':
                    item = data[4]
                elif language == 'zh-TW':
                    item = data[5]
                elif language == 'zh-HK':
                    item = data[6]   
                if not item:
                    return False, None
                
                return True, json.loads(item)
                    
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    def write_tmdb_media_info(self, mediatype : int, id : str, language, iteminfo):
        """
        写入TMDB媒体信息
        :param mediatype 媒体类型 1TV 2电影
        :param id 媒体ID
        :param language 语言
        :param iteminfo 媒体信息
        :returen True or False
        """
        try:
            if mediatype == 1:
                ret, datalist = self.query(sql="select * from tmdb_tv where media_id = '{}';".format(id))
            else:
                ret, datalist = self.query(sql="select * from tmdb_movie where media_id = '{}';".format(id))
            if not ret:
                return False
            key = None
            if language == 'zh-CN':
                key = 'media_data_zh_cn'
            elif language == 'zh-SG':
                key = 'media_data_zh_sg'
            elif language == 'zh-TW':
                key = 'media_data_zh_tw'
            elif language == 'zh-HK':
                key = 'media_data_zh_hk'
            if not key:
                self.err = '当前语言[{}]不支持'.format(language)
                return False
            for data in datalist:
                if mediatype == 1:
                    ret = self.execution(sql="update tmdb_tv set {} = ?, media_name = ?, update_time = ? where media_id = ?;".format(key), data=(json.dumps(iteminfo), iteminfo['name'], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                else:
                    ret = self.execution(sql="update tmdb_movie set {} = ?, media_name = ?, update_time = ? where media_id = ?;".format(key), data=(json.dumps(iteminfo), iteminfo['title'], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                return ret
            if mediatype == 1:
                ret = self.execution(sql="insert into tmdb_tv(id, media_id, media_name, {}, update_time) values(null, ?, ?, ?, ?);".format(key), data=(id, iteminfo['name'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                ret = self.execution(sql="insert into tmdb_movie(id, media_id, media_name, {}, update_time) values(null, ?, ?, ?, ?);".format(key), data=(id, iteminfo['title'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False

    def get_tmdb_season_info(self, id : str, language):
        """
        读取TMDB季信息
        :param id 媒体ID
        :param language 语言
        :returen True or False, iteminfo
        """
        try:
            ret, datalist = self.query(sql="select * from tmdb_tv where media_id = '{}';".format(id))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                item = None
                if language == 'zh-CN':
                    item = data[7]
                elif language == 'zh-SG':
                    item = data[8]
                elif language == 'zh-TW':
                    item = data[9]
                elif language == 'zh-HK':
                    item = data[10]   
                if not item:
                    return False, None
                
                return True, json.loads(item)
                    
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    def write_tmdb_season_info(self, id : str, language, iteminfo):
        """
        写入TMDB季信息
        :param id 媒体ID
        :param language 语言
        :param iteminfo 季信息
        :returen True or False
        """
        try:
            ret, datalist = self.query(sql="select * from tmdb_tv where media_id = '{}';".format(id))
            if not ret:
                return False
            key = None
            if language == 'zh-CN':
                key = 'season_data_zh_cn'
            elif language == 'zh-SG':
                key = 'season_data_zh_sg'
            elif language == 'zh-TW':
                key = 'season_data_zh_tw'
            elif language == 'zh-HK':
                key = 'season_data_zh_hk'
            if not key:
                self.err = '当前语言[{}]不支持'.format(language)
                return False
            for data in datalist:
                ret = self.execution(sql="update tmdb_tv set {} = ?, update_time = ? where media_id = ?;".format(key), data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                return ret
            ret = self.execution(sql="insert into tmdb_tv(id, media_id, {}, update_time) values(null, ?, ?, ?);".format(key), data=(id, json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False

    def get_tmdb_people_info(self, id : str, language):
        """
        获取TMDB人物信息
        :param id 人物ID
        :param language 语言
        :returen True or False, iteminfo
        """
        try:
            ret, datalist = self.query(sql="select * from tmdb_people where people_id = '{}';".format(id))
            if not ret or not len(datalist):
                return False, None
            for data in datalist:
                item = None
                if language == 'zh-CN':
                    item = data[3]
                elif language == 'zh-SG':
                    item = data[4]
                elif language == 'zh-TW':
                    item = data[5]
                elif language == 'zh-HK':
                    item = data[6]   
                if not item:
                    return False, None
                
                return True, json.loads(item)
                    
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    def write_tmdb_people_info(self, id : str, language, iteminfo):
        """
        写入TMDB人物信息
        :param id 人物ID
        :param language 语言
        :param iteminfo 人物信息
        :returen True or False
        """
        try:
            ret, datalist = self.query(sql="select * from tmdb_people where people_id = '{}';".format(id))
            if not ret:
                return False
            key = None
            if language == 'zh-CN':
                key = 'people_data_zh_cn'
            elif language == 'zh-SG':
                key = 'people_data_zh_sg'
            elif language == 'zh-TW':
                key = 'people_data_zh_tw'
            elif language == 'zh-HK':
                key = 'people_data_zh_hk'
            if not key:
                self.err = '当前语言[{}]不支持'.format(language)
                return False
            for data in datalist:
                ret = self.execution(sql="update tmdb_people set {} = ?, update_time = ? where people_id = ?;".format(key), data=(json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data[1]))
                return ret
            ret = self.execution(sql="insert into tmdb_people(id, people_id, people_name, {}, update_time) values(null, ?, ?, ?, ?);".format(key), data=(id, iteminfo['name'], json.dumps(iteminfo), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            return ret
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False