# -*- coding:utf-8 -*-
from os import path
import os
import datetime
import sys
import requests
import config, log, util
import time
import hist_handler
import traceback
from threadpool import ThreadPool
from Queue import Queue
from mutagen.id3 import ID3,TRCK,TIT2,TALB,TPE1,APIC,TDRC,COMM,TPOS,USLT
from threading import Thread
#see download_url_urllib doc
import urllib2
import pydoc
import codecs


LOG = log.get_logger('zxLogger')

if config.LANG.upper() == 'CN':
    import i18n.msg_cn as msg
else:
    import i18n.msg_en as msg

#total number of jobs
total=0
#the number of finished jobs
done=0
#progress dictionary, for progress display. {filename:Download_Progress obj}
progress = {}
#finsished job to be shown in progress
done2show=[]

#success/failed song lists (song objects)
success_list=[]
failed_list=[]

class Download_Progress(object):
    """
    a download progress object 
    """
    def __init__(self, filename):
        self.filename = filename
        self.total_length = 0
        self.finished_length =0
        self.start = datetime.datetime.now()


    def percent(self):
        """calculate downloaded percentage"""
        return float(self.finished_length) / float(self.total_length) if self.total_length else 0.0

    def rate(self):
        """ calculate downloading rate """
        elapsed = datetime.datetime.now() - self.start
        return float(self.total_length-self.finished_length)/float(elapsed.total_seconds())/1024



class Downloader(Thread):
    def __init__(self, songs, pool):
        Thread.__init__(self)
        self.songs = songs
        self.pool = pool

    def run(self):
        global progress
        for song in self.songs:
            self.pool.add_task(download_single_song, song)
        self.pool.wait_completion()

def get_proxy(song):
    proxy = None
    if song.handler.need_proxy_pool:
        proxy = {'http':song.handler.proxies.get_proxy()}
    elif config.CHINA_PROXY_HTTP:
        proxy={'http': config.CHINA_PROXY_HTTP}
    return proxy

def write_mp3_meta(song):
    """
     write mp3 meta data to downloaded mp3 files
     @song an Song instance
     """
    id3 = ID3()
    id3.add(TIT2(encoding=3, text=song.song_name))
    id3.add(TALB(encoding=3, text=song.album_name))
    id3.add(TPE1(encoding=3, text=song.artist_name))
    id3.add(TRCK(encoding=3, text=str(song.track_no)))
    id3.save(song.abs_path)

def print_progress():
    """ print progress info """
    #the factor of width used for progress bar
    percent_bar_factor = 0.4
    width = util.get_terminal_size()[1] -5
    bar_count = (int(width*percent_bar_factor)-2/10) # number of percent bar
    #line = log.hl(u' %s\n'% ('-'*90), 'cyan')
    line = log.hl(u' %s\n'% ('+'*width), 'cyan')
    sep = log.hl(u' %s\n'% ('='*width), 'cyan')
    sys.stdout.write(u'\x1b[2J\x1b[H') #clear screen
    sys.stdout.write(line)
    header = msg.fmt_dl_header % (config.DOWNLOAD_DIR, config.THREAD_POOL_SIZE)
    #header = util.ljust(header, width)
    sys.stdout.write(log.hl(u' %s'%header,'warning'))
    sys.stdout.write(line)

    fmt_progress = '%s [%s] %.1f%% (%dkib/s)\n'


    all_p = [] #all progress bars, filled by following for loop
    sum_percent = 0 # total percent for running job
    sum_rate = 0 # total rate for running job
    total_percent = 0

    for filename, prog_obj in progress.items():
        percent = prog_obj.percent()
        rate = prog_obj.rate()
        #sum for the total progress
        sum_percent += percent
        sum_rate += rate

        bar = util.ljust('=' * int(percent * bar_count), bar_count)
        per100 = percent * 100 
        single_p =  fmt_progress % \
                (util.rjust(filename,(width - bar_count -22)), bar, per100,rate) # the -20 is for the xx.x% and [ and ] xx.xkb/s (spaces)
        all_p.append(log.hl(single_p,'green'))
    
    #calculate total progress percent
    total_percent = float(sum_percent+done)/total
    
    #global progress
    g_text = msg.fmt_dl_progress % (done, total)
    g_bar = util.ljust('#' * int(total_percent* bar_count), bar_count)
    g_progress =  fmt_progress % \
                (util.rjust(g_text,(width - bar_count -22)), g_bar, 100*total_percent,sum_rate) # the -20 is for the xx.x% and [ and ] xx.xkb/s (spaces)

    #output all total progress bars
    sys.stdout.write(log.hl(u'%s'%g_progress, 'red'))
    sys.stdout.write(sep)

    #output all downloads' progress bars
    sys.stdout.write(''.join(all_p))

    # finished jobs
    if len(done2show):
        sys.stdout.write(line)
        sys.stdout.write(log.hl(msg.fmt_dl_last_finished % config.SHOW_DONE_NUMBER,'warning'))
        sys.stdout.write(line)
        #display finished jobs
        for d in done2show:
            sys.stdout.write(log.hl(u' √ %s\n'% d,'cyan'))

    #failed downloads
    if len(failed_list):
        sys.stdout.write(line)
        sys.stdout.write(log.hl(msg.fmt_dl_failed_jobs,'error'))
        sys.stdout.write(line)
        #display failed jobs
        for failed_song in failed_list:
            sys.stdout.write(log.hl(u' ✘ %s\n' % failed_song.filename,'red'))


    sys.stdout.write(line)
    sys.stdout.flush()


