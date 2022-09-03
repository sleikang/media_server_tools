import time
from emby import emby
from tmdb import tmdb
import re

class embyserver:
    embyclient = None
    tmdbclient = None
    languagelist = None
    err = None

    def __init__(self, embyhost : str, embyuserid : str, embykey : str, tmdbkey : str) -> None:
        self.embyclient = emby(host=embyhost, userid=embyuserid, key=embykey)
        self.tmdbclient = tmdb(key=tmdbkey)
        self.languagelist = ['zh-CN', 'zh-SG', 'zh-TW']

    """
    更新媒体中文名称
    :return True or False
    """
    def updatemedianame(self):
        #获取媒体库根文件夹
        ret, itmes = self.embyclient.getitems()
        if ret == False:
            print('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
            return False
        return self.__checkmediainfo__(itemlist=itmes)

    """
    检查媒体信息
    :return True or False
    """
    def __checkmediainfo__(self, itemlist):
        try:
            for item in itemlist['Items']:
                if 'Folder' in item['Type']:
                    ret, items = self.embyclient.getitems(parentid=item['Id'])
                    if ret == False:
                        print('获取Emby媒体列表失败, {}'.format(self.embyclient.err))
                        continue
                    self.__checkmediainfo__(itemlist=items)
                else:
                    updatename = False
                    updatepeople = False
                    ret, iteminfo = self.embyclient.getiteminfo(itemid=item['Id'])
                    if not self.__ischinese__(string=item['Name']):
                        if ret == False:
                            print('获取Emby媒体信息失败, {}'.format(self.embyclient.err))
                            continue
                        if 'Tmdb' not in iteminfo['ProviderIds']:
                            print('媒体[{}]Tmdb不存在'.format(item['Id']))
                            continue
                        if 'Series' in item['Type']:
                            ret, name = self.__getmediatmdbname__(type=1, id=iteminfo['ProviderIds']['Tmdb'])
                        else:
                            ret, name = self.__getmediatmdbname__(type=2, id=iteminfo['ProviderIds']['Tmdb'])
                        if ret == False:
                            continue
                        originalname = iteminfo['Name']
                        iteminfo['Name'] = name
                        iteminfo['LockedFields'] = ['Name']
                        updatename = True
                    
                    if 'People' in iteminfo:
                        for people in iteminfo['People']:
                            if self.__ischinese__(people['Name']):
                                continue
                            ret, peopleinfo = self.embyclient.getiteminfo(itemid=people['Id'])
                            if ret == False:
                                print('获取Emby人物信息失败, {}'.format(self.embyclient.err))
                                continue
                            if 'Tmdb' not in peopleinfo['ProviderIds']:
                                print('人物[{}]Tmdb不存在'.format(peopleinfo['Id']))
                                continue
                            if not self.__ischinese__(peopleinfo['Name']):
                                ret, name = self.__getpersontmdbname(personid=peopleinfo['ProviderIds']['Tmdb'])
                                if ret == False:
                                    continue
                            else:
                                name = peopleinfo['Name']
                            originalpeoplename = people['Name']
                            peopleinfo['Name'] = name
                            peopleinfo['LockedFields'] = ['Name']
                            people['Name'] = name
                            ret = self.embyclient.setiteminfo(itemid=peopleinfo['Id'], iteminfo=peopleinfo)
                            if ret:
                                print('原始人物名称[{}]更新为[{}]'.format(originalpeoplename, name))
                            updatepeople = True

                    if not updatename and not updatepeople:
                        continue
                    ret = self.embyclient.setiteminfo(itemid=iteminfo['Id'], iteminfo=iteminfo)
                    if ret:
                        if updatename:
                            print('原始媒体名称[{}]更新为[{}]'.format(originalname, iteminfo['Name']))
                        elif updatepeople:
                            print('原始媒体名称[{}]更新人物'.format(iteminfo['Name']))

                    time.sleep(1)

            return True
                
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False
        
    """
    获取媒体tmdb中文
    :param type 类型 1TV 2电影
    :return True or False, name
    """
    def __getmediatmdbname__(self, type : int, id):
        try:
            for language in self.languagelist:
                if type == 1:
                    ret, tvinfo = self.tmdbclient.gettvinfo(tvid=id, language=language)
                    if ret == False:
                        print('获取TMDB媒体信息失败, {}'.format(self.tmdbclient.err))
                        continue
                    if self.__ischinese__(string=tvinfo['name']):
                        return True, tvinfo['name']
                    else:
                        ret, name = self.__alternativename__(alternativetitles=tvinfo)
                        if ret == False:
                            continue
                        return True, name
                else:
                    ret, movieinfo = self.tmdbclient.getmoveinfo(movieid=id, language=language)
                    if ret == False:
                        print('获取TMDB媒体信息失败, {}'.format(self.tmdbclient.err))
                        continue
                    if self.__ischinese__(string=movieinfo['title']):
                        return True, movieinfo['title']
                    else:
                        ret, name = self.__alternativename__(alternativetitles=movieinfo)
                        if ret == False:
                            continue
                        return True, name
                    
            return False, None
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    """
    获取任务tmdb中文
    :param personid 人物ID
    :return True or False, name
    """
    def __getpersontmdbname(self, personid):
        try:
            for language in self.languagelist:
                ret, personinfo = self.tmdbclient.getpersoninfo(personid=personid, language=language)
                if ret == False:
                    print('获取TMDB人物信息失败, {}'.format(self.tmdbclient.err))
                    continue
                for name in personinfo['also_known_as']:
                    if not self.__ischinese__(string=name):
                        continue
                    
                    return True, str(name).replace(" ", "")
            return False, None
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None

    """
    返回别名中文名称
    :return True or False, name
    """
    def __alternativename__(self, alternativetitles):
        try:
            for title in alternativetitles['alternative_titles']['titles']:
                if 'iso_3166_1' not in title:
                    continue
                if title['iso_3166_1'] != 'CN':
                    continue
                if not self.__ischinese__(string=title['title']):
                    continue
                return True, title['title']
        except Exception as result:
            self.err = "异常错误：{}".format(result)
            return False, None


    """
    判断是否包含中文
    :return True or False
    """
    def __ischinese__(self, string : str):
        for ch in string:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        if re.match(pattern='^[0-9]+$', string=string):
            return True
        return False