from emby import emby
from tmdb import tmdb
from douban import douban
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import zhconv
import log

class media:
    embyclient = None
    tmdbclient = None
    doubanclient = None
    languagelist = None
    threadpool = None
    tasklist = None
    updatepeople = None
    updateoverview = None
    err = None

    """
    :param embyhost Emby地址
    :param embyuserid Emby用户ID
    :param embykey Emby ApiKey
    :param tmdbkey Tmdb ApiKey
    :param doubankey 豆瓣 ApiKey
    :param threadnum 线程数量 
    :param updatepeople 更新人物
    :param updateoverview 更新概述
    """
    def __init__(self, embyhost : str, embyuserid : str, embykey : str, tmdbkey : str, doubankey : str, threadnum : int, updatepeople : int, updateoverview : int) -> None:
        self.embyclient = emby(host=embyhost, userid=embyuserid, key=embykey)
        self.tmdbclient = tmdb(key=tmdbkey)
        self.doubanclient = douban(key=doubankey)
        self.languagelist = ['zh-CN', 'zh-SG', 'zh-TW', 'zh-HK']
        self.threadpool = ThreadPoolExecutor(max_workers=threadnum)
        self.tasklist = []
        self.updatepeople = updatepeople
        self.updateoverview = updateoverview

    """
    开始扫描媒体
    :return True or False
    """
    def start_scan_media(self):
        #获取媒体库根文件夹
        ret, itmes = self.embyclient.get_items()
        if not ret:
            log.info('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
            return False
        self.tasklist = []
        ret = self.__check_media_info__(itemlist=itmes)
        log.info('总媒体数量[{}]'.format(len(self.tasklist)))
        for task in as_completed(self.tasklist):
            ret, name = task.result()
            log.info('媒体[{}]处理完成'.format(name))
        return ret

    """
    检查媒体信息
    :param itemlist 项目列表
    :return True or False
    """
    def __check_media_info__(self, itemlist):
        try:
            for item in itemlist['Items']:
                if 'Folder' in item['Type'] and ('CollectionType' not in item or 'boxsets' not in item['CollectionType']):
                    ret, items = self.embyclient.get_items(parentid=item['Id'])
                    if not ret:
                        log.info('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
                        continue
                    self.__check_media_info__(itemlist=items)
                else:
                    if 'Series' in item['Type'] or 'Movie' in item['Type']:
                        task = self.threadpool.submit(self.__to_deal_with_item__, item)
                        self.tasklist.append(task)


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
            updateoverview = False
            ret, iteminfo = self.embyclient.get_item_info(itemid=item['Id'])
            if not ret:
                log.info('获取Emby媒体信息失败, {}'.format(self.embyclient.err))
                return False
            if 'LockedFields' not in iteminfo:
                iteminfo['LockedFields'] = []
            if not self.__is_chinese__(string=item['Name']):
                if 'Tmdb' not in iteminfo['ProviderIds'] and 'tmdb' not in iteminfo['ProviderIds']:
                    log.info('媒体[{}]Tmdb不存在'.format(item['Id']))
                    return False
                
                if 'Tmdb' in iteminfo['ProviderIds']:
                    tmdbid = iteminfo['ProviderIds']['Tmdb']
                else:
                    tmdbid = iteminfo['ProviderIds']['tmdb']

                if 'Series' in item['Type']:
                    ret, name = self.__get_media_tmdb_name__(mediatype=1, datatype=1, id=tmdbid)
                else:
                    ret, name = self.__get_media_tmdb_name__(mediatype=2, datatype=1, id=tmdbid)
                if not ret:
                    return False, item['Name']
                originalname = iteminfo['Name']
                iteminfo['Name'] = name
                if 'Name' not in iteminfo['LockedFields']:
                    iteminfo['LockedFields'].append('Name')
                updatename = True
                    
            if self.updatepeople and 'People' in iteminfo:
                for people in iteminfo['People']:
                    if self.__is_chinese__(string=people['Name'], mode=2) and not self.__is_chinese__(string=people['Name'], mode=3):
                        if not re.match(pattern='\s+', string=people['Name']):
                            continue
                        
                    ret, peopleinfo = self.embyclient.get_item_info(itemid=people['Id'])
                    if 'LockedFields' not in peopleinfo:
                        peopleinfo['LockedFields'] = []
                    if not ret:
                        log.info('获取Emby人物信息失败, {}'.format(self.embyclient.err))
                        continue

                    if 'Tmdb' not in peopleinfo['ProviderIds'] and 'tmdb' not in peopleinfo['ProviderIds']:
                        log.info('人物[{}]Tmdb不存在'.format(peopleinfo['Id']))
                        continue
                    if 'Tmdb' in peopleinfo['ProviderIds']:
                        tmdbid = peopleinfo['ProviderIds']['Tmdb']
                    else:
                        tmdbid = peopleinfo['ProviderIds']['tmdb']
                    if not self.__is_chinese__(string=peopleinfo['Name'], mode=2):
                        ret, name = self.__get_person_tmdb_name(personid=tmdbid)
                        if not ret:
                            continue
                    else:
                        name = re.sub(pattern='\s+', repl='', string=name)
                        name = zhconv.convert(peopleinfo['Name'], 'zh-cn')
                    originalpeoplename = people['Name']
                    peopleinfo['Name'] = name
                    if 'Name' not in peopleinfo['LockedFields']:
                        peopleinfo['LockedFields'].append('Name')
                    people['Name'] = name
                    ret = self.embyclient.set_item_info(itemid=peopleinfo['Id'], iteminfo=peopleinfo)
                    if ret:
                        log.info('原始人物名称[{}]更新为[{}]'.format(originalpeoplename, name))
                        updatepeople = True

            if self.updateoverview:
                if 'Overview' not in iteminfo or not self.__is_chinese__(string=iteminfo['Overview']):
                    if 'Tmdb' in iteminfo['ProviderIds']:
                        tmdbid = iteminfo['ProviderIds']['Tmdb']
                    else:
                        tmdbid = iteminfo['ProviderIds']['tmdb']

                    if 'Series' in item['Type']:
                        ret, overview = self.__get_media_tmdb_name__(mediatype=1, datatype=2, id=tmdbid)
                    else:
                        ret, overview = self.__get_media_tmdb_name__(mediatype=2, datatype=2, id=tmdbid)
                    if not ret:
                        return False, item['Name']
                    iteminfo['Overview'] = overview
                    if 'Overview' not in iteminfo['LockedFields']:
                        iteminfo['LockedFields'].append('Overview')
                    updateoverview = True
                
                if 'Series' in item['Type']:
                    if 'Tmdb' in iteminfo['ProviderIds']:
                        tmdbid = iteminfo['ProviderIds']['Tmdb']
                    else:
                        tmdbid = iteminfo['ProviderIds']['tmdb']
                    ret, seasons = self.embyclient.get_items(parentid=item['Id'])
                    if not ret:
                        log.info('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
                    else:
                        for season in seasons['Items']:
                            ret, episodes = self.embyclient.get_items(parentid=season['Id'])
                            if not ret:
                                log.info('获取Emby媒体信息失败, {}'.format(self.embyclient.err))
                                continue
                            for episode in episodes['Items']:
                                ret, episodeinfo = self.embyclient.get_item_info(itemid=episode['Id'])
                                if not ret:
                                    log.info('获取Emby媒体信息失败, {}'.format(self.embyclient.err))
                                else:
                                    if 'Overview' not in episodeinfo or not self.__is_chinese__(string=episodeinfo['Overview']):
                                        ret, name, overview = self.__get_tv_season_info__(tvid=tmdbid, seasonid=season['IndexNumber'], episodeid=episode['IndexNumber'])
                                        if not ret:
                                            continue
                                        if 'LockedFields' not in episodeinfo:
                                            episodeinfo['LockedFields'] = []
                                        episodeinfo['Name'] = name
                                        episodeinfo['Overview'] = overview
                                        if 'Name' not in episodeinfo['LockedFields']:
                                            episodeinfo['LockedFields'].append('Name')
                                        if 'Overview' not in episodeinfo['LockedFields']:
                                            episodeinfo['LockedFields'].append('Overview')
                                        ret = self.embyclient.set_item_info(itemid=episodeinfo['Id'], iteminfo=episodeinfo)
                                        if ret:
                                            log.info('原始媒体名称[{}] 第[{}]季 第[{}]集更新概述'.format(iteminfo['Name'], season['IndexNumber'], episode['IndexNumber']))

            if not updatename and not updatepeople and not updateoverview:
                return True, item['Name']
            ret = self.embyclient.set_item_info(itemid=iteminfo['Id'], iteminfo=iteminfo)
            if ret:
                if updatename:
                    log.info('原始媒体名称[{}]更新为[{}]'.format(originalname, iteminfo['Name']))
                if updatepeople:
                    log.info('原始媒体名称[{}]更新人物'.format(iteminfo['Name']))
                if updateoverview:
                    log.info('原始媒体名称[{}]更新概述'.format(iteminfo['Name']))
            return True, item['Name']
                    
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, item['Name']    

    """
    获取媒体tmdb中文
    :param mediatype 媒体类型 1TV 2电影
    :param datatype 数据类型 1名字 2概述
    :param id tmdbid
    :return True or False, name
    """
    def __get_media_tmdb_name__(self, mediatype : int, datatype : int, id : str):
        try:
            for language in self.languagelist:
                if mediatype == 1:
                    ret, tvinfo = self.tmdbclient.get_tv_info(tvid=id, language=language)
                    if not ret:
                        log.info('获取TMDB媒体信息失败, {}'.format(self.tmdbclient.err))
                        continue
                    if datatype == 1:
                        if self.__is_chinese__(string=tvinfo['name']):
                            if self.__is_chinese__(string=tvinfo['name'], mode=3):
                                return True, zhconv.convert(tvinfo['name'], 'zh-cn')
                            return True, tvinfo['name']
                        else:
                            ret, name = self.__alternative_name__(alternativetitles=tvinfo)
                            if not ret:
                                continue
                            return True, name
                    else:
                        if self.__is_chinese__(string=tvinfo['overview']):
                            if self.__is_chinese__(string=tvinfo['overview'], mode=3):
                                return True, zhconv.convert(tvinfo['overview'], 'zh-cn')
                            return True, tvinfo['overview']
                else:
                    ret, movieinfo = self.tmdbclient.get_movie_info(movieid=id, language=language)
                    if not ret:
                        log.info('获取TMDB媒体信息失败, {}'.format(self.tmdbclient.err))
                        continue
                    if datatype == 1:
                        if self.__is_chinese__(string=movieinfo['title']):
                            if self.__is_chinese__(string=movieinfo['title'], mode=3):
                                return True, zhconv.convert(movieinfo['title'], 'zh-cn')
                            return True, movieinfo['title']
                        else:
                            ret, name = self.__alternative_name__(alternativetitles=movieinfo)
                            if not ret:
                                continue
                            return True, name
                    else:
                        if self.__is_chinese__(string=movieinfo['overview']):
                            if self.__is_chinese__(string=movieinfo['overview'], mode=3):
                                return True, zhconv.convert(movieinfo['overview'], 'zh-cn')
                            return True, movieinfo['overview']
                    
            return False, None
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    """
    获取季tmdb中文
    :param tvid tmdbid
    :param seasonid 季ID
    :param episodeid 集ID
    :return True or False, name, overview
    """
    def __get_tv_season_info__(self, tvid : str, seasonid : str, episodeid : int):
        try:
            for language in self.languagelist:
                ret, seasoninfo = self.tmdbclient.get_tv_season_info(tvid=tvid, seasonid=seasonid, language=language)
                if not ret:
                    log.info('获取TMDB季信息失败, {}'.format(self.tmdbclient.err))
                    continue
                for episodes in seasoninfo['episodes']:
                    if episodes['episode_number'] > episodeid:
                        break
                    if episodes['episode_number'] != episodeid:
                        continue
                    if self.__is_chinese__(string=episodes['overview']):
                        if self.__is_chinese__(string=episodes['name'], mode=3):
                            name = zhconv.convert(episodes['name'], 'zh-cn')
                        else:
                            name = episodes['name']
                        if self.__is_chinese__(string=episodes['overview'], mode=3):
                            overview = zhconv.convert(episodes['overview'], 'zh-cn')
                        else:
                            overview = episodes['overview']
                        return True, name, overview

            return False, None, None
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None, None
    """
    获取人物tmdb中文
    :param personid 人物ID
    :return True or False, name
    """
    def __get_person_tmdb_name(self, personid):
        try:
            for language in self.languagelist:
                ret, personinfo = self.tmdbclient.get_person_info(personid=personid, language=language)
                if not ret:
                    log.info('获取TMDB人物信息失败, {}'.format(self.tmdbclient.err))
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
                if self.__is_chinese__(string=title['title'], mode=3):
                    return True, zhconv.convert(title['title'], 'zh-cn')
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
