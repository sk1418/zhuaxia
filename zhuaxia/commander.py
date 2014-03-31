# -*- coding:utf-8 -*-

import sys
import config ,util ,logging ,log,downloader
import xiami as xm
from threadpool import ThreadPool
from time import sleep

LOG = log.get_logger("zxLogger")

dl_songs = []
total = 0
done = 0

def xiami_url_abbr(url):
    return url.replace('http://www.xiami.com/', '...')


def parse_and_prepare(xm_obj, url, verbose=False):
    """ parse the input string (xiami url), and do download"""

    msg = ''
    if '/song/' in url:
        song = xm.Song(xm_obj, url=url)
        dl_songs.append(song)
        msg = 'Parsing: "%s" ..... [Song] %s'% (xiami_url_abbr(url), song.song_name)
    if '/album/' in url:
        album = xm.Album(xm_obj, url)
        dl_songs.extend(album.songs)
        msgs = ['Parsing: "%s" ..... [Album] %s' % (xiami_url_abbr(url),album.album_name)]
        if verbose:
            for s in album.songs:
                msgs.append('[Song] %s'%s.song_name)
            msg = '\n    |-> '.join(msgs)
        else:
            msgs.append('%d songs parsed.' % len(album.songs))
            msg=' => '.join(msgs)

    if '/lib-song/u/' in url:
        fav = xm.Favorite(xm_obj, url)
        dl_songs.extend(fav.songs)
        msgs = ['Parsing: "%s" ..... [Favorite]'% xiami_url_abbr(url)]
        if verbose:
            for s in fav.songs:
                msgs.append('[Song] %s'%s.song_name)
            msg = '\n    |-> '.join(msgs)
        else:
            msgs.append('%d songs parsed.' % len(fav.songs))
            msg = ' => '.join(msgs)

    global total, done
    done +=1
    if not msg:
        #unknown url
        LOG.error('unknown resource url [%s].' % url)
    else:
        pre = ('[%d/%d] ' % (done, total)) if not verbose else ''
        LOG.info('%s%s'% (pre,msg))

def from_file(xm_obj, infile):
    """ download objects (songs, albums...) from an input file.  """

    border = log.hl(u'%s'% ('='*90), 'cyan')
    urls = []
    with open(infile) as f:
        urls = f.readlines() 

    global total, done
    total = len(urls)
    print border
    LOG.info(u' 文件包含链接总数: %d' % total)
    print border
    pool = ThreadPool(config.THREAD_POOL_SIZE)
    for link in urls:
        pool.add_task(parse_and_prepare, xm_obj,link.rstrip('\n'))

    pool.wait_completion()
    print border
    LOG.info(u' 下载任务总数: %d' % len(dl_songs))
    sleep(3)

