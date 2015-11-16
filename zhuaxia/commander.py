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

#after init config, loading message
if config.LANG.upper() == 'CN':
    import i18n.msg_cn as msgTxt
else:
    import i18n.msg_en as msgTxt

LOG = log.get_logger("zxLogger")

dl_songs = []
total = 0
done = 0

fmt_parsing = msgTxt.fmt_parsing
fmt_has_song_nm = msgTxt.fmt_has_song_nm
fmt_single_song = msgTxt.fmt_single_song
border = log.hl(u'%s'% ('='*90), 'cyan')

pat_xm = r'^https?://[^/.]*\.xiami\.com/'
pat_163 = r'^https?://music\.163\.com/'

#proxypool
ppool = None

#xiami object. declare it here because we want to init it only if it is required
xiami_obj = None

def __init_xiami_obj(option):
    #if ppool is required, it should have been initialized in shall_i_begin()
    global xiami_obj
    if not xiami_obj:
        xiami_obj = xm.Xiami(config.XIAMI_LOGIN_EMAIL,\
            config.XIAMI_LOGIN_PASSWORD, \
            option)


def shall_I_begin(option):
    #start terminate_watcher
    Terminate_Watcher()
    global ppool, xiami_obj
    if option.need_proxy_pool:
        LOG.info(msgTxt.init_proxypool)
        ppool = ProxyPool()
        option.proxies = ppool
        LOG.info(msgTxt.fmt_init_proxypool_done %len(ppool.proxies))

    #netease obj
    m163 = netease.Netease(option)

    if option.inFile:
        from_file(m163,option)
    elif re.match(pat_xm, option.inUrl):
        __init_xiami_obj(option)
        from_url_xm(xiami_obj, option.inUrl)
    elif re.match(pat_163, option.inUrl):
        from_url_163(m163, option.inUrl)

    print border
    if len(dl_songs):
        LOG.info(msgTxt.fmt_total_dl_nm % len(dl_songs))
        sleep(3)
        downloader.start_download(dl_songs)
    else:
        LOG.warning(msgTxt.no_dl_task)


def from_url_163(m163, url, verbose=True):
    """ parse the input string (163 url), and do download""" 

    LOG.debug('processing 163 url: "%s"'% url)
    msg = u''
    if '/song?id=' in url:
        song =netease.NeteaseSong(m163,url=url)
        dl_songs.append(song)
        msg = fmt_parsing % (m163_url_abbr(url),msgTxt.song,  song.song_name)

    elif '/album?id=' in url:
        album = netease.NeteaseAlbum(m163, url)
        dl_songs.extend(album.songs)
        msgs = [fmt_parsing % (m163_url_abbr(url),msgTxt.album,  album.artist_name+u' => '+album.album_name)]
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
        msgs = [ fmt_parsing % (m163_url_abbr(url), msgTxt.playlist, playlist.playlist_name)]
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
        msgs = [fmt_parsing % (m163_url_abbr(url), msgTxt.artistTop ,topsong.artist_name)]
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
        LOG.error(msgTxt.fmt_163_unknow_url% (pre,url))
    else:
        LOG.info(u'%s%s'% (pre,msg))


def from_url_xm(xm_obj, url, verbose=True):
    """ parse the input string (xiami url), and do download"""

    LOG.debug('processing xiami url: "%s"'% url)
    msg = u''
    if '/collect/' in url:
        collect = xm.Collection(xm_obj, url)
        dl_songs.extend(collect.songs)
        msgs = [ fmt_parsing % (xiami_url_abbr(url), msgTxt.collection ,collect.collection_name)]
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
        msg = fmt_parsing % (xiami_url_abbr(url),msgTxt.song,  song.song_name)
    elif '/album/' in url:
        album = xm.Album(xm_obj, url)
        dl_songs.extend(album.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url),msgTxt.album,  album.artist_name+u' => '+album.album_name)]
        if verbose:
            for s in album.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append(fmt_has_song_nm % len(album.songs))
            msg= u' => '.join(msgs)

    elif '/lib-song/u/' in url:
        if verbose:
            LOG.warning(msgTxt.warning_many_collections)

        fav = xm.Favorite(xm_obj, url, verbose)
        dl_songs.extend(fav.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url), msgTxt.Favorite ,'')]
        if verbose:
            for s in fav.songs:
                msgs.append(fmt_single_song %s.song_name)
            msg = u'\n    |-> '.join(msgs)
        else:
            msgs.append( fmt_has_song_nm % len(fav.songs))
            msg = u' => '.join(msgs)
    elif re.search(r'/artist/', url):
        topsong=xm.TopSong(xm_obj, url)
        dl_songs.extend(topsong.songs)
        msgs = [fmt_parsing % (xiami_url_abbr(url), msgTxt.artistTop,topsong.artist_name)]
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
        LOG.error(msgTxt.fmt_xm_unknown_url % (pre,url))
    else:
        LOG.info(u'%s%s'% (pre,msg))

def from_file(m163,option):
    """ download objects (songs, albums...) from an input file.  """

    urls = []
    with open(option.inFile) as f:
        urls = f.readlines() 

    global total, done, xiami_obj
    total = len(urls)
    print border
    LOG.info(msgTxt.fmt_links_in_file % total)
    print border
    pool = ThreadPool(config.THREAD_POOL_SIZE)
    for link in [u for u in urls if u]:
        link = link.rstrip('\n')
        #if it is a xiami link, init xiami object
        if re.match(pat_xm, link):
            __init_xiami_obj(option)
            pool.add_task(from_url_xm, xiami_obj,link, verbose=False)
        elif re.match(pat_163, link):
            pool.add_task(from_url_163, m163,link, verbose=False)
        else:
            LOG.warning(msgTxt.fmt_skip_unknown_url % link)

    pool.wait_completion()

def xiami_url_abbr(url):
    return re.sub(pat_xm,msgTxt.short_xm,url)

def m163_url_abbr(url):
    return re.sub(pat_163,msgTxt.short_163,url)
