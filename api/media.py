import re
import time
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore

import zhconv

from api.douban import douban
from api.mediasql import mediasql
from api.nastools import nastools
from api.server.emby import emby
from api.server.jellyfin import jellyfin
from api.server.plex import plex
from api.tmdb import tmdb
from system.config import Config
from system.log import log


class media:
    media_server_type = None
    nas_tools_client = None
    meidia_server_client = None
    tmdb_client = None
    douban_client = None
    language_list = None
    thread_pool = None
    update_people = None
    update_overview = None
    update_season_group = None
    douban_api_space = None
    del_not_image_people = None
    check_media_search = None
    config_load = None
    sql_client = None
    config_info = None
    thread_num = None
    semaphore = None
    exclude_path = None
    exclude_media = None
    update_title = None
    update_score = None

    def __init__(self) -> None:
        """
        :param configinfo 配置
        """
        try:
            self.config_info = Config().get_config()
            self.media_server_type = self.config_info["system"]["mediaserver"]
            self.config_load = False
            self.sql_client = mediasql()
            self.nas_tools_client = nastools(
                host=self.config_info["api"]["nastools"]["host"],
                authorization=self.config_info["api"]["nastools"]["authorization"],
                username=self.config_info["api"]["nastools"]["username"],
                passwd=self.config_info["api"]["nastools"]["passwd"],
            )

            self.tmdb_client = tmdb(
                key=self.config_info["api"]["tmdb"]["key"],
                host=self.config_info["api"]["tmdb"].get(
                    "host", "https://api.themoviedb.org/3"
                ),
                proxy=self.config_info["api"]["tmdb"].get("proxy", None),
            )
            self.douban_client = douban(
                key=self.config_info["api"]["douban"]["key"],
                cookie=self.config_info["api"]["douban"]["cookie"],
            )
            self.language_list = ["zh-CN", "zh-SG", "zh-TW", "zh-HK"]
            self.thread_num = self.config_info["system"]["threadnum"]
            self.semaphore = BoundedSemaphore(self.thread_num)
            self.thread_pool = ThreadPoolExecutor(max_workers=self.thread_num)
            self.update_people = self.config_info["system"]["updatepeople"]
            self.update_overview = self.config_info["system"]["updateoverview"]
            self.douban_api_space = self.config_info["system"]["doubanapispace"]
            self.del_not_image_people = self.config_info["system"]["delnotimagepeople"]
            self.update_season_group = self.config_info["system"]["updateseasongroup"]
            self.check_media_search = self.config_info["system"]["checkmediasearch"]
            self.exclude_path = self.config_info["system"]["excludepath"]
            self.exclude_media = self.config_info["system"]["excludemedia"]
            self.update_title = self.config_info["system"]["updatetitle"]
            self.update_score = self.config_info["system"]["updatescore"]
            if "Emby" in self.media_server_type:
                self.meidia_server_client = emby(
                    host=self.config_info["api"]["emby"]["host"],
                    userid=self.config_info["api"]["emby"]["userid"],
                    key=self.config_info["api"]["emby"]["key"],
                )
                self.config_load = True
            elif "Jellyfin" in self.media_server_type:
                self.meidia_server_client = jellyfin(
                    host=self.config_info["api"]["jellyfin"]["host"],
                    userid=self.config_info["api"]["jellyfin"]["userid"],
                    key=self.config_info["api"]["jellyfin"]["key"],
                )
                self.config_load = True
            elif "Plex" in self.media_server_type:
                self.meidia_server_client = plex(
                    host=self.config_info["api"]["plex"]["host"],
                    userid="",
                    key=self.config_info["api"]["plex"]["key"],
                )
                self.config_load = True
            else:
                log().logger.info(
                    "当前设置媒体服务器[{}]不支持".format(self.media_server_type)
                )
                self.config_load = False

        except Exception as result:
            log().logger.info("配置异常错误, {}".format(result))

    def start_scan_media(self):
        """
        开始扫描媒体
        :return True or False
        """
        if not self.config_load:
            log().logger.info("配置未正常加载")
            return False
        # 获取媒体库根文件夹
        ret, itmes = self.meidia_server_client.get_items()
        if not ret:
            log().logger.info(
                "获取[{}]媒体总列表失败, {}".format(
                    self.media_server_type, self.meidia_server_client.err
                )
            )
            return False
        ret, iteminfo = self.meidia_server_client.get_items_count()
        log().logger.info(
            "总媒体数量[{}]".format(iteminfo["MovieCount"] + iteminfo["SeriesCount"])
        )
        if not ret:
            log().logger.info(
                "获取[{}]媒体数量失败, {}".format(
                    self.media_server_type, self.meidia_server_client.err
                )
            )
            return False

        ret = True

        for item in self.__check_media_info__(itemlist=itmes):
            if not item:
                continue
            self.__submit_task__(item=item)
        while self.semaphore._value != self.thread_num:
            time.sleep(0.1)
        return ret

    def __submit_task__(self, item):
        """
        提交任务
        :param item
        """
        self.semaphore.acquire()
        self.thread_pool.submit(self.__start_task__, item)

    def __start_task__(self, item):
        """
        开始任务
        :param item
        """
        ret, name = self.__to_deal_with_item__(item=item)
        if ret:
            log().logger.info("媒体[{}]处理完成".format(name))
        else:
            log().logger.info("媒体[{}]处理失败".format(name))
        self.semaphore.release()

    def __check_media_info__(self, itemlist):
        """
        检查媒体信息
        :param itemlist 项目列表
        :return True or False
        """
        try:
            for item in itemlist["Items"]:
                if "Folder" in item["Type"] and (
                    "CollectionType" not in item
                    or "boxsets" not in item["CollectionType"]
                ):
                    # 排除文件夹
                    is_exclude_media = False
                    for exclude in self.exclude_path:
                        match = re.match(exclude, item["Name"])
                        if match:
                            is_exclude_media = True
                            break
                    if is_exclude_media:
                        log().logger.info(
                            "排除[{}]媒体文件夹[{}]".format(
                                self.media_server_type,
                                item["Name"],
                            )
                        )
                        continue
                    ret, items = self.meidia_server_client.get_items(
                        parentid=item["Id"]
                    )
                    if not ret:
                        log().logger.info(
                            "获取[{}]媒体[{}]ID[{}]列表失败, {}".format(
                                self.media_server_type,
                                item["Name"],
                                item["Id"],
                                self.meidia_server_client.err,
                            )
                        )
                        continue
                    for tmpitem in self.__check_media_info__(itemlist=items):
                        yield tmpitem
                else:
                    if "Series" in item["Type"] or "Movie" in item["Type"]:
                        # 排除文件夹
                        is_exclude_media = False
                        for exclude in self.exclude_media:
                            match = re.match(exclude, item["Name"])
                            if match:
                                is_exclude_media = True
                                break
                        if is_exclude_media:
                            log().logger.info(
                                "排除[{}]媒体[{}]".format(
                                    self.media_server_type,
                                    item["Name"],
                                )
                            )
                            continue
                        yield item

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )

        yield {}

    def __check_media_info_search__(self, item):
        """
        检查媒体信息搜索是否正确
        :param item 媒体信息
        """
        try:
            ret, iteminfo = self.meidia_server_client.get_item_info(itemid=item["Id"])
            if not ret:
                log().logger.info(
                    "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                        self.media_server_type,
                        item["Name"],
                        item["Id"],
                        self.meidia_server_client.err,
                    )
                )
                return False
            tmdbid = ""
            if "Tmdb" in iteminfo["ProviderIds"]:
                tmdbid = iteminfo["ProviderIds"]["Tmdb"]
            elif "tmdb" in iteminfo["ProviderIds"]:
                tmdbid = iteminfo["ProviderIds"]["tmdb"]
            name = re.sub(
                pattern="\\s+-\\s+\\d{1,4}[k|K|p|P]|\\s+\\(\\d{4}\\)|\\.\\S{1,4}$",
                repl="",
                string=iteminfo["FileName"],
            )
            year = None
            redata = re.search(pattern="\\((\\d{4})\\)", string=iteminfo["FileName"])
            if redata:
                year = redata.group(1)
            if (
                name in item["Name"]
                and (
                    year
                    and "ProductionYear" in iteminfo
                    and year in str(iteminfo["ProductionYear"])
                )
                and tmdbid
            ):
                return True
            mediatype = "MOV"
            if "Movie" in item["Type"]:
                mediatype = "MOV"
            else:
                mediatype = "TV"
            ret, mediainfo = self.nas_tools_client.media_info(
                name=name, year=year, type=mediatype
            )
            if not ret:
                log().logger.info(
                    "[{}]媒体名称[{}]与原始名称[{}]不一致可能识别错误, NasTools识别媒体[{}]失败, {}".format(
                        self.media_server_type,
                        item["Name"],
                        iteminfo["FileName"],
                        name,
                        self.nas_tools_client.err,
                    )
                )
                return False
            testtmdbid = None
            if year and year != mediainfo["year"]:
                return False
            if mediainfo["tmdbid"] > 0:
                testtmdbid = str(mediainfo["tmdbid"])
            if not testtmdbid or tmdbid == testtmdbid:
                return True
            if "Series" in item["Type"]:
                ret, tvinfo = self.__get_tmdb_media_info__(
                    mediatype=1, name=item["Name"], id=testtmdbid
                )
                if not ret:
                    return False
                if len(tvinfo["seasons"]) < iteminfo["ChildCount"]:
                    return False

            ret, searchinfo = self.meidia_server_client.search_movie(
                itemid=item["Id"], tmdbid=testtmdbid, name=name, year=year
            )
            if not ret:
                log().logger.info(
                    "[{}]搜索媒体[{}]ID[{}]TMDB[{}]信息失败, {}".format(
                        self.media_server_type,
                        item["Name"],
                        item["Id"],
                        testtmdbid,
                        self.meidia_server_client.err,
                    )
                )
                return False
            for info in searchinfo:
                if "Plex" not in self.media_server_type:
                    info["Type"] = iteminfo["Type"]
                    info["IsFolder"] = iteminfo["IsFolder"]
                ret = self.meidia_server_client.apply_search(
                    itemid=item["Id"], iteminfo=info
                )
                if not ret:
                    log().logger.info(
                        "[{}]更新媒体[{}]ID[{}]TMDB[{}]信息失败, {}".format(
                            self.media_server_type,
                            item["Name"],
                            item["Id"],
                            testtmdbid,
                            self.meidia_server_client.err,
                        )
                    )
                    return False
                log().logger.info(
                    "[{}]更新媒体[{}]ID[{}]TMDB[{}]更新为媒体[{}]TMDB[{}]".format(
                        self.media_server_type,
                        item["Name"],
                        item["Id"],
                        tmdbid,
                        mediainfo["title"],
                        testtmdbid,
                    )
                )
                item["Name"] = mediainfo["title"]
                break
            return True
        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False

    def __to_deal_with_item__(self, item):
        """
        处理媒体
        :param item
        :return True or False
        """
        try:
            if self.check_media_search:
                _ = self.__check_media_info_search__(item=item)

            update_name = False
            update_people = False
            update_overview = False
            update_score = False

            ret, item_info = self.meidia_server_client.get_item_info(itemid=item["Id"])
            if not ret:
                log().logger.info(
                    "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                        self.media_server_type,
                        item["Name"],
                        item["Id"],
                        self.meidia_server_client.err,
                    )
                )
                return False, item["Name"]
            if "LockedFields" not in item_info:
                item_info["LockedFields"] = []
            tmdbid = None
            imdbid = None
            if "Tmdb" in item_info["ProviderIds"]:
                tmdbid = item_info["ProviderIds"]["Tmdb"]
            elif "tmdb" in item_info["ProviderIds"]:
                tmdbid = item_info["ProviderIds"]["tmdb"]

            if "Imdb" in item_info["ProviderIds"]:
                imdbid = item_info["ProviderIds"]["Imdb"]
            elif "imdb" in item_info["ProviderIds"]:
                imdbid = item_info["ProviderIds"]["imdb"]

            douban_media_info = None
            original_name = item_info["Name"]
            if "CommunityRating" not in item_info:
                item_info["CommunityRating"] = "0"
            original_score = item_info["CommunityRating"]
            if self.update_title:
                if not self.__is_chinese__(string=item["Name"]):
                    if not tmdbid and not imdbid:
                        log().logger.info(
                            "[{}]媒体[{}]ID[{}]Tmdb|Imdb不存在".format(
                                self.media_server_type, item["Name"], item["Id"]
                            )
                        )
                        return False, item["Name"]
                    name = None
                    if tmdbid:
                        if "Series" in item["Type"]:
                            ret, name = self.__get_tmdb_media_name__(
                                mediatype=1, datatype=1, name=item["Name"], id=tmdbid
                            )
                        else:
                            ret, name = self.__get_tmdb_media_name__(
                                mediatype=2, datatype=1, name=item["Name"], id=tmdbid
                            )
                    if imdbid and not name:
                        if "Series" in item["Type"]:
                            ret, douban_media_info = self.__get_douban_media_info__(
                                mediatype=1, name=item["Name"], id=imdbid
                            )
                        else:
                            ret, douban_media_info = self.__get_douban_media_info__(
                                mediatype=2, name=item["Name"], id=imdbid
                            )
                        if ret:
                            if self.__is_chinese__(
                                string=douban_media_info["title"], mode=2
                            ):
                                name = douban_media_info["title"]

                    if name:

                        item_info["Name"] = name
                        if "Name" not in item_info["LockedFields"]:
                            item_info["LockedFields"].append("Name")
                        update_name = True

            if self.update_score:
                if imdbid:
                    if not douban_media_info:
                        if "Series" in item["Type"]:
                            ret, douban_media_info = self.__get_douban_media_info__(
                                mediatype=1, name=item["Name"], id=imdbid
                            )
                        else:
                            ret, douban_media_info = self.__get_douban_media_info__(
                                mediatype=2, name=item["Name"], id=imdbid
                            )
                    if douban_media_info:
                        score = douban_media_info["rating"]["value"]
                        if "CommunityRating" not in item_info["LockedFields"]:
                            item_info["LockedFields"].append("CommunityRating")
                        if score > 0 and score != original_score:
                            update_score = True
                            item_info["CommunityRating"] = score

            if self.update_people and "People" in item_info:
                update_people = self.__update_people__(
                    item=item, iteminfo=item_info, imdbid=imdbid
                )

                if "Series" in item["Type"]:
                    ret, seasons = self.meidia_server_client.get_items(
                        parentid=item["Id"], type="Season"
                    )
                    if not ret:
                        log().logger.info(
                            "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                self.media_server_type,
                                item["Name"],
                                item["Id"],
                                self.meidia_server_client.err,
                            )
                        )
                    else:
                        for season in seasons["Items"]:
                            if "Jellyfin" in self.media_server_type:
                                ret, seasoninfo = (
                                    self.meidia_server_client.get_item_info(
                                        itemid=season["Id"]
                                    )
                                )
                                if not ret:
                                    log().logger.info(
                                        "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                            self.media_server_type,
                                            season["Name"],
                                            season["Id"],
                                            self.meidia_server_client.err,
                                        )
                                    )
                                    continue
                                ret = self.__update_people__(
                                    item=season, iteminfo=seasoninfo, imdbid=imdbid
                                )
                                if not ret:
                                    continue
                                if ret:
                                    _ = self.__refresh_people__(
                                        item=season, iteminfo=seasoninfo
                                    )
                                    log().logger.info(
                                        "原始媒体名称[{}] 第[{}]季更新人物".format(
                                            item_info["Name"], season["IndexNumber"]
                                        )
                                    )
                                ret = self.meidia_server_client.set_item_info(
                                    itemid=seasoninfo["Id"], iteminfo=seasoninfo
                                )
                            ret, episodes = self.meidia_server_client.get_items(
                                parentid=season["Id"], type="Episode"
                            )
                            if not ret:
                                log().logger.info(
                                    "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                        self.media_server_type,
                                        season["Name"],
                                        season["Id"],
                                        self.meidia_server_client.err,
                                    )
                                )
                                continue
                            for episode in episodes["Items"]:
                                (
                                    ret,
                                    episodeinfo,
                                ) = self.meidia_server_client.get_item_info(
                                    itemid=episode["Id"]
                                )
                                if not ret:
                                    log().logger.info(
                                        "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                            self.media_server_type,
                                            episode["Name"],
                                            episode["Id"],
                                            self.meidia_server_client.err,
                                        )
                                    )
                                else:
                                    ret = self.__update_people__(
                                        item=episode,
                                        iteminfo=episodeinfo,
                                        imdbid=imdbid,
                                    )
                                    if not ret:
                                        continue
                                    ret = self.meidia_server_client.set_item_info(
                                        itemid=episodeinfo["Id"], iteminfo=episodeinfo
                                    )
                                    if ret:
                                        if "Jellyfin" in self.media_server_type:
                                            _ = self.__refresh_people__(
                                                item=episode, iteminfo=episodeinfo
                                            )
                                        log().logger.info(
                                            "原始媒体名称[{}] 第[{}]季 第[{}]集更新人物".format(
                                                item_info["Name"],
                                                season["IndexNumber"],
                                                episode["IndexNumber"],
                                            )
                                        )

            if self.update_overview:
                if "Overview" not in item_info or not self.__is_chinese__(
                    string=item_info["Overview"]
                ):
                    if not tmdbid and not imdbid:
                        log().logger.info(
                            "[{}]媒体[{}]ID[{}]Tmdb|Imdb不存在".format(
                                self.media_server_type, item["Name"], item["Id"]
                            )
                        )
                        return False, item["Name"]
                    ret = False
                    if tmdbid:
                        if "Series" in item["Type"]:
                            ret, overview = self.__get_tmdb_media_name__(
                                mediatype=1, datatype=2, name=item["Name"], id=tmdbid
                            )
                        else:
                            ret, overview = self.__get_tmdb_media_name__(
                                mediatype=2, datatype=2, name=item["Name"], id=tmdbid
                            )
                    if ret:
                        item_info["Overview"] = overview
                        if "Overview" not in item_info["LockedFields"]:
                            item_info["LockedFields"].append("Overview")
                        update_overview = True
                    elif imdbid:
                        if not douban_media_info:
                            if "Series" in item["Type"]:
                                ret, douban_media_info = self.__get_douban_media_info__(
                                    mediatype=1, name=item["Name"], id=imdbid
                                )
                            else:
                                ret, douban_media_info = self.__get_douban_media_info__(
                                    mediatype=2, name=item["Name"], id=imdbid
                                )
                        if douban_media_info:
                            if douban_media_info["intro"]:
                                item_info["Overview"] = douban_media_info["intro"]
                                if "Overview" not in item_info["LockedFields"]:
                                    item_info["LockedFields"].append("Overview")
                                update_overview = True

                if "Series" in item["Type"]:
                    ret, seasons = self.meidia_server_client.get_items(
                        parentid=item["Id"], type="Season"
                    )
                    if not ret:
                        log().logger.info(
                            "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                self.media_server_type,
                                item["Name"],
                                item["Id"],
                                self.meidia_server_client.err,
                            )
                        )
                    else:
                        seasongroupinfo = None
                        groupid = None
                        if self.update_season_group:
                            for groupinfo in self.config_info["system"]["seasongroup"]:
                                infolist = groupinfo.split("|")
                                if len(infolist) < 2:
                                    continue
                                if infolist[0] == item["Name"]:
                                    groupid = infolist[1]
                                    break
                        for season in seasons["Items"]:
                            ret, episodes = self.meidia_server_client.get_items(
                                parentid=season["Id"], type="Episode"
                            )
                            if not ret:
                                log().logger.info(
                                    "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                        self.media_server_type,
                                        season["Name"],
                                        season["Id"],
                                        self.meidia_server_client.err,
                                    )
                                )
                                continue
                            for episode in episodes["Items"]:
                                (
                                    ret,
                                    episodeinfo,
                                ) = self.meidia_server_client.get_item_info(
                                    itemid=episode["Id"]
                                )
                                if not ret:
                                    log().logger.info(
                                        "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                                            self.media_server_type,
                                            episode["Name"],
                                            episode["Id"],
                                            self.meidia_server_client.err,
                                        )
                                    )
                                else:
                                    imageurl = None
                                    name = None
                                    overview = None
                                    ommunityrating = None
                                    if not groupid:
                                        if (
                                            "Overview" not in episodeinfo
                                            or not self.__is_chinese__(
                                                string=episodeinfo["Overview"]
                                            )
                                        ):
                                            (
                                                ret,
                                                name,
                                                overview,
                                                ommunityrating,
                                                imageurl,
                                            ) = self.__get_tmdb_tv_season_info__(
                                                name=item["Name"],
                                                tvid=tmdbid,
                                                seasonid=season["IndexNumber"],
                                                episodeid=episode["IndexNumber"],
                                            )
                                            if not ret:
                                                continue
                                    else:
                                        if not seasongroupinfo:
                                            (
                                                ret,
                                                seasongroupinfo,
                                            ) = self.__get_tmdb_tv_season_group_info__(
                                                name=item["Name"], groupid=groupid
                                            )
                                            if not ret:
                                                continue
                                        tmdbepisodeinfo = None
                                        for seasondata in seasongroupinfo["groups"]:
                                            if (
                                                seasondata["order"]
                                                != season["IndexNumber"]
                                            ):
                                                continue
                                            for episodedata in seasondata["episodes"]:
                                                if (
                                                    episodedata["order"] + 1
                                                    != episode["IndexNumber"]
                                                ):
                                                    continue
                                                tmdbepisodeinfo = episodedata
                                                break
                                            if tmdbepisodeinfo:
                                                break
                                        if not tmdbepisodeinfo:
                                            log().logger.info(
                                                "原始媒体名称[{}] 第[{}]季 第[{}]集未匹配到TMDB剧集组数据".format(
                                                    item_info["Name"],
                                                    season["IndexNumber"],
                                                    episode["IndexNumber"],
                                                )
                                            )
                                            continue
                                        if (
                                            tmdbepisodeinfo["name"]
                                            != episodeinfo["Name"]
                                        ):
                                            name = tmdbepisodeinfo["name"]
                                        if (
                                            "Overview" not in episodeinfo
                                            or tmdbepisodeinfo["overview"]
                                            != episodeinfo["Overview"]
                                        ):
                                            overview = tmdbepisodeinfo["overview"]
                                        if (
                                            "still_path" in tmdbepisodeinfo
                                            and tmdbepisodeinfo["still_path"]
                                        ):
                                            imageurl = "https://www.themoviedb.org/t/p/original{}".format(
                                                tmdbepisodeinfo["still_path"]
                                            )
                                        if (
                                            "CommunityRating" not in episodeinfo
                                            or episodeinfo["CommunityRating"]
                                            != tmdbepisodeinfo["vote_average"]
                                        ):
                                            ommunityrating = tmdbepisodeinfo[
                                                "vote_average"
                                            ]

                                    if not name and not overview and not ommunityrating:
                                        continue
                                    if "LockedFields" not in episodeinfo:
                                        episodeinfo["LockedFields"] = []
                                    if name:
                                        episodeinfo["Name"] = name
                                    if overview:
                                        episodeinfo["Overview"] = overview
                                    if ommunityrating:
                                        episodeinfo["CommunityRating"] = ommunityrating
                                    if "Name" not in episodeinfo["LockedFields"]:
                                        episodeinfo["LockedFields"].append("Name")
                                    if "Overview" not in episodeinfo["LockedFields"]:
                                        episodeinfo["LockedFields"].append("Overview")
                                    ret = self.meidia_server_client.set_item_info(
                                        itemid=episodeinfo["Id"], iteminfo=episodeinfo
                                    )
                                    if ret:
                                        if overview:
                                            log().logger.info(
                                                "原始媒体名称[{}] 第[{}]季 第[{}]集更新概述".format(
                                                    item_info["Name"],
                                                    season["IndexNumber"],
                                                    episode["IndexNumber"],
                                                )
                                            )
                                        if ommunityrating:
                                            log().logger.info(
                                                "原始媒体名称[{}] 第[{}]季 第[{}]集更新评分".format(
                                                    item_info["Name"],
                                                    season["IndexNumber"],
                                                    episode["IndexNumber"],
                                                )
                                            )
                                    if imageurl:
                                        ret = self.meidia_server_client.set_item_image(
                                            itemid=episodeinfo["Id"], imageurl=imageurl
                                        )
                                        if ret:
                                            log().logger.info(
                                                "原始媒体名称[{}] 第[{}]季 第[{}]集更新图片".format(
                                                    item_info["Name"],
                                                    season["IndexNumber"],
                                                    episode["IndexNumber"],
                                                )
                                            )

            if (
                not update_name
                and not update_people
                and not update_overview
                and not update_score
            ):
                return True, item["Name"]
            ret = self.meidia_server_client.set_item_info(
                itemid=item_info["Id"], iteminfo=item_info
            )
            if ret:
                if update_name:
                    log().logger.info(
                        "原始媒体名称[{}]更新为[{}]".format(
                            original_name, item_info["Name"]
                        )
                    )
                if update_score:
                    log().logger.info(
                        "原始媒体名称[{}]更新豆瓣评分[{}]".format(
                            item_info["Name"], item_info["CommunityRating"]
                        )
                    )
                if update_people:
                    if "Jellyfin" in self.media_server_type:
                        _ = self.__refresh_people__(item=item, iteminfo=item_info)
                    log().logger.info(
                        "原始媒体名称[{}]更新人物".format(item_info["Name"])
                    )
                if update_overview:
                    log().logger.info(
                        "原始媒体名称[{}]更新概述".format(item_info["Name"])
                    )

            return True, item["Name"]

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, item["Name"]

    def __refresh_people__(self, item, iteminfo):
        """
        刷新人物元数据
        :param iteminfo 项目信息
        :return True of False
        """
        try:
            ret, newiteminfo = self.meidia_server_client.get_item_info(
                itemid=item["Id"]
            )
            if not ret:
                log().logger.info(
                    "获取[{}]媒体[{}]ID[{}]信息失败, {}".format(
                        self.media_server_type,
                        item["Name"],
                        item["Id"],
                        self.meidia_server_client.err,
                    )
                )
                return False
            for people, newpeople in zip(iteminfo["People"], newiteminfo["People"]):
                if (
                    people["Id"] in newpeople["Id"]
                    or people["Name"] not in newpeople["Name"]
                ):
                    continue
                ret, peopleinfo = self.meidia_server_client.get_item_info(
                    itemid=people["Id"]
                )
                if not ret:
                    log().logger.info(
                        "获取[{}]人物信息失败, {}".format(
                            self.media_server_type, self.meidia_server_client.err
                        )
                    )
                    continue
                ret, newpeopleinfo = self.meidia_server_client.get_item_info(
                    itemid=newpeople["Id"]
                )
                if not ret:
                    log().logger.info(
                        "获取[{}]人物信息失败, {}".format(
                            self.media_server_type, self.meidia_server_client.err
                        )
                    )
                    continue
                newpeopleinfo["ProviderIds"] = peopleinfo["ProviderIds"]
                ret = self.meidia_server_client.set_item_info(
                    itemid=newpeopleinfo["Id"], iteminfo=newpeopleinfo
                )
                if not ret:
                    log().logger.info(
                        "更新[{}]人物信息失败, {}".format(
                            self.media_server_type, self.meidia_server_client.err
                        )
                    )
                    continue
                ret, newpeopleinfo = self.meidia_server_client.get_item_info(
                    itemid=newpeople["Id"]
                )
                if not ret:
                    log().logger.info(
                        "获取[{}]人物信息失败, {}".format(
                            self.media_server_type, self.meidia_server_client.err
                        )
                    )
                    continue
                """
                ret = self.meidiaserverclient.refresh(peopleinfo['Id'])
                if not ret:
                    log().logger.info('刷新[{}]人物信息失败, {}'.format(self.mediaservertype, self.meidiaserverclient.err))
                """

            return True
        except Exception as result:
            log().logger.info("异常错误: {}".format(result))
        return False

    def __update_people__(self, item, iteminfo, imdbid):
        """
        更新人物
        :param item 项目
        :param iteminfo 项目信息
        :param imdbid IMDB ID
        :return True of False
        """
        updatepeople = False
        try:
            doubanmediainfo = None
            doubancelebritiesinfo = None
            needdelpeople = []
            for people in iteminfo["People"]:
                ret, peopleinfo = self.meidia_server_client.get_item_info(
                    itemid=people["Id"]
                )
                if not ret:
                    log().logger.info(
                        "获取[{}]人物信息失败, {}".format(
                            self.media_server_type, self.meidia_server_client.err
                        )
                    )
                    continue

                peopleimdbid = None
                peopletmdbid = None
                peoplename = None
                if "Tmdb" in peopleinfo["ProviderIds"]:
                    peopletmdbid = peopleinfo["ProviderIds"]["Tmdb"]
                elif "tmdb" in peopleinfo["ProviderIds"]:
                    peopletmdbid = peopleinfo["ProviderIds"]["tmdb"]

                if "Imdb" in peopleinfo["ProviderIds"]:
                    peopleimdbid = peopleinfo["ProviderIds"]["Imdb"]
                elif "imdb" in peopleinfo["ProviderIds"]:
                    peopleimdbid = peopleinfo["ProviderIds"]["imdb"]

                if not self.__is_chinese__(string=people["Name"], mode=1):
                    if "LockedFields" not in peopleinfo:
                        peopleinfo["LockedFields"] = []

                    if not peopletmdbid and not peopleimdbid:
                        log().logger.info(
                            "[{}]人物[{}]ID[{}]Tmdb|Imdb不存在".format(
                                self.media_server_type,
                                peopleinfo["Name"],
                                peopleinfo["Id"],
                            )
                        )
                        needdelpeople.append(peopleinfo["Id"])
                        continue

                    if peopleimdbid and imdbid:
                        if not doubanmediainfo:
                            if "Series" in item["Type"]:
                                ret, doubanmediainfo = self.__get_douban_media_info__(
                                    mediatype=1, name=item["Name"], id=imdbid
                                )
                            else:
                                ret, doubanmediainfo = self.__get_douban_media_info__(
                                    mediatype=2, name=item["Name"], id=imdbid
                                )

                        if doubanmediainfo and not doubancelebritiesinfo:
                            if "Series" in item["Type"]:
                                (
                                    ret,
                                    doubancelebritiesinfo,
                                ) = self.__get_douban_media_celebrities_info__(
                                    mediatype=1,
                                    name=item["Name"],
                                    id=doubanmediainfo["id"],
                                )
                            else:
                                (
                                    ret,
                                    doubancelebritiesinfo,
                                ) = self.__get_douban_media_celebrities_info__(
                                    mediatype=2,
                                    name=item["Name"],
                                    id=doubanmediainfo["id"],
                                )

                        if doubancelebritiesinfo:
                            ret, celebrities = self.__get_people_info__(
                                celebritiesinfo=doubancelebritiesinfo,
                                people=people,
                                imdbid=peopleimdbid,
                            )
                            if ret and self.__is_chinese__(string=celebrities["name"]):
                                peoplename = re.sub(
                                    pattern="\\s+", repl="", string=celebrities["name"]
                                )
                    if not peoplename:
                        if self.__is_chinese__(string=peopleinfo["Name"], mode=2):
                            peoplename = re.sub(
                                pattern="\\s+", repl="", string=peopleinfo["Name"]
                            )
                            peoplename = zhconv.convert(peopleinfo["Name"], "zh-cn")
                        elif peopletmdbid:
                            ret, peoplename = self.__get_tmdb_person_name(
                                name=peopleinfo["Name"], personid=peopletmdbid
                            )

                    if peoplename:
                        originalpeoplename = people["Name"]
                        peopleinfo["Name"] = peoplename
                        if "Name" not in peopleinfo["LockedFields"]:
                            peopleinfo["LockedFields"].append("Name")
                        people["Name"] = peoplename
                        if "Emby" in self.media_server_type:
                            ret = self.meidia_server_client.set_item_info(
                                itemid=peopleinfo["Id"], iteminfo=peopleinfo
                            )
                        else:
                            ret = True
                        if ret:
                            log().logger.info(
                                "原始人物名称[{}]更新为[{}]".format(
                                    originalpeoplename, peoplename
                                )
                            )
                            updatepeople = True
                elif "Role" not in people or not self.__is_chinese__(
                    string=people["Role"], mode=2
                ):
                    if imdbid:
                        if not doubanmediainfo:
                            if "Series" in item["Type"]:
                                ret, doubanmediainfo = self.__get_douban_media_info__(
                                    mediatype=1, name=item["Name"], id=imdbid
                                )
                            else:
                                ret, doubanmediainfo = self.__get_douban_media_info__(
                                    mediatype=2, name=item["Name"], id=imdbid
                                )

                        if doubanmediainfo and not doubancelebritiesinfo:
                            if "Series" in item["Type"]:
                                (
                                    ret,
                                    doubancelebritiesinfo,
                                ) = self.__get_douban_media_celebrities_info__(
                                    mediatype=1,
                                    name=item["Name"],
                                    id=doubanmediainfo["id"],
                                )
                            else:
                                (
                                    ret,
                                    doubancelebritiesinfo,
                                ) = self.__get_douban_media_celebrities_info__(
                                    mediatype=2,
                                    name=item["Name"],
                                    id=doubanmediainfo["id"],
                                )

                        if peopleimdbid and doubanmediainfo and doubancelebritiesinfo:
                            ret, celebrities = self.__get_people_info__(
                                celebritiesinfo=doubancelebritiesinfo,
                                people=people,
                                imdbid=peopleimdbid,
                            )
                            if ret:
                                if self.__is_chinese__(
                                    string=re.sub(
                                        pattern="饰\\s+",
                                        repl="",
                                        string=celebrities["character"],
                                    )
                                ):
                                    people["Role"] = re.sub(
                                        pattern="饰\\s+",
                                        repl="",
                                        string=celebrities["character"],
                                    )
                                    updatepeople = True
                                doubanname = re.sub(
                                    pattern="\\s+", repl="", string=celebrities["name"]
                                )
                                if doubanname.find("演员") != -1:
                                    continue
                                if people["Name"] != doubanname and self.__is_chinese__(
                                    string=doubanname
                                ):
                                    originalpeoplename = people["Name"]
                                    peopleinfo["Name"] = doubanname
                                    people["Name"] = doubanname
                                    if "Emby" in self.media_server_type:
                                        ret = self.meidia_server_client.set_item_info(
                                            itemid=peopleinfo["Id"], iteminfo=peopleinfo
                                        )
                                    else:
                                        ret = True
                                    if ret:
                                        log().logger.info(
                                            "原始人物名称[{}]更新为[{}]".format(
                                                originalpeoplename, people["Name"]
                                            )
                                        )
                                        updatepeople = True

            if "Emby" in self.media_server_type:
                peoplelist = []
                peoples = []
                for people in iteminfo["People"]:
                    if self.del_not_image_people:
                        if "PrimaryImageTag" not in people:
                            updatepeople = True
                            continue
                    if people["Name"] + people["Type"] not in peoplelist:
                        peoplelist.append(people["Name"] + people["Type"])
                        peoples.append(people)
                    else:
                        updatepeople = True
                iteminfo["People"] = peoples

            if needdelpeople:
                peoples = []
                for people in iteminfo["People"]:
                    if people["Id"] in needdelpeople:
                        continue
                    peoples.append(people)

                iteminfo["People"] = peoples
                updatepeople = True

        except Exception as result:
            log().logger.info("异常错误: {}".format(result))
        return updatepeople

    def __get_people_info__(self, celebritiesinfo, people, imdbid):
        """
        获取人物信息
        :param celebritiesinfo 演员信息
        :param 人物信息
        :param imdbid
        :return True of False, celebrities
        """
        try:
            if people["Type"] == "Director":
                for celebrities in celebritiesinfo["directors"]:
                    if "info" not in celebrities:
                        continue
                    haspeople = False
                    for imdb in celebrities["info"]["extra"]["info"]:
                        if imdb[0] != "IMDb编号":
                            continue
                        if imdb[1] == imdbid:
                            haspeople = True
                            break

                    if haspeople:
                        return True, celebrities

                for celebrities in celebritiesinfo["directors"]:
                    if (
                        people["Name"] == celebrities["name"]
                        or people["Name"] == celebrities["latin_name"]
                    ):
                        return True, celebrities

            if people["Type"] == "Actor":
                for celebrities in celebritiesinfo["actors"]:
                    if "info" not in celebrities:
                        continue
                    haspeople = False
                    for imdb in celebrities["info"]["extra"]["info"]:
                        if imdb[0] != "IMDb编号":
                            continue
                        if imdb[1] == imdbid:
                            haspeople = True
                            break

                    if haspeople:
                        return True, celebrities

                for celebrities in celebritiesinfo["actors"]:
                    if (
                        people["Name"] == celebrities["name"]
                        or people["Name"] == celebrities["latin_name"]
                    ):
                        return True, celebrities

        except Exception as result:
            log().logger.info("异常错误: {}".format(result))
        return False, None

    def __get_douban_media_celebrities_info__(self, mediatype: int, name: str, id: str):
        """
        获取豆瓣媒体演员信息
        :param mediatype 媒体类型 1TV 2电影
        :name name 媒体名称
        :id id 媒体ID
        :return True or False, celebritiesinfo
        """
        try:
            ret, celebritiesinfo = self.sql_client.get_douban_celebrities_info(
                mediatype=mediatype, id=id
            )
            if not ret:
                if mediatype == 1:
                    ret, celebritiesinfo = self.douban_client.get_tv_celebrities_info(
                        tvid=id
                    )
                else:
                    ret, celebritiesinfo = (
                        self.douban_client.get_movie_celebrities_info(movieid=id)
                    )
                if not ret:
                    log().logger.info(
                        "获取豆瓣媒体[{}]ID[{}]演员信息失败, {}".format(
                            name, id, self.douban_client.err
                        )
                    )
                    return False, None
                ret = self.sql_client.write_douban_celebrities_info(
                    mediatype=mediatype, id=id, iteminfo=celebritiesinfo
                )
                if not ret:
                    log().logger.info(
                        "保存豆瓣媒体[{}]ID[{}]演员信息失败, {}".format(
                            name, id, self.douban_client.err
                        )
                    )
            for celebrities in celebritiesinfo["directors"]:
                ret, info = self.sql_client.get_douban_people_info(id=celebrities["id"])
                if not ret:
                    ret, info = self.douban_client.get_celebrity_info(
                        celebrityid=celebrities["id"]
                    )
                    if not ret:
                        log().logger.info(
                            "获取豆瓣媒体[{}]ID[{}]演员信息失败, {}".format(
                                name, id, self.douban_client.err
                            )
                        )
                        continue
                    ret = self.sql_client.write_douban_people_info(
                        id=celebrities["id"], iteminfo=info
                    )
                    if not ret:
                        log().logger.info(
                            "获取豆瓣媒体[{}]ID[{}]演员信息失败, {}".format(
                                name, id, self.douban_client.err
                            )
                        )
                celebrities["info"] = info
            for celebrities in celebritiesinfo["actors"]:
                ret, info = self.sql_client.get_douban_people_info(id=celebrities["id"])
                if not ret:
                    ret, info = self.douban_client.get_celebrity_info(
                        celebrityid=celebrities["id"]
                    )
                    if not ret:
                        log().logger.info(
                            "获取豆瓣媒体[{}]ID[{}]演员[{}]ID[{}]信息失败, {}".format(
                                name,
                                id,
                                celebrities["name"],
                                celebrities["id"],
                                self.douban_client.err,
                            )
                        )
                        continue
                    ret = self.sql_client.write_douban_people_info(
                        id=celebrities["id"], iteminfo=info
                    )
                    if not ret:
                        log().logger.info(
                            "保存豆瓣媒体[{}]ID[{}]演员[{}]ID[{}]信息失败, {}".format(
                                name,
                                id,
                                celebrities["name"],
                                celebrities["id"],
                                self.douban_client.err,
                            )
                        )
                celebrities["info"] = info
            return True, celebritiesinfo
        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __get_douban_media_info__(self, mediatype: int, name: str, id: str):
        """
        获取豆瓣媒体信息
        :param mediatype 媒体类型 1TV 2电影
        :name name 媒体名称
        :id imdb
        :return True or False, mediainfo
        """
        try:
            ret, items = self.sql_client.search_douban_media(
                mediatype=mediatype, title=name
            )
            if not ret:
                time.sleep(self.douban_api_space)
                ret, items = self.douban_client.search_media_pc(name)
                if not ret or not items["items"]:
                    time.sleep(self.douban_api_space)
                    ret, items = self.douban_client.search_media(name)
                if not ret or not items["items"]:
                    time.sleep(self.douban_api_space)
                    ret, items = self.douban_client.search_media_weixin(name)
                if not ret or not items["items"]:
                    log().logger.info(
                        "豆瓣搜索媒体[{}]失败, {}".format(
                            name, str(self.douban_client.err)
                        )
                    )
                    return False, None

            for item in items["items"]:
                if mediatype == 1:
                    if "target_type" in item and item["target_type"] != "tv":
                        continue
                elif mediatype == 2:
                    if "target_type" in item and item["target_type"] != "movie":
                        continue
                ret, mediainfo = self.sql_client.get_douban_media_info(
                    mediatype=mediatype, id=item["target_id"]
                )
                if not ret:
                    if mediatype == 2:
                        ret, mediainfo = self.douban_client.get_movie_info(
                            movieid=item["target_id"]
                        )
                    else:
                        ret, mediainfo = self.douban_client.get_tv_info(
                            tvid=item["target_id"]
                        )
                    if not ret:
                        log().logger.info(
                            "获取豆瓣媒体[{}]ID[{}]信息失败, {}".format(
                                item["title"], item["target_id"], self.douban_client.err
                            )
                        )
                        return False, None
                    ret = self.sql_client.write_douban_media_info(
                        mediatype=mediatype, id=item["target_id"], iteminfo=mediainfo
                    )
                    if not ret:
                        log().logger.info(
                            "保存豆瓣媒体[{}]ID[{}]信息失败, {}".format(
                                item["title"], item["target_id"], self.douban_client.err
                            )
                        )
                if "IMDb" not in mediainfo["info"]:
                    continue
                if mediainfo["info"]["IMDb"] == id:
                    ret = self.sql_client.write_douban_media(
                        mediatype=mediatype, id=item["target_id"], iteminfo=item
                    )
                    if not ret:
                        log().logger.info(
                            "保存豆瓣媒体[{}]ID[{}]信息失败, {}".format(
                                item["title"], item["target_id"], self.douban_client.err
                            )
                        )
                    return True, mediainfo

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __get_tmdb_media_info__(
        self, mediatype: int, name: str, id: str, language: str = "zh-CN"
    ):
        """
        获取tmdb媒体信息
        :param mediatype 媒体类型 1TV 2电影
        :name name 媒体名称
        :param id tmdbid
        :return True or False, iteminfo
        """
        try:
            iteminfo = None
            if mediatype == 1:
                ret, iteminfo = self.sql_client.get_tmdb_media_info(
                    mediatype=mediatype, id=id, language=language
                )
                if not ret:
                    ret, iteminfo = self.tmdb_client.get_tv_info(
                        tvid=id, language=language
                    )
                    if not ret:
                        log().logger.info(
                            "获取TMDB媒体[{}]ID[{}]信息失败, {}".format(
                                name, id, self.tmdb_client.err
                            )
                        )
                        return False, None
                    ret = self.sql_client.write_tmdb_media_info(
                        mediatype=mediatype, id=id, language=language, iteminfo=iteminfo
                    )
                    if not ret:
                        log().logger.info(
                            "保存TMDB媒体[{}]ID[{}]信息失败, {}".format(
                                name, id, self.tmdb_client.err
                            )
                        )
                return True, iteminfo
            else:
                ret, iteminfo = self.sql_client.get_tmdb_media_info(
                    mediatype=mediatype, id=id, language=language
                )
                if not ret:
                    ret, iteminfo = self.tmdb_client.get_movie_info(
                        movieid=id, language=language
                    )
                    if not ret:
                        log().logger.info(
                            "获取TMDB媒体[{}]ID[{}]信息失败, {}".format(
                                name, id, self.tmdb_client.err
                            )
                        )
                        return False, None
                    ret = self.sql_client.write_tmdb_media_info(
                        mediatype=mediatype, id=id, language=language, iteminfo=iteminfo
                    )
                    if not ret:
                        log().logger.info(
                            "保存TMDB媒体[{}]ID[{}]信息失败, {}".format(
                                name, id, self.tmdb_client.err
                            )
                        )
                return True, iteminfo

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __get_tmdb_media_name__(
        self, mediatype: int, datatype: int, name: str, id: str
    ):
        """
        获取tmdb媒体中文名称
        :param mediatype 媒体类型 1TV 2电影
        :param datatype 数据类型 1名字 2概述
        :name name 媒体名称
        :param id tmdbid
        :return True or False, name
        """
        try:
            for language in self.language_list:
                if mediatype == 1:
                    ret, tvinfo = self.__get_tmdb_media_info__(
                        mediatype=mediatype, name=name, id=id, language=language
                    )
                    if not ret:
                        continue
                    if datatype == 1:
                        if self.__is_chinese__(string=tvinfo["name"]):
                            if self.__is_chinese__(string=tvinfo["name"], mode=3):
                                return True, zhconv.convert(tvinfo["name"], "zh-cn")
                            return True, tvinfo["name"]
                        else:
                            ret, name = self.__alternative_name__(
                                alternativetitles=tvinfo
                            )
                            if not ret:
                                continue
                            return True, name
                    else:
                        if self.__is_chinese__(string=tvinfo["overview"]):
                            if self.__is_chinese__(string=tvinfo["overview"], mode=3):
                                return True, zhconv.convert(tvinfo["overview"], "zh-cn")
                            return True, tvinfo["overview"]
                else:
                    ret, movieinfo = self.__get_tmdb_media_info__(
                        mediatype=mediatype, name=name, id=id, language=language
                    )
                    if not ret:
                        continue
                    if datatype == 1:
                        if self.__is_chinese__(string=movieinfo["title"]):
                            if self.__is_chinese__(string=movieinfo["title"], mode=3):
                                return True, zhconv.convert(movieinfo["title"], "zh-cn")
                            return True, movieinfo["title"]
                        else:
                            ret, name = self.__alternative_name__(
                                alternativetitles=movieinfo
                            )
                            if not ret:
                                continue
                            return True, name
                    else:
                        if self.__is_chinese__(string=movieinfo["overview"]):
                            if self.__is_chinese__(
                                string=movieinfo["overview"], mode=3
                            ):
                                return True, zhconv.convert(
                                    movieinfo["overview"], "zh-cn"
                                )
                            return True, movieinfo["overview"]

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __get_tmdb_tv_season_group_info__(self, name, groupid):
        """
        获取TMDB电视剧季组信息
        :param name 媒体名称
        :param groupid 组ID
        :return True or False, iteminfo
        """
        try:
            for language in self.language_list:
                ret, iteminfo = self.tmdb_client.get_tv_season_group(
                    groupid=groupid, language=language
                )
                if not ret:
                    log().logger.info(
                        "获取TMDB剧集[{}]组ID[{}]信息失败, {}".format(
                            name, groupid, self.tmdb_client.err
                        )
                    )
                    continue
                return True, iteminfo

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __get_tmdb_tv_season_info__(
        self, name: str, tvid: str, seasonid: str, episodeid: int
    ):
        """
        获取tmdb季中文
        :param name 媒体名称
        :param tvid tmdbid
        :param seasonid 季ID
        :param episodeid 集ID
        :return True or False, name, overview, ommunityrating, imageurl
        """
        try:
            for language in self.language_list:
                ret, seasoninfo = self.sql_client.get_tmdb_season_info(
                    id=tvid, seasonid=seasonid, language=language
                )
                if not ret:
                    ret, seasoninfo = self.tmdb_client.get_tv_season_info(
                        tvid=tvid, seasonid=seasonid, language=language
                    )
                    if not ret:
                        log().logger.info(
                            "获取TMDB媒体[{}]ID[{}]季ID[{}]信息失败, {}".format(
                                name, tvid, seasonid, self.tmdb_client.err
                            )
                        )
                        continue
                    ret = self.sql_client.write_tmdb_season_info(
                        id=tvid,
                        seasonid=seasonid,
                        language=language,
                        iteminfo=seasoninfo,
                    )
                    if not ret:
                        log().logger.info(
                            "保存TMDB媒体[{}]ID[{}]季ID[{}]信息失败, {}".format(
                                name, tvid, seasonid, self.tmdb_client.err
                            )
                        )
                for episodes in seasoninfo["episodes"]:
                    if episodes["episode_number"] > episodeid:
                        break
                    if episodes["episode_number"] != episodeid:
                        continue
                    if self.__is_chinese__(string=episodes["overview"]):
                        name = None
                        overview = None
                        ommunityrating = None
                        imageurl = None
                        if self.__is_chinese__(string=episodes["name"], mode=3):
                            name = zhconv.convert(episodes["name"], "zh-cn")
                        else:
                            name = episodes["name"]
                        if self.__is_chinese__(string=episodes["overview"], mode=3):
                            overview = zhconv.convert(episodes["overview"], "zh-cn")
                        else:
                            overview = episodes["overview"]
                        if episodes["vote_average"] > 0:
                            ommunityrating = episodes["vote_average"]
                        if "still_path" in episodes and episodes["still_path"]:
                            imageurl = (
                                "https://www.themoviedb.org/t/p/original{}".format(
                                    episodes["still_path"]
                                )
                            )
                        return True, name, overview, ommunityrating, imageurl

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None, None, None, None

    def __get_tmdb_person_name(self, name, personid):
        """
        获取tmdb人物中文
        :param name 人物名称
        :param personid 人物ID
        :return True or False, name
        """
        try:
            for language in self.language_list:
                ret, personinfo = self.sql_client.get_tmdb_people_info(
                    id=personid, language=language
                )
                if not ret:
                    ret, personinfo = self.tmdb_client.get_person_info(
                        personid=personid, language=language
                    )
                    if not ret:
                        log().logger.info(
                            "获取TMDB人物[{}]ID[{}]信息失败, {}".format(
                                name, personid, self.tmdb_client.err
                            )
                        )
                        continue
                    ret = self.sql_client.write_tmdb_people_info(
                        id=personid, language=language, iteminfo=personinfo
                    )
                    if not ret:
                        log().logger.info(
                            "保存TMDB人物[{}]ID[{}]信息失败, {}".format(
                                name, personid, self.tmdb_client.err
                            )
                        )
                for name in personinfo["also_known_as"]:
                    if not self.__is_chinese__(string=name, mode=2):
                        continue
                    if self.__is_chinese__(string=name, mode=3):
                        name = zhconv.convert(name, "zh-cn")
                    return True, re.sub(pattern="\\s+", repl="", string=name)
                break

        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __alternative_name__(self, alternativetitles):
        """
        返回别名中文名称
        :return True or False, name
        """
        try:
            if (
                "alternative_titles" not in alternativetitles
                or "titles" not in alternativetitles["alternative_titles"]
            ):
                return False, None
            for title in alternativetitles["alternative_titles"]["titles"]:
                if "iso_3166_1" not in title:
                    continue
                if title["iso_3166_1"] != "CN":
                    continue
                if not self.__is_chinese__(string=title["title"]):
                    continue
                if self.__is_chinese__(string=title["title"], mode=3):
                    return True, zhconv.convert(title["title"], "zh-cn")
                return True, title["title"]
        except Exception as result:
            log().logger.info(
                "异常错误：{}".format(
                    result,
                )
            )
        return False, None

    def __is_chinese__(self, string: str, mode: int = 1):
        """
        判断是否包含中文
        :param string 需要判断的字符
        :param mode 模式 1匹配简体和繁体 2只匹配简体 3只匹配繁体
        :return True or False
        """
        for ch in string:
            if mode == 1:
                if "\u4e00" <= ch <= "\u9FFF":
                    return True
            elif mode == 2:
                if "\u4e00" <= ch <= "\u9FFF":
                    if zhconv.convert(ch, "zh-cn") == ch:
                        return True
            elif mode == 3:
                if "\u4e00" <= ch <= "\u9FFF":
                    if zhconv.convert(ch, "zh-cn") != ch:
                        return True
        if re.search(pattern="^[0-9]+$", string=string):
            return True
        return False
