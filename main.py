import time
from embyserver import embyserver

#EMBY 域名 包含http(s)和端口号后面不带/
#例如https://xxx.xxx.xxx:8920
embyhost = ''
#EMBY 用户ID 进EMBY 用户点击管理员账号配置可以在网址上看到userId
embyuserid = ''
#EMBY APIKEY
embykey = ''
#TMDB APIKEY
tmdbkey = ''
#线程数量
threadnum = 16
#是否刷新人名
updatepeople = True
#每次刷新全部媒体间隔时间 [小时]
updatetime = 1

if __name__ == '__main__':
    embymediaclient = embyserver(embyhost=embyhost, embyuserid=embyuserid, embykey=embykey, tmdbkey=tmdbkey, threadnum=threadnum, updatepeople=updatepeople)
    while True:
        try:
            print('开始刷新媒体库元数据')
            embymediaclient.update_media_name()
            print('刷新媒体库元数据完成')
        except Exception as reuslt:
            print(reuslt)