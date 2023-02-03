import os

from plexapi.server import PlexServer

from api.server.serverbase import serverbase


class plex(serverbase):
    def __init__(self, host : str, userid : str, key : str) -> None:
        """
        :param host
        :param userid
        :param key
        """
        try:
            super().__init__(host=host, userid=userid, key=key)
            self.client = PlexServer(baseurl=host, token=key)
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
    

    def get_items(self, parentid : str = '', type = None):
        """
        获取项目列表
        :param parentid 父文件夹ID
        :param type 类型
        :return True or False, items
        """
        items = {}
        try:
            items['Items'] = []
            if parentid:
                if type and 'Season' in type:
                    plexitem = self.client.library.fetchItem(ekey=parentid)
                    items['Items'] = []
                    for season in plexitem.seasons():
                        item = {}
                        item['Name'] = season.title
                        item['Id'] = season.key
                        item['IndexNumber'] = season.seasonNumber
                        item['Overview'] = season.summary
                        items['Items'].append(item)
                elif type and 'Episode' in type:
                    plexitem = self.client.library.fetchItem(ekey=parentid)
                    items['Items'] = []
                    for episode in plexitem.episodes():
                        item = {}
                        item['Name'] = episode.title
                        item['Id'] = episode.key
                        item['IndexNumber'] = episode.episodeNumber
                        item['Overview'] = episode.summary
                        item['CommunityRating'] = episode.audienceRating
                        items['Items'].append(item)
                else:
                    plexitems = self.client.library.sectionByID(sectionID=parentid)
                    for plexitem in plexitems.all():
                        item = {}
                        if 'movie' in plexitem.METADATA_TYPE:
                            item['Type'] = 'Movie'
                            item['IsFolder'] = False
                        elif 'episode' in plexitem.METADATA_TYPE:
                            item['Type'] = 'Series'
                            item['IsFolder'] = False
                        item['Name'] = plexitem.title
                        item['Id'] = plexitem.key
                        items['Items'].append(item)
            else:
                plexitems = self.client.library.sections()
                for plexitem in plexitems:
                    item = {}
                    if 'Directory' in plexitem.TAG:
                        item['Type'] = 'Folder'
                        item['IsFolder'] = True
                    elif 'movie' in plexitem.METADATA_TYPE:
                        item['Type'] = 'Movie'
                        item['IsFolder'] = False
                    elif 'episode' in plexitem.METADATA_TYPE:
                        item['Type'] = 'Series'
                        item['IsFolder'] = False
                    item['Name'] = plexitem.title
                    item['Id'] = plexitem.key
                    items['Items'].append(item)

            return True, items
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False, items

    def get_items_count(self):
        """
        获取项目数量
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            iteminfo['MovieCount'] = 0
            iteminfo['SeriesCount'] = 0
            items = self.client.library.sections()
            for item in items:
                if 'movie' in item.METADATA_TYPE:
                    iteminfo['MovieCount'] += item.totalSize
                elif 'episode' in item.METADATA_TYPE:
                    iteminfo['SeriesCount'] += item.totalSize
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False, iteminfo

    def get_item_info(self, itemid : str):
        """
        获取项目
        :param itemid 项目ID
        :return True or False, iteminfo
        """
        iteminfo = {}
        try:
            plexitem = self.client.library.fetchItem(ekey=itemid)
            if 'movie' in plexitem.METADATA_TYPE:
                iteminfo['Type'] = 'Movie'
                iteminfo['IsFolder'] = False
            elif 'episode' in plexitem.METADATA_TYPE:
                iteminfo['Type'] = 'Series'
                iteminfo['IsFolder'] = False
                if 'show' in plexitem.TYPE:
                    iteminfo['ChildCount'] = plexitem.childCount
            iteminfo['Name'] = plexitem.title
            iteminfo['Id'] = plexitem.key
            iteminfo['ProductionYear'] = plexitem.year
            iteminfo['ProviderIds'] = {}
            for guid in plexitem.guids:
                idlist = str(guid.id).split(sep='://')
                if len(idlist) < 2:
                    continue
                iteminfo['ProviderIds'][idlist[0]] = idlist[1]
            for location in plexitem.locations:
                iteminfo['Path'] = location
                iteminfo['FileName'] = os.path.basename(location)
            iteminfo['Overview'] = plexitem.summary
            iteminfo['CommunityRating'] = plexitem.audienceRating
            
            """
            iteminfo['People'] = []
            for actor in plexitem.actors:
                people = {}
                people['Id'] = actor.key
                people['Name'] = actor.tag
                people['Role'] = actor.role
                iteminfo['People'].append(people)
            """
            return True, iteminfo
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False, iteminfo

    def set_item_info(self, itemid : str, iteminfo):
        """
        更新项目
        :param iteminfo 项目信息
        :return True or False, iteminfo
        """
        try:
            plexitem = self.client.library.fetchItem(ekey=itemid)
            if 'CommunityRating' in iteminfo:
                edits = {
                    'audienceRating.value': iteminfo['CommunityRating'],
                    'audienceRating.locked': 1
                }
                plexitem.edit(**edits)
            plexitem.editTitle(iteminfo['Name']).editSummary(iteminfo['Overview']).reload()     
            return True
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False

    def set_item_image(self, itemid : str, imageurl : str):
        """
        更新项目图片
        :param imageurl 图片URL
        :return True or False
        """
        try:
            plexitem = self.client.library.fetchItem(ekey=itemid)
            plexitem.uploadPoster(url=imageurl)
            return True
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False

    def search_movie(self, itemid, tmdbid, name = None, year = None):
        """
        搜索视频
        :param itemid 项目ID
        :param tmdbid TMDB ID
        :param name 标题
        :param year 年代
        :return True or False, iteminfo
        """
        iteminfo = []
        try:
            plexitem = self.client.library.fetchItem(ekey=itemid)
            searchinfo = plexitem.matches(title=name, year=year)
            for info in searchinfo:
                if tmdbid:
                    iteminfo.append(info)
                    return True, iteminfo
            for info in searchinfo:
                if name in info.name and year in info.year:
                    iteminfo.append(info)
                    return True, iteminfo
            self.err = '未匹配到结果'
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False, iteminfo
    
    def apply_search(self, itemid, iteminfo):
        """
        应用搜索
        :param itemid 项目ID
        :param iteminfo 项目信息
        :return True or False
        """
        try:
            plexitem = self.client.library.fetchItem(ekey=itemid)
            plexitem.fixMatch(searchResult=iteminfo)
            return True
        except Exception as result:
            self.err = "文件[{}]行[{}]异常错误：{}".format(result.__traceback__.tb_frame.f_globals["__file__"], result.__traceback__.tb_lineno, result)
        return False
    