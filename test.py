from media import media
from system.config import config
import os
from system.log import log


if __name__ == '__main__':
    try:
        if 'EMBYTOOLS_CONFIG' not in os.environ:
            os.environ['EMBYTOOLS_CONFIG'] = os.path.join(os.getcwd(), 'config')

        path = os.path.join(os.environ['EMBYTOOLS_CONFIG'], 'config.yaml')
        configinfo = config(path=path)
        mediaclient = media(configinfo=configinfo)
        while True:
            try:
                #ret, mediainfo = mediaclient.nastoolsclient.name_test('[OPFans枫雪动漫][ONE PIECE 海贼王][第1032话][1080p][周日版][MKV][简繁内封]')
                ret, mediainfo = mediaclient.meidiaserverclient.refresh('1145fd62d0c47b15bc6201a503f07c11')
                #ret, mediainfo = mediaclient.doubanclient.search_media_weixin('生化危机')
                #ret, mediainfo = mediaclient.tmdbclient.get_person_info('1796805')
                print(mediainfo)
            except Exception as reuslt:
                log().info(reuslt)
    except Exception as reuslt:
        log().info('异常错误, {}'.format(reuslt))