# -*- coding:utf-8 -*-
import time
import re
import requests
import log, config
from os import path

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
    def __init__(self,xiami_obj,url=None,song_json=None):
        self.xm = xiami_obj
        if url:
            self.url = url
            self.init_by_url(url)
        elif song_json:
            self.init_by_json(song_json)


    def init_by_json(self, song_json):
        self.song_id = song_json['song_id']
        self.album_id = song_json['album_id']
        self.song_name = song_json['name']
        self.dl_link = song_json['location']
        # lyrics link
        self.lyrics_link = song_json['lyric']
        # artist_name
        self.artist_name = song_json['artist_name']
        # album id, name
        self.album_name = song_json['title']

        self.filename = self.song_name + u'.mp3'
        self.group_dir = self.artist_name + u'_' + self.album_name
        self.abs_path = path.join(config.DOWNLOAD_DIR, self.group_dir, self.filename)

    def init_by_url(self,url):
        self.song_id = re.search(r'(?<=/song/)\d+', url).group(0)
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

        #used only for album/collection etc. create a dir to group all songs
        self.group_dir = None
        #filename  artistName_songName.mp3
        self.filename = (self.artist_name + "_" if self.artist_name  else "" ) + self.song_name + u'.mp3'
        self.abs_path = path.join(config.DOWNLOAD_DIR,self.filename)


class Album(object):
    """The xiami album object"""
    def __init__(self, xm_obj, url):

        self.xm = xm_obj
        self.url = url 
        self.album_id = re.search(r'(?<=/album/)\d+', self.url).group(0)

        self.year = None
        self.track=None
        self.songs = [] # list of Song
        self.init_album()

    def init_album(self):
        j = self.xm.read_link(url_album % self.album_id).json()
        #name
        self.album_name = j['album']['title']
        #album logo
        self.logo = j['album']['album_logo']
        # artist_name
        self.artist_name = j['album']['artist_name']

        #description
        self.album_desc = j['album']['description']

        #handle songs
        for jsong in j['album']['songs']:
            song = Song(self.xm, song_json=jsong)
            self.songs.append(song)








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
        #do login
        self.login_with_cookie()
        


    def login_with_cookie(self):
        ts = str(int(time.time()))
        if path.exists(self.cookie_file):
            LOG.info('[Login] read member_auth from cookie file ...')
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
        LOG.info( '[Login] Writing cookie file ...')
        with open(self.cookie_file, 'w') as f:
            f.write(ts + ' ' + self.member_auth)


    def login(self):
        LOG.info( '[Login] login with email and password....')
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

    def read_link(self, link):
        headers = {'User-Agent':AGENT}
        headers['Cookie'] = 'member_auth=%s' % self.member_auth
        return requests.get(link,headers=headers)