def fill_download_progress(filename, total_length, finished_length):
    """ fill the global dict progress {} with download progress """
    global progress

    if filename in progress:
        prog_obj = progress[filename]
        prog_obj.total_length = total_length
        prog_obj.finished_length = finished_length
    else:
        prog_obj = Download_Progress(filename)
        progress[filename] = prog_obj



def download_url_urllib(url,filepath,show_progress=False, proxy=None):
    """ 
    this function does the samething as the download_url(). The different is
    this function uses the standard urllib2 to download files.
    basic downloading function, download url and save to 
    file path
    http.get timeout: 30s

    """

    if ( not filepath ) or (not url):
        LOG.error( 'Url or filepath is not valid, resouce cannot be downloaded.')
        return 1

    fname = path.basename(filepath)

    try:
        proxyServer = urllib2.ProxyHandler(proxy) if proxy else None
        opener = urllib2.build_opener()
        # for downloading, ignore the proxy, it seems that if 
        # we got the real link, both 163 and xiami don't need a CN proxy to
        # download the songs

        # if proxyServer:
            # opener = urllib2.build_opener(proxyServer)
            
        urllib2.install_opener(opener)
        r = urllib2.urlopen(url, timeout=30)

        if r.getcode() == 200:
            total_length = int(r.info().getheader('Content-Length').strip())
            
            done_length = 0
            chunk_size=1024
            with open(filepath,'wb') as f:
                while True:
                    chunk = r.read(chunk_size)
                    done_length += len(chunk)
                    if not chunk:
                        break
                    f.write(chunk)
                    if show_progress:
                        fill_download_progress(fname, total_length, done_length)
            return 0
        else:
            LOG.debug("[DL_URL] HTTP Status %d . Song: %s " % (r.status_code,fname))
            return 1

    except Exception, err:
        LOG.debug("[DL_URL] downloading song %s timeout!" % fname)
        LOG.debug(traceback.format_exc())
        return 1

def download_url(url,filepath,show_progress=False, proxy=None):
    """ 
    basic downloading function, download url and save to 
    file path
    http.get timeout: 30s
    """
    if ( not filepath ) or (not url):
        LOG.error( 'Url or filepath is not valid, resouce cannot be downloaded.')
        return 1

    fname = path.basename(filepath)

    try:
        #get request timeout 30 s
        r = requests.get(url, stream=True, timeout=30, proxies=proxy)
        if r.status_code == 200:
            total_length = int(r.headers.get('content-length'))
            done_length = 0
            with open(filepath,'wb') as f:
                for chunk in r.iter_content(1024):
                    done_length += len(chunk)
                    f.write(chunk)
                    if show_progress:
                        fill_download_progress(fname, total_length, done_length)
            return 0
        else:
            LOG.debug("[DL_URL] HTTP Status %d . Song: %s " % (r.status_code,fname))
            return 1
    except Exception, err:
        LOG.debug("[DL_URL] downloading song %s timeout!" % fname)
        LOG.debug(traceback.format_exc())
        return 1

def download_single_song(song):
    """
    download a single song 
    max retry 5 times
    """
    global done, progress

    #download retry count
    retry = 5

    if ( not song.filename ) or (not song.dl_link):
        LOG.error( 'Song [id:%s] cannot be downloaded' % song.song_id)
        retry = -1 # this will make the song bypass the downloading

    mp3_file = song.abs_path

    dl_result = -1 # download return code
    LOG.debug("[DL_Song] downloading: %s " % song.dl_link)
    while retry > 0 :
        retry -= 1
        LOG.debug("[DL_Song] start downloading: %s retry: %d" % (mp3_file, 5-retry))

        #if file not in progress, add
        if song.filename not in progress:
            fill_download_progress(song.filename, 0.0, 0.0)

        #do the actual downloading
        dl_result = download_url_urllib(song.dl_link, mp3_file, show_progress=True, proxy= get_proxy(song))

        if dl_result == 0: #success
            write_mp3_meta(song)
            LOG.debug("[DL_Song] Finished: %s" % mp3_file)
            break
        else: # return code is not 0
            
            #remove from progress
            del progress[song.filename]
            if path.exists(song.abs_path):
                #remove file if already exists
                LOG.debug( '[DL_Song] remove incompleted file : ' + song.abs_path)
                os.remove(song.abs_path)
            # retry


    done+=1 #no matter success of fail, the task was done
    if dl_result == 0:
        #set the success flag
        song.success = True 
        fill_done2show(song)
        #remove from progress
        del progress[song.filename]
    else:
        # if it comes here, 5 retries run out
        fill_failed_list(song)


