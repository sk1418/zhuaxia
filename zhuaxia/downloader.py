# -*- coding:utf-8 -*-
from os import path
import urllib
import requests
import config
import log
import datetime,time
import multiprocessing

LOG = log.get_logger('zxLogger')

MULTITASKS_VALUES = ('THREAD', 'PROCESS')

def download(song):
    if ( not song.filename ) or (not song.dl_link):
        LOG.err( 'Song [id:%s] cannot downloaded' % song.song_id)
        return
    mp3_file = path.join(config.DOWNLOAD_DIR,song.group_dir, song.filename) if song.group_dir \
            else path.join(config.DOWNLOAD_DIR, song.filename)
    print log.hl('[starting] %s' % song.filename ,'cyan')
    #urllib.urlretrieve(url,filename)   
    r = requests.get(song.dl_link, stream=True)
    if r.status_code == 200:
        with open(mp3_file,'wb') as mp3:
            for chunk in r.iter_content():
                mp3.write(chunk)
    print log.hl('[finished] %s' % song.filename ,'cyan')
    #TODO modify the mp3 file

def start_download(songs):
    if 'PROCESS' == upper(config.MULTITASKS_MODE):
        pool = multiprocessing.Pool(processes=config.MULTITASKS_POOL_SIZE)
    else:
        from multiprocessing.pool import ThreadPool
        pool = ThreadPool(processes=config.MULTITASKS_POOL_SIZE)
    for song in Songs:
        pool.apply_async(download,song)
    pool.close()
    pool.join()
