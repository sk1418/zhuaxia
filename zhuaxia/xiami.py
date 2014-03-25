# -*- coding:utf-8 -*-
import time
import re
import requests
from os import path
import log,config

LOG = log.get_logger("zxLogger")

#xiami android/iphone api urls
url_xiami="http://www.xiami.com"
url_login="https://login.xiami.com/member/login"
url_song = "http://www.xiami.com/app/android/song?id=%s"
url_album = "http://www.xiami.com/app/android/album?id=%s"
url_collect = "http://www.xiami.com/app/android/collect?id=%s"
url_artist_albums = "http://www.xiami.com/app/android/artist-albums?id=%s&page=%s"
url_artist_top_song = "http://www.xiami.com/app/android/artist-topsongs?id=%s"
url_lib_songs = "http://www.xiami.com/app/android/lib-songs?uid=%s&page=%s"

#agent string for http request header
AGENT= 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'

class Song(object):
    """xiami Song class"""
    def __init__(self,xiami_obj,url):
        self.xm = xiami_obj
        self.url = url
        self.album_id = ''
        self.song_id = re.search(r'(?<=/song/)\d+', self.url).group(0)
        self.album_id = ''
        self.dl_link = ''
        self.lyrics_link = ''
        self.artist_name = ''
        self.song_name = self.song_id
        self.album_name = ''
        self.filename = ''

        self.year = None
        self.track=None

        self.init_song()


    def init_song(self):
        j = self.xm.read_link(url_song % self.song_id).json()
        #name
        self.song_name = j['song']['song_name']
        # download link
        self.dl_link = j['song']['song_location']
        # lyrics link
        self.lyrics_link = j['song']['song_lrc']
        # artist_name
        self.artist_name = j['song']['artist_name']
        # album id, name
        self.album_name = j['song']['album_name']
        self.album_id = j['song']['album_id']

        #filename  artistName_songName.mp3
        self.filename = (self.artist_name + "_" if self.artist_name  else "" ) + self.song_name + u'.mp3'


    def write_mp3_meta_info(self, mp3_meta, filename):
        id3 = ID3()
        id3.add(TRCK(encoding=3, text=self.track if self.track else ""))
        id3.add(TDRC(encoding=3, text=self.year if self.year else ""))
        id3.add(TIT2(encoding=3, text=self.song_name))
        id3.add(TALB(encoding=3, text=self.album_name))
        id3.add(TPE1(encoding=3, text=self.artist_name))
        #id3.add(TPOS(encoding=3, text=mp3_meta['cd_serial']))
        #id3.add(COMM(encoding=3, desc=u'Comment', text=u'\n\n'.join([mp3_meta['url_song'], mp3_meta['album_description']])))
        id3.save(self.filename)


    

        
class Album(object):
    """The xiami album object"""
    def __init__(self, url):
        
        self.url = url 
        self.album_id = album_id
        self.songs = [] # list of Song

class Favorite(object):
    def __init__(self,url):
        self.url = url



checkin_headers = {
    'User-Agent': AGENT,
    'Content-Length': '0',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'www.xiami.com',
    'Origin': url_xiami,
    'Referer': url_xiami,
    'Content-Length': '0',
}

class Xiami(object):

    def __init__(self, email, password, cookie_file):
        self.email = email
        self.password = password
        self.cookie_file = cookie_file
        self.member_auth = ""
        self.opener = None 
        #do login
        self.login_with_cookie()
        #init opener
        self.init_opener()
        


    def login_with_cookie(self):
        ts = str(int(time.time()))
        if path.exists(self.cookie_file):
            LOG.info('read member_auth from cookie file ...')
            with open(self.cookie_file) as f:
                cif = f.read().split(' ')
                ts_expired = (int(ts) - int(cif[0])) > 18000 
                self.member_auth = cif[1]
                if ts_expired:
                    self.write_cookie(ts)
        else:
           self.write_cookie(ts)
        

    def write_cookie(self, ts):
        if not self.login():
            exit(1)
        LOG.info( 'Writing cookie file ...')
        with open(self.cookie_file, 'w') as f:
            f.write(ts + ' ' + self.member_auth)


    def login(self):
        LOG.info( 'login with email and password....')
        _form = {
            'email': self.email,
            'password': self.password,
            'submit': '登录',
        }
        headers = {'User-Agent': AGENT}
        headers['Referer'] = url_login
        # do http post login
        try:
            sess = requests.Session()
            sess.headers['User-Agent'] = AGENT
            sess.verify = False
            sess.mount('https://', requests.adapters.HTTPAdapter())
            res = sess.post(url_login, data=_form)
            self.memeber_auth = sess.cookies['member_auth']
            LOG.info( 'login success')
            return True
        except:
            LOG.error( "login failed")
            return False

    def init_opener(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'), ('User-Agent', AGENT), ('Cookie', 'member_auth=%s' % self.member_auth)]

    def read_link(self, link):
        headers = {'User-Agent':AGENT}
        headers['Cookie'] = 'member_auth=%s' % self.member_auth
        return requests.get(link,headers=headers)


