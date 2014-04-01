# -*- coding:utf-8 -*-
from os import path
import sys
import requests
import config, log, util
import datetime,time
from threadpool import ThreadPool
from Queue import Queue
from mutagen.id3 import ID3,TRCK,TIT2,TALB,TPE1,APIC,TDRC,COMM,TPOS,USLT
from threading import Thread

LOG = log.get_logger('zxLogger')

#total number of jobs
total=0
#the number of finished jobs
done=0
#progress dictionary, for progress display
progress = {}
#finsished job to be shown in progress
done2show=[]


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
# output progress 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
def print_progress():
    width = util.get_terminal_size()[1] -5
    per_part = int(width * 0.5)
    bar_count = (per_part-2/10) # number of percent bar
    #line = log.hl(u' %s\n'% ('-'*90), 'cyan')
    line = log.hl(u' %s\n'% ('-'*width), 'cyan')
    sys.stdout.write(u'\x1b[2J\x1b[H') #clear screen
    sys.stdout.write(line)
    header = u' 线程池:[%d] | 总进度:[%d/%d]\n'% (config.THREAD_POOL_SIZE,done,total)
    #header = header.rjust(80)
    header = header.rjust(width-10)
    sys.stdout.write(log.hl(u' %s'%header,'warning'))
    sys.stdout.write(line)
    for filename, percent in progress.items():
        #bar = ('=' * int(percent * 40)).ljust(40)
        bar = ('=' * int(percent * bar_count)).ljust(bar_count)
        percent = percent * 100
        single_p =  "%s [%s] %.1f%%\n" % (filename.ljust(width - bar_count-10), bar, percent) 
        sys.stdout.write(log.hl(single_p,'green'))

    if len(done2show):
        sys.stdout.write(line)
        sys.stdout.write(log.hl((u'最近完成(只显示%d个):\n'% config.SHOW_DONE_NUMBER).rjust(width-10),'warning'))
        sys.stdout.write(line)
        #display finished jobs
        for d in done2show:
            sys.stdout.write(log.hl((u' - %s\n'% d)),'cyan')

    sys.stdout.flush()

def download_by_url(url,filepath,show_progress=False):
    """ 
    basic downloading function, download url and save to 
    file path
    """
    if ( not filepath ) or (not url):
        LOG.err( 'Url or filepath is not valid, resouce cannot be downloaded.')
        return

    fname = path.basename(filepath)
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        total_length = int(r.headers.get('content-length'))
        done_length = 0
        with open(filepath,'wb') as f:
            for chunk in r.iter_content(1024):
                done_length += len(chunk)
                f.write(chunk)
                if show_progress:
                    percent = float(done_length) / float(total_length)
                    progress[fname] = percent
    return 0

def download(song):
    global done, progress

    #if file not in progress, add
    if song.filename not in progress:
        progress[song.filename] = 0.0

    if ( not song.filename ) or (not song.dl_link):
        LOG.err( 'Song [id:%s] cannot be downloaded' % song.song_id)
        return
    mp3_file = song.abs_path

    download_by_url(song.dl_link, mp3_file, show_progress=True)

    write_mp3_meta(song)
    done += 1
    fill_done2show(song.filename)
    #remove from progress
    del progress[song.filename]

def fill_done2show(filename):
    global done2show
    if len(done2show) == config.SHOW_DONE_NUMBER:
        done2show.pop()
    done2show.append(filename)

def start_download(songs):
    global total, progress
    total = len(songs)
    pool = ThreadPool(config.THREAD_POOL_SIZE)

    downloader = Downloader(songs, pool)
    downloader.start()

    while done < total:
        time.sleep(1)
        print_progress()


class Downloader(Thread):
    def __init__(self, songs, pool):
        Thread.__init__(self)
        self.songs = songs
        self.pool = pool

    def run(self):
        global progress
        for song in self.songs:
            self.pool.add_task(download, song)
        self.pool.wait_completion()

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
