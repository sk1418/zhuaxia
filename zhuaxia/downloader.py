# -*- coding:utf-8 -*-
import os
import urllib
import config
import log
import datetime,time

LOG = log.get_logger('zxLogger')

MULTITASKS_VALUES = ('THREAD', 'PROCESS')

def download(filename,url,agent=None):
    print log.hl('开始下载 %s ...' % filename ,'cyan')
    urllib.urlretrieve(url,filename)   
