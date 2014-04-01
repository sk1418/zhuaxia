# -*- coding:utf-8 -*-
import time
import re
import requests
import log, config, util
from os import path
import downloader

LOG = log.get_logger("zxLogger")

#xiami android/iphone api urls
url_xiami="http://www.xiami.com"
url_login="https://login.xiami.com/member/login"
url_song = "http://www.xiami.com/app/android/song?id=%s"
url_album = "http://www.xiami.com/app/android/album?id=%s"
url_fav = "http://www.xiami.com/app/android/lib-songs?uid=%s&page=%s"
url_collection = "http://www.xiami.com/app/android/collect?id=%s"
#url_artist_albums = "http://www.xiami.com/app/android/artist-albums?id=%s&page=%s"
#url_artist_top_song = "http://www.xiami.com/app/android/artist-topsongs?id=%s"

#agent string for http request header
AGENT= 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'

class Song(object):
    """
    xiami Song class, if song_json was given, 
    the group_dir and abs_path of the object needs to be set by the caller
    """

    def __init__(self,xiami_obj,url=None,song_json=None):
        self.xm = xiami_obj
        self.group_dir = None
        if url:
            self.url = url
            self.init_by_url(url)
        elif song_json:
            self.init_by_json(song_json)


    def init_by_json(self, song_json):
        """ the group dir and abs_path would be set by the caller"""

        self.song_id = song_json['song_id']
        self.album_id = song_json['album_id']
        self.song_name = util.decode_html(song_json['name'])
        self.dl_link = song_json['location']
        # lyrics link
        self.lyrics_link = song_json['lyric']
        # artist_name
        self.artist_name = song_json['artist_name']
        # album id, name
        self.album_name = song_json['title']

        self.filename = self.song_name + u'.mp3'

    def init_by_url(self,url):
        self.song_id = re.search(r'(?<=/song/)\d+', url).group(0)
        j = self.xm.read_link(url_song % self.song_id).json()
        #name
        self.song_name = j['song']['song_name'].replace('&#039;',"'")
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
        self.filename = (self.artist_name + u"_" if self.artist_name  else "" ) + self.song_name + u'.mp3'
        self.abs_path = path.join(config.DOWNLOAD_DIR,self.filename)


class Album(object):
    """The xiami album object"""
    def __init__(self, xm_obj, url):

        self.xm = xm_obj
        self.url = url 
        self.album_id = re.search(r'(?<=/album/)\d+', self.url).group(0)
        LOG.debug(u'开始初始化专辑[%s]'% self.album_id)

        self.year = None
        self.track=None
        self.songs = [] # list of Song
        self.init_album()

    def init_album(self):
        j = self.xm.read_link(url_album % self.album_id).json()['album']
        #name
        self.album_name = j['title']
        #album logo
        self.logo = j['album_logo']
        # artist_name
        self.artist_name = j['artist_name']

        #description
        self.album_desc = j['description']

        #handle songs
        for jsong in j['songs']:
            song = Song(self.xm, song_json=jsong)
            song.group_dir = song.artist_name + u'_' + song.album_name
            song.abs_path = path.join(config.DOWNLOAD_DIR, song.group_dir, song.filename)
            self.songs.append(song)

        d = path.dirname(self.songs[-1].abs_path)
        #creating the dir
        LOG.debug(u'创建专辑目录[%s]' % d)
        util.create_dir(d)

        #download album logo images
        LOG.debug(u'下载专辑[%s]封面'% self.album_name)
        downloader.download_by_url(self.logo, path.join(d,'cover.' +self.logo.split('.')[-1]))


class Favorite(object):
    """ xiami Favorite songs by user"""
    def __init__(self,xm_obj, url):
        self.url = url
        self.xm = xm_obj
        #user id in url
        self.uid = re.search(r'(?<=/lib-song/u/)\d+', self.url).group(0)
        self.songs = []
        self.init_fav()

    def init_fav(self):
        page = 1
        while True:
            j = self.xm.read_link(url_fav % (self.uid, str(page)) ).json()
            if j['songs'] :
                for jsong in j['songs']:
                    song = Song(self.xm, song_json=jsong)
                    #rewrite filename, make it different
                    song.group_dir = 'favorite_%s' % self.uid
                    song.abs_path = path.join(config.DOWNLOAD_DIR, song.group_dir, song.filename)
                    self.songs.append(song)
                page += 1
            else:
                break
        if len(self.songs):
            #creating the dir
            util.create_dir(path.dirname(self.songs[-1].abs_path))
            
class Collection(object):
    """ xiami song - collections made by user"""
    def __init__(self,xm_obj, url):
        self.url = url
        self.xm = xm_obj
        #user id in url
        self.collection_id = re.search(r'(?<=/showcollect/id/)\d+', self.url).group(0)
        self.songs = []
        self.init_collection()

    def init_collection(self):
        j = self.xm.read_link(url_collection % (self.collection_id) ).json()['collect']
        self.collection_name = j['name']
        for jsong in j['songs']:
            song = Song(self.xm, song_json=jsong)
            #rewrite filename, make it different
            song.group_dir = self.collection_name
            song.abs_path = path.join(config.DOWNLOAD_DIR, song.group_dir, song.filename)
            self.songs.append(song)
        if len(self.songs):
            #creating the dir
            util.create_dir(path.dirname(self.songs[-1].abs_path))
            


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
        self.member_auth = ''
        #do login
        #self.login_with_cookie()
        self.login()
        


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
            #'submit': '登录',
        }
        headers = {'User-Agent': AGENT}
        headers['Referer'] = url_login
        # do http post login
        try:
            sess = requests.Session()
            sess.headers['User-Agent'] = AGENT
            sess.verify = False
            sess.mount('https://', requests.adapters.HTTPAdapter())
            #res = sess.post(url_login, data=_form)
            #self.memeber_auth = sess.cookies['member_auth']
            #LOG.info( 'login success')
            return True
        except:
            LOG.error( "login failed")
            return False

    def read_link(self, link):
        headers = {'User-Agent':AGENT}
        headers['Cookie'] = 'member_auth=%s' % self.member_auth
        return requests.get(link,headers=headers)


