# -*- coding:utf-8 -*-
import os
import urllib
import config
import log
import datetime,time
from multiprocessing

LOG = log.get_logger('zxLogger')

MULTITASKS_VALUES = ('THREAD', 'PROCESS')

def download(song):
    print log.hl('[starting] %s' % filename ,'cyan')
    #TODO download song
    #urllib.urlretrieve(url,filename)   
    print log.hl('[finished] %s' % filename ,'cyan')
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
