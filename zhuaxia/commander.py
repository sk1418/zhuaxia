# -*- coding:utf-8 -*-

import sys
import config ,util ,logging ,log,downloader
import xiami as xm
import netease
import re
from threadpool import ThreadPool
from time import sleep
from os import path
from threadpool import Terminate_Watcher
from proxypool import ProxyPool

LOG = log.get_logger("zxLogger")

dl_songs = []
total = 0
done = 0

fmt_parsing = u'解析: "%s" ..... [%s] %s' 
fmt_has_song_nm = u'包含%d首歌曲.' 
fmt_single_song = u'[曲目] %s'
border = log.hl(u'%s'% ('='*90), 'cyan')

pat_xm = r'^https?://[^/.]*\.xiami\.com/'
pat_163 = r'^https?://music\.163\.com/'

#proxypool
ppool = None

def shall_I_begin(in_str, is_file=False, is_hq=False, need_proxy_pool = False):
    #start terminate_watcher
    Terminate_Watcher()
    global ppool
    if need_proxy_pool:
        LOG.info(u'初始化proxy pool')
        ppool = ProxyPool()
        LOG.info(u'proxy pool:[%d] 初始完毕'%len(ppool.proxies))

    #xiami obj
    xiami_obj = xm.Xiami(config.XIAMI_LOGIN_EMAIL,\
            config.XIAMI_LOGIN_PASSWORD, \
            is_hq,proxies=ppool)
    #netease obj
    m163 = netease.Netease(is_hq, proxies=ppool)

    if is_file:
        from_file(xiami_obj, m163,in_str)
    elif re.match(pat_xm, in_str):
        from_url_xm(xiami_obj, in_str)
    elif re.match(pat_163, in_str):
        from_url_163(m163, in_str)

    print border
    if len(dl_songs):
        LOG.info(u' 下载任务总数: %d \n 3秒后开始下载' % len(dl_songs))
        sleep(3)
        downloader.start_download(dl_songs)
    else:
        LOG.warning(u' 没有可下载任务,自动退出.')


def from_url_163(m163, url, verbose=True):
    """ parse the input string (163 url), and do download""" 

    LOG.debug('processing 163 url: "%s"'% url)
    msg = u''
    if '/song?id=' in url:
        song =netease.NeteaseSong(m163,url=url)
        dl_songs.append(song)
        msg = fmt_parsing % (m163_url_abbr(url),u'曲目',  song.song_name)

    elif '/album?id=' in url:
        album = netease.NeteaseAlbum(m163, url)
        dl_songs.extend(album.songs)
        msgs = [fmt_parsing % (m163_url_abbr(url),u'专辑',  album.artist_name+u' => '+album.album_name)]
        if verbose:
            for s in album.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append(fmt_has_song_nm % len(album.songs))
            msg= u' => '.join(msgs)

    elif '/playlist?id=' in url:
        playlist = netease.NeteasePlayList(m163, url)
        dl_songs.extend(playlist.songs)
        msgs = [ fmt_parsing % (m163_url_abbr(url),u'歌单',playlist.playlist_name)]
        if verbose:
            for s in playlist.songs:
                msgs.append( fmt_single_song % s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append(fmt_has_song_nm % len(playlist.songs))
            msg= u' => '.join(msgs)

    elif '/artist?id=' in url:
        topsong= netease.NeteaseTopSong(m163, url)
        dl_songs.extend(topsong.songs)
        msgs = [fmt_parsing % (m163_url_abbr(url), u'艺人热门歌曲',topsong.artist_name)]
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
        LOG.error(u'%s [易]不能识别的url [%s].' % (pre,url))
    else:
        LOG.info(u'%s%s'% (pre,msg))


def from_url_xm(xm_obj, url, verbose=True):
    """ parse the input string (xiami url), and do download"""

    LOG.debug('processing xiami url: "%s"'% url)
    msg = u''
    if '/collect/' in url:
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
        song = xm.XiamiSong(xm_obj, url=url)
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
        if verbose:
            LOG.warning(u'[虾]如用户收藏较多，解析歌曲需要较长时间，请耐心等待')

        fav = xm.Favorite(xm_obj, url, verbose)
        dl_songs.extend(fav.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url), u'用户收藏','')]
        if verbose:
            for s in fav.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append( fmt_has_song_nm % len(fav.songs))
            msg = u' => '.join(msgs)
    elif re.search(r'/artist/top/id/\d+', url):
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
        LOG.error(u'%s [虾]不能识别的url [%s].' % (pre,url))
    else:
        LOG.info(u'%s%s'% (pre,msg))

def from_file(xm_obj,m163, infile):
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
        link = link.rstrip('\n')
        if re.match(pat_xm, link):
            pool.add_task(from_url_xm, xm_obj,link, verbose=False)
        elif re.match(pat_163, link):
            pool.add_task(from_url_163, m163,link, verbose=False)
        else:
            LOG.warning(u' 略过不能识别的url [%s].' % link)

    pool.wait_completion()

def xiami_url_abbr(url):
    return re.sub(pat_xm,u'[虾] ',url)

def m163_url_abbr(url):
    return re.sub(pat_163,u'[易] ',url)
