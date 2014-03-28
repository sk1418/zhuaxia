# -*- coding:utf-8 -*-
from os import path
import sys
import requests
import config
import log
import datetime,time
from Queue import Queue
from threading import Thread
from mutagen.id3 import ID3,TRCK,TIT2,TALB,TPE1,APIC,TDRC,COMM,TPOS,USLT

LOG = log.get_logger('zxLogger')

total=0
done=0
progress = {}


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
# print progress 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
def print_progress():
    sys.stdout.write(u'\x1b[2J\x1b[H') #clear screen
    header = u'<已完成的任务只显示最近3个> | 线程池:[%d] | 已完成:[%d/%d]\n'%(config.THREAD_POOL_SIZE,done,total)
    sys.stdout.write(log.hl(u' %70s'%header,'warning'))
    sys.stdout.write(log.hl(u' %s\n'% ('v'*90), 'cyan'))
    for filename, percent in progress.items():
        bar = ('=' * int(percent * 40)).ljust(40)
        percent = percent * 100
        line =  "%40s [%s] %.1f%%\n" % (filename, bar, percent) 
        sys.stdout.write(log.hl(line,'green'))
    sys.stdout.flush()

def download(song):
    global done, progress
    if ( not song.filename ) or (not song.dl_link):
        LOG.err( 'Song [id:%s] cannot be downloaded' % song.song_id)
        return
    mp3_file = song.abs_path

    r = requests.get(song.dl_link, stream=True)
    if r.status_code == 200:
        total_length = int(r.headers.get('content-length'))
        done_length = 0
        with open(mp3_file,'wb') as mp3:
            for chunk in r.iter_content(1024):
                done_length += len(chunk)
                mp3.write(chunk)
                percent = float(done_length) / float(total_length)
                progress[song.filename] = percent
    write_mp3_meta(song)

    #TODO only keep last 3 finished job in progress
    done += 1


def start_download(songs):
    global total, progress
    total = len(songs)
    LOG.info(u'下载任务总数: %s' % total)
    pool = ThreadPool(config.THREAD_POOL_SIZE)

    for song in songs:
        progress[song.filename] = 0.0
        pool.add_task(download, song)


    while done < total:
        time.sleep(1)
        print_progress()

    pool.wait_completion()


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
# ThreadPool implementation
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
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

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
# write mp3 meta data to downloaded mp3 files
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
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
