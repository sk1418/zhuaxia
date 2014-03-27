# -*- coding:utf-8 -*-
from os import path
import urllib
import requests
import config
import log
import datetime,time
import multiprocessing
from mutagen.id3 import ID3,TRCK,TIT2,TALB,TPE1,APIC,TDRC,COMM,TPOS,USLT

LOG = log.get_logger('zxLogger')

MULTITASKS_VALUES = ('THREAD', 'PROCESS')

def download(song):
    if ( not song.filename ) or (not song.dl_link):
        LOG.err( 'Song [id:%s] cannot downloaded' % song.song_id)
        return
    mp3_file = song.abs_path

    LOG.info('[starting] %s' % song.filename )
    r = requests.get(song.dl_link, stream=True)
    if r.status_code == 200:
        with open(mp3_file,'wb') as mp3:
            for chunk in r.iter_content():
                mp3.write(chunk)
    LOG.info('[finished] %s' % song.filename )
    write_mp3_meta_info(song)
    
    #TODO modify the mp3 file

def start_download(songs):
    LOG.info(config.MULTITASKS_MODE)
    pool = multiprocessing.Pool(processes=config.MULTITASKS_POOL_SIZE)
    #if 'PROCESS' == config.MULTITASKS_MODE.upper():
        #pool = multiprocessing.Pool(processes=config.MULTITASKS_POOL_SIZE)
    #else:
        #from multiprocessing.pool import ThreadPool
        #pool = ThreadPool(processes=config.MULTITASKS_POOL_SIZE)
    #for song in songs:
        #pool.apply_async(download,song)
    pool.map_async(download, songs)
    pool.close()
    pool.join()


def write_mp3_meta_info(song):
    id3 = ID3()
    #id3.add(TRCK(encoding=3, text=song.track if song.track else ""))
    #id3.add(TDRC(encoding=3, text=song.year if song.year else ""))
    id3.add(TIT2(encoding=3, text=song.song_name))
    id3.add(TALB(encoding=3, text=song.album_name))
    id3.add(TPE1(encoding=3, text=song.artist_name))
    #id3.add(TPOS(encoding=3, text=mp3_meta['cd_serial']))
    #id3.add(COMM(encoding=3, desc=u'Comment', text=u'\n\n'.join([mp3_meta['url_song'], mp3_meta['album_description']])))
    id3.save(song.abs_path)
