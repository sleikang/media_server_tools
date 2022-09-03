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
#每次刷新全部媒体间隔时间 [小时]
updatetime = 1

if __name__ == '__main__':
    embymediaclient = embyserver(embyhost=embyhost, embyuserid=embyuserid, embykey=embykey, tmdbkey=tmdbkey)
    while True:
        try:
            embymediaclient.updatemedianame()
            time.sleep(updatetime * 3600)
        except Exception as reuslt:
            print(reuslt)