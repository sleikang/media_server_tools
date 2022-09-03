import time
from emby import emby
from tmdb import tmdb
from concurrent.futures import ThreadPoolExecutor
import re
import zhconv

class embyserver:
    embyclient = None
    tmdbclient = None
    languagelist = None
    threadpool = None
    tasklist = None
    updatepeople = None
    err = None

    """
    :param embyhost Emby地址
    :param embyuserid Emby用户ID
    :param embykey Emby ApiKey
    :param tmdbkey Tmdb ApiKey
    :param threadnum 线程数量 
    """
    def __init__(self, embyhost : str, embyuserid : str, embykey : str, tmdbkey : str, threadnum : int = 10, updatepeople : int = False) -> None:
        self.embyclient = emby(host=embyhost, userid=embyuserid, key=embykey)
        self.tmdbclient = tmdb(key=tmdbkey)
        self.languagelist = ['zh-CN', 'zh-SG', 'zh-TW']
        self.threadpool = ThreadPoolExecutor(max_workers=threadnum)
        self.tasklist = []
        self.updatepeople = updatepeople

    """
    更新媒体中文名称
    :return True or False
    """
    def update_media_name(self):
        #获取媒体库根文件夹
        ret, itmes = self.embyclient.get_items()
        if ret == False:
            print('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
            return False
        ret = self.__check_media_info__(itemlist=itmes)
        for task in self.tasklist:
            task.result()
        self.tasklist.clear()
        self.threadpool.shutdown(wait=True)
        return ret

    """
    检查媒体信息
    :param itemlist 项目列表
    :return True or False
    """
    def __check_media_info__(self, itemlist):
        try:
            for item in itemlist['Items']:
                if 'Folder' in item['Type']:
                    ret, items = self.embyclient.get_items(parentid=item['Id'])
                    if ret == False:
                        print('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
                        continue
                    self.__check_media_info__(itemlist=items)
                    time.sleep(0.1)
                else:
                    task = self.threadpool.submit(self.__to_deal_with_item__, item)
                    self.tasklist.append(task)
                    time.sleep(0.1)

            return True     
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False
        
    """
    处理媒体
    :param item
    :return True or False
    """
    def __to_deal_with_item__(self, item):
        try:
            updatename = False
            updatepeople = False
            ret, iteminfo = self.embyclient.get_item_info(itemid=item['Id'])
            if not self.__is_chinese__(string=item['Name']):
                if ret == False:
                    print('获取Emby媒体信息失败, {}'.format(self.embyclient.err))
                    return False
                if 'Tmdb' not in iteminfo['ProviderIds']:
                    print('媒体[{}]Tmdb不存在'.format(item['Id']))
                    return False
                if 'Series' in item['Type']:
                    ret, name = self.__get_media_tmdb_name__(type=1, id=iteminfo['ProviderIds']['Tmdb'])
                else:
                    ret, name = self.__get_media_tmdb_name__(type=2, id=iteminfo['ProviderIds']['Tmdb'])
                    if ret == False:
                        return False
                    originalname = iteminfo['Name']
                    iteminfo['Name'] = name
                    iteminfo['LockedFields'] = ['Name']
                    updatename = True
                    
            if self.updatepeople and 'People' in iteminfo:
                for people in iteminfo['People']:
                    if self.__is_chinese__(string=people['Name'], mode=2) and not self.__is_chinese__(string=people['Name'], mode=3):
                        if not re.match(pattern='\s+', string=people['Name']):
                            continue
                        
                    ret, peopleinfo = self.embyclient.get_item_info(itemid=people['Id'])
                    if ret == False:
                        print('获取Emby人物信息失败, {}'.format(self.embyclient.err))
                        continue

                    if 'Tmdb' not in peopleinfo['ProviderIds']:
                        print('人物[{}]Tmdb不存在'.format(peopleinfo['Id']))
                        continue
                    if not self.__is_chinese__(string=peopleinfo['Name'], mode=2):
                        ret, name = self.__get_person_tmdb_name(personid=peopleinfo['ProviderIds']['Tmdb'])
                        if ret == False:
                            continue
                    else:
                        name = re.sub(pattern='\s+', repl='', string=name)
                        name = zhconv.convert(peopleinfo['Name'], 'zh-cn')
                        originalpeoplename = people['Name']
                        peopleinfo['Name'] = name
                        peopleinfo['LockedFields'] = ['Name']
                        people['Name'] = name
                        ret = self.embyclient.set_item_info(itemid=peopleinfo['Id'], iteminfo=peopleinfo)
                        if ret:
                             print('原始人物名称[{}]更新为[{}]'.format(originalpeoplename, name))
                        updatepeople = True

            if not updatename and not updatepeople:
                return False
            ret = self.embyclient.set_item_info(itemid=iteminfo['Id'], iteminfo=iteminfo)
            if ret:
                if updatename:
                    print('原始媒体名称[{}]更新为[{}]'.format(originalname, iteminfo['Name']))
                elif updatepeople:
                    print('原始媒体名称[{}]更新人物'.format(iteminfo['Name']))
            return True
                    
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False    

    """
    获取媒体tmdb中文
    :param type 类型 1TV 2电影
    :return True or False, name
    """
    def __get_media_tmdb_name__(self, type : int, id):
        try:
            for language in self.languagelist:
                if type == 1:
                    ret, tvinfo = self.tmdbclient.get_tv_info(tvid=id, language=language)
                    if ret == False:
                        print('获取TMDB媒体信息失败, {}'.format(self.tmdbclient.err))
                        continue
                    if self.__is_chinese__(string=tvinfo['name']):
                        return True, tvinfo['name']
                    else:
                        ret, name = self.__alternative_name__(alternativetitles=tvinfo)
                        if ret == False:
                            continue
                        return True, name
                else:
                    ret, movieinfo = self.tmdbclient.get_move_info(movieid=id, language=language)
                    if ret == False:
                        print('获取TMDB媒体信息失败, {}'.format(self.tmdbclient.err))
                        continue
                    if self.__is_chinese__(string=movieinfo['title']):
                        return True, movieinfo['title']
                    else:
                        ret, name = self.__alternative_name__(alternativetitles=movieinfo)
                        if ret == False:
                            continue
                        return True, name
                    
            return False, None
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    """
    获取人物tmdb中文
    :param personid 人物ID
    :return True or False, name
    """
    def __get_person_tmdb_name(self, personid):
        try:
            for language in self.languagelist:
                ret, personinfo = self.tmdbclient.get_person_info(personid=personid, language=language)
                if ret == False:
                    print('获取TMDB人物信息失败, {}'.format(self.tmdbclient.err))
                    continue
                for name in personinfo['also_known_as']:
                    if not self.__is_chinese__(string=name, mode=2):
                        continue
                    if self.__is_chinese__(string=name, mode=3):
                        name = zhconv.convert(name, 'zh-cn')
                    return True, re.sub(pattern='\s+', repl='', string=name)
                break
            return False, None
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    """
    返回别名中文名称
    :return True or False, name
    """
    def __alternative_name__(self, alternativetitles):
        try:
            for title in alternativetitles['alternative_titles']['titles']:
                if 'iso_3166_1' not in title:
                    continue
                if title['iso_3166_1'] != 'CN':
                    continue
                if not self.__is_chinese__(string=title['title']):
                    continue
                return True, title['title']
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None


    """
    判断是否包含中文
    :param string 需要判断的字符
    :param mode 模式 1匹配简体和繁体 2只匹配简体 3只匹配繁体
    :return True or False
    """
    def __is_chinese__(self, string : str, mode : int = 1):
        for ch in string:
            if mode == 1:
                if '\u4e00' <= ch <= '\u9FFF':
                    return True
            elif mode == 2:
                if '\u4e00' <= ch <= '\u9FA5':
                    return True
            elif mode == 3:
                if '\u4e00' <= ch <= '\u9FFF':
                    if zhconv.convert(ch, 'zh-cn') != ch:
                        return True
        if re.match(pattern='^[0-9]+$', string=string):
            return True
        return False