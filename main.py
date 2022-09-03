import time
from embyserver import embyserver

#EMBY 域名 包含http(s)和端口号后面不带/
#例如https://xxx.xxx.xxx:8920
embyhost = 'https://emby.smwap.top:8920'
#EMBY 用户ID 进EMBY 用户点击管理员账号配置可以在网址上看到userId
embyuserid = 'b88b932533f84f8198418face0236668'
#EMBY APIKEY
embykey = '77bcfc573e5644d5b08d2fa30bac2a9e'
#TMDB APIKEY
tmdbkey = '8dcc68473afb858174575cc7a1af8eb5'
#线程数量
threadnum = 16
#每次刷新全部媒体间隔时间 [小时]
updatetime = 1

if __name__ == '__main__':
    embymediaclient = embyserver(embyhost=embyhost, embyuserid=embyuserid, embykey=embykey, tmdbkey=tmdbkey, threadnum=threadnum)
    while True:
        try:
            embymediaclient.update_media_name()
            time.sleep(updatetime * 3600)
        except Exception as reuslt:
            print(reuslt)