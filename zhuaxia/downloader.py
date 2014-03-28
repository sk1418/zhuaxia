# -*- coding:utf-8 -*-
from os import path
import requests
import config
import log
import datetime,time
from Queue import Queue
from threading import Thread
from mutagen.id3 import ID3,TRCK,TIT2,TALB,TPE1,APIC,TDRC,COMM,TPOS,USLT

LOG = log.get_logger('zxLogger')

MULTITASKS_VALUES = ('THREAD', 'PROCESS')

total=0
done=0

def download(song):
    if ( not song.filename ) or (not song.dl_link):
        LOG.err( 'Song [id:%s] cannot downloaded' % song.song_id)
        return
    mp3_file = song.abs_path

    LOG.info(u'开始下载 %s ...' % song.filename )

    #LOG.info('simulating %s dl' % song.song_name)
    #time.sleep(7)
    r = requests.get(song.dl_link, stream=True)
    if r.status_code == 200:
        with open(mp3_file,'wb') as mp3:
            for chunk in r.iter_content():
                mp3.write(chunk)
    write_mp3_meta(song)
    global done
    done += 1
    LOG.info( u'[%s] 完成: %s' % ('/'.join((str(done),str(total)) ),song.filename ))
    

def start_download(songs):
    global total 
    total = len(songs)
    LOG.info(u'下载任务总数: %s' % total)
    pool = ThreadPool(config.THREAD_POOL_SIZE)
    [pool.add_task(download, song) for song in songs]
    pool.wait_completion()


def write_mp3_meta(song):
    id3 = ID3()
    #id3.add(TRCK(encoding=3, text=song.track if song.track else ""))
    #id3.add(TDRC(encoding=3, text=song.year if song.year else ""))
    id3.add(TIT2(encoding=3, text=song.song_name))
    id3.add(TALB(encoding=3, text=song.album_name))
    id3.add(TPE1(encoding=3, text=song.artist_name))
    #id3.add(TPOS(encoding=3, text=mp3_meta['cd_serial']))
    #id3.add(COMM(encoding=3, desc=u'Comment', text=u'\n\n'.join([mp3_meta['url_song'], mp3_meta['album_description']])))
    id3.save(song.abs_path)

class ThreadPool(object):
    def __init__(self, size):
        self.size = size
        self.tasks = Queue(size)
        for i in range(size):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func,args,kargs))

    def wait_completion(self):
        self.tasks.join()

class Worker(Thread):
    def __init__(self, taskQueue):
        Thread.__init__(self)
        self.tasks = taskQueue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func ,args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception, e: 
                LOG.error(str(e))
            finally:
                self.tasks.task_done()



    

