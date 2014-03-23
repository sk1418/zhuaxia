# -*- coding:utf-8 -*-
import time
import re
import json
import urllib,urllib2
import httplib
from contextlib import closing
from Cookie import SimpleCookie
from os import path
import log,config

LOG = log.get_logger("zxLogger")

#xiami android/iphone api urls
url_xiami="http://www.xiami.com"
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
        api_json = self.xm.read_link(url_song % self.song_id)
        j = json.loads(api_json)

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
                auth = self.checkin()
                if auth == '0' or ts_expired:
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
            'LoginButton': '登录',
        }
        data = urllib.urlencode(_form)
        headers = {'User-Agent': AGENT}
        headers['Referer'] = 'http://www.xiami.com/web/login'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        with closing(httplib.HTTPConnection('www.xiami.com')) as conn:
            #proxy setting
            if config.PROXY_HAS :
                conn = httplib.HTTPConnection(config.PROXY_HOST, config.PROXY_PORT)
            conn.request('POST', '/web/login', data, headers)
            res = conn.getresponse()
            cookie = res.getheader('Set-Cookie')
            try:
                self.member_auth = SimpleCookie(cookie)['member_auth'].value
                LOG.info( 'login success')
                return True
            except:
                LOG.error( "login failed")
            return False

    def checkin(self):
        if not self.member_auth:
            if not self.login():
                exit(1)
        headers = checkin_headers
        headers['Cookie'] = 'member_auth=%s; t_sign_auth=1' % self.member_auth
        with closing(httplib.HTTPConnection('www.xiami.com')) as conn:
            conn.request('POST', '/task/signin', None, headers)
            res = conn.getresponse()
            return res.read()

    
    def init_opener(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'), ('User-Agent', AGENT), ('Cookie', 'member_auth=%s' % self.member_auth)]

    def read_link(self, link):
        return self.opener.open(link).read()