def fill_done2show(song):
    """
    fill the given filename into global list 'done2show'
    Depends on the config.SHOW_DONE_NUMBER, the eldest entry will be
    poped out from the list.
    """
    global done2show, success_list
    success_list.append(song)
    if len(done2show) == config.SHOW_DONE_NUMBER:
        done2show.pop()
    done2show.insert(0, song.filename)

def fill_failed_list(song):
    """
    fill the given song into global list 'failed2show'
    """
    global  failed_list
    failed_list.insert(0,song)


def start_download(songs, skipped_hists):
    """
    start multi-threading downloading songs. and generate a summary file
    songs: the list of songs need to be downloaded

    call the finish_hook function, pass skipped_hist
    """
    global total
    total = len(songs)
    LOG.debug('init thread pool (%d) for downloading'% config.THREAD_POOL_SIZE)
    pool = ThreadPool(config.THREAD_POOL_SIZE)
    downloader = Downloader(songs, pool)

    LOG.debug('Start downloading' )
    downloader.start()

    while done < total:
        time.sleep(1)
        print_progress()

    # handling lyrics downloading
    download_lyrics(songs)

    print log.hl(msg.fmt_insert_hist, 'warning')
    hist_handler.insert_hist(songs)
    print log.hl(msg.fmt_all_finished, 'warning')
    #call finish hook
    finish_summary(skipped_hists)

def finish_summary(skipped_hist):
    """
    build the summary after finishing all dl

    skipped_hist: a History list, contains skipped songs, it is not empty only
                  if incremental_dl is true
    """
    border= "\n"+u">>"*40 + u"\n"
    #build summary text:
    text = []
    if skipped_hist:
        text.append( border+msg.fmt_summary_skip_title +border)
        text.append( msg.fmt_summary_skip_header)
        for hist in skipped_hist:
            text.append( "%s\t%s\t%s\t%s" % (msg.head_xm if hist.source ==1 else msg.head_163, hist.last_dl_time_str(), hist.song_name, hist.location))

    if success_list:
        text.append( border+msg.fmt_summary_success_title +border)
        text.append( msg.fmt_summary_success_header)
        for song in success_list:
            text.append('%s\t%s'%(song.song_name, song.abs_path))

    if failed_list:
        text.append( border+msg.fmt_summary_failed_title +border)
        text.append( msg.fmt_summary_failed_header)
        for song in failed_list:
            text.append('%s\t%s'%(song.song_name, song.abs_path))

    while True:
        sys.stdout.write(msg.summary_prompt)
        choice = raw_input().lower()
        if choice == 'q' or choice == '':
            break
        elif choice == 'v':
            pydoc.pager(u"\n".join(text))
            break
        elif choice == 's':
            summary = path.join(config.DOWNLOAD_DIR,'summary_'+str(datetime.datetime.today())+".txt")
            with codecs.open(summary, 'w', 'utf-8') as f:
                f.write("\n".join(text))
            print log.hl(msg.summary_saved % summary ,'cyan')
            break
        else:
            sys.stdout.write(msg.summary_prompt_err)

def download_lyrics(songs):
    """download / write lyric to file if it is needed"""

    url_lyric_163 = "http://music.163.com/api/song/lyric?id=%s&lv=1"
    
    percent_bar_factor = 0.4
    width = util.get_terminal_size()[1] -5
    bar_count = (int(width*percent_bar_factor)-2/10) # number of percent bar
    line = log.hl(u' %s'% ('+'*width), 'cyan')

    if songs[0].handler.dl_lyric == True:
        print log.hl(msg.fmt_dl_lyric_start, 'warning')
        print line

        for song in songs:
            if song.lyric_abs_path:
                print log.hl(u' %s '% song.lyric_filename,'cyan'),  #the ending comma is for hide the newline
                if song.song_type == 1: #xiami
                    if song.handler.need_proxy_pool:
                        if song.lyric_link:
                            download_url(song.lyric_link, song.lyric_abs_path, show_progress=True, proxy={'http':song.handler.proxies.get_proxy()})
                    else:
                        if song.lyric_link:
                            download_url(song.lyric_link, song.lyric_abs_path, show_progress=True)
                    print log.hl(u' √','cyan')
                else: #163
                    lyric_link = url_lyric_163 % song.song_id
                    lyric_json = song.handler.read_link(lyric_link).json()
                    if not lyric_json or not lyric_json.has_key('lrc')  or  not lyric_json['lrc'].has_key('lyric'):
                        print log.hl(u' ✘ Not Found','red')
                        continue
                    song.lyric_text = song.handler.read_link(lyric_link).json()['lrc']['lyric']
                    import codecs
                    with codecs.open(song.lyric_abs_path, 'w', 'utf-8') as f:
                        f.write(song.lyric_text)
                    print log.hl(u' √','cyan')
        print line

