# -*- coding:utf-8 -*-

import sys
import config ,util ,logging ,log,downloader
import xiami as xm
import re
from threadpool import ThreadPool
from time import sleep
from os import path

LOG = log.get_logger("zxLogger")

dl_songs = []
total = 0
done = 0

fmt_parsing = u'解析: "%s" ..... [%s] %s' 
fmt_has_song_nm = u'包含%d首歌曲.' 
fmt_single_song = u'[曲目] %s'
border = log.hl(u'%s'% ('='*90), 'cyan')

def shall_I_begin(in_str, is_file=False, is_hq=False):
    xiami_obj = xm.Xiami(config.XIAMI_LOGIN_EMAIL,\
            config.XIAMI_LOGIN_PASSWORD, \
            is_hq)
    if is_file:
        from_file(xiami_obj, in_str)
    else:
        from_url(xiami_obj, in_str)

    print border
    if len(dl_songs):
        LOG.info(u' 下载任务总数: %d \n 3秒后开始下载' % len(dl_songs))
        sleep(3)
        downloader.start_download(dl_songs)
    else:
        LOG.warning(u' 没有可下载任务,自动退出.')


def from_url(xm_obj, url, verbose=True):
    """ parse the input string (xiami url), and do download"""

    LOG.debug('processing url: "%s"'% url)
    msg = u''
    if '/showcollect/id/' in url:
        collect = xm.Collection(xm_obj, url)
        dl_songs.extend(collect.songs)
        msgs = [ fmt_parsing % (xiami_url_abbr(url),u'精选集',collect.collection_name)]
        if verbose:
            for s in collect.songs:
                msgs.append( fmt_single_song % s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append(fmt_has_song_nm % len(collect.songs))
            msg= u' => '.join(msgs)

    elif '/song/' in url:
        song = xm.Song(xm_obj, url=url)
        dl_songs.append(song)
        msg = fmt_parsing % (xiami_url_abbr(url),u'曲目',  song.song_name)
    elif '/album/' in url:
        album = xm.Album(xm_obj, url)
        dl_songs.extend(album.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url),u'专辑',  album.artist_name+u' => '+album.album_name)]
        if verbose:
            for s in album.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append(fmt_has_song_nm % len(album.songs))
            msg= u' => '.join(msgs)

    elif '/lib-song/u/' in url:
        fav = xm.Favorite(xm_obj, url)
        dl_songs.extend(fav.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url), u'用户收藏','')]
        if verbose:
            for s in fav.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append( fmt_has_song_nm % len(fav.songs))
            msg = u' => '.join(msgs)
    elif re.search(r'/artist/\d+', url):
        topsong=xm.TopSong(xm_obj, url)
        dl_songs.extend(topsong.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url), u'艺人热门歌曲',topsong.artist_name)]
        if verbose:
            for s in topsong.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append( fmt_has_song_nm % len(topsong.songs))
            msg = u' => '.join(msgs)
        

    global total, done
    done +=1
    pre = ('[%d/%d] ' % (done, total)) if not verbose else ''
    if not msg:
        #unknown url
        LOG.error(u'%s 不能识别的url [%s].' % (pre,url))
    else:
        LOG.info(u'%s%s'% (pre,msg))

def from_file(xm_obj, infile):
    """ download objects (songs, albums...) from an input file.  """

    urls = []
    with open(infile) as f:
        urls = f.readlines() 

    global total, done
    total = len(urls)
    print border
    LOG.info(u' 文件包含链接总数: %d' % total)
    print border
    pool = ThreadPool(config.THREAD_POOL_SIZE)
    for link in [u for u in urls if u]:
        pool.add_task(from_url, xm_obj,link.rstrip('\n'), verbose=False)

    pool.wait_completion()

def xiami_url_abbr(url):
    return url.replace('http://www.xiami.com/', '...')
