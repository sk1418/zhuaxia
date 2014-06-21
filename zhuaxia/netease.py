# -*- coding:utf-8 -*-
import time
import re
import requests
import log, config, util
import urllib
from os import path
import downloader
from obj import Song

LOG = log.get_logger("zxLogger")

#163 music api url
url_163="http://music.163.com"
url_album="http://music.163.com/api/album/%s/"
url_song="http://music.163.com/api/song/detail/?id=%s&ids=[%s]"
url_playlist="http://music.163.com/api/playlist/detail?id=%s"
url_artist_top_song = "tbd"

#agent string for http request header
AGENT= 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'


class NeteaseSong(Song):
    """
    163 Song class, if song_json was given, 
    Song.post_set() needs to be called for post-setting 
    abs_path, filename, etc.
    url example: http://music.163.com/song?id=209235
    """

    def __init__(self,o163,url=None,song_json=None):
        self.song_type=2
        self.o163 = o163
        self.group_dir = None
    #TODO for 163.com music, init_json should be called by init_url, or skip the "init_url"
        if url:
            self.url = url
            self.init_by_url(url)
            #set filename, abs_path etc.
            self.post_set()

        elif song_json:
            self.init_by_json(song_json)


    def init_by_url(self,url):
        self.song_id = re.search(r'(?<=/song?id=)\d+', url).group(0)

        j = self.o163.read_link(url_song % (self.song_id,self.song_id)).json()
        js = j['songs'][0]
        #name
        #self.song_name = j['song']['song_name'].replace('&#039;',"'")
        self.song_name = util.decode_html(j['songs'][0]['name'])
        # lyrics link
        self.lyrics_link = j['song']['song_lrc']
        # artist_name
        self.artist_name = j['song']['artist_name']
        # album id, name
        self.album_name = util.decode_html(j['song']['album_name'])
        self.album_id = j['song']['album_id']

        # download link
        self.dl_link = j['song']['song_location']
        #used only for album/collection etc. create a dir to group all songs
        self.group_dir = None

    def init_by_json(self, song_json ):
        """ the group dir and abs_path should be set by the caller"""

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

        #self.filename = (self.song_name + u'.mp3').replace('/','_')



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
            song = XiamiSong(self.xm, song_json=jsong)
            song.group_dir = song.artist_name + u'_' + song.album_name
            song.post_set()
            self.songs.append(song)

        d = path.dirname(self.songs[-1].abs_path)
        #creating the dir
        LOG.debug(u'创建专辑目录[%s]' % d)
        util.create_dir(d)

        #download album logo images
        LOG.debug(u'下载专辑[%s]封面'% self.album_name)
        downloader.download_by_url(self.logo, path.join(d,'cover.' +self.logo.split('.')[-1]))

        LOG.debug(u'保存专辑[%s]介绍'% self.album_name)
        if self.album_desc:
            self.album_desc = re.sub(r'&lt;\s*[bB][rR]\s*/&gt;','\n',self.album_desc)
            self.album_desc = re.sub(r'&lt;.*?&gt;','',self.album_desc)
            self.album_desc = util.decode_html(self.album_desc)
            import codecs
            with codecs.open(path.join(d,'album_description.txt'), 'w', 'utf-8') as f:
                f.write(self.album_desc)


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
                    song = XiamiSong(self.xm, song_json=jsong)
                    #rewrite filename, make it different
                    song.group_dir = 'favorite_%s' % self.uid
                    song.post_set()
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
            song.post_set()
            self.songs.append(song)
        if len(self.songs):
            #creating the dir
            util.create_dir(path.dirname(self.songs[-1].abs_path))

class TopSong(object):
    """download top songs of given artist"""
    def __init__(self, xm_obj, url):
        self.url = url
        self.xm = xm_obj
        #artist id
        self.artist_id = re.search(r'(?<=/artist/)\d+', self.url).group(0)
        self.artist_name = ""
        self.songs = []
        self.init_topsong()

    def init_topsong(self):
        j = self.xm.read_link(url_artist_top_song % (self.artist_id)).json()
        for jsong in j['songs']:
            song = XiamiSong(self.xm, song_json=jsong)
            song.group_dir = song.artist_name + '_TopSongs'
            song.post_set()
            self.songs.append(song)
            #check config for top X
            if len(self.songs) >= config.DOWNLOAD_TOP_SONG:
                break

        if len(self.songs):
            #set the artist name
            self.artist_name = self.songs[-1].artist_name
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


class Netease(object):

    def __init__(self, is_hq=False):
        self.is_hq = is_hq


    def read_link(self, link):
        headers = {'User-Agent':AGENT}
        headers['Referer'] = url_163
        headers['Cookie'] = 'appver=1.7.3'
        return requests.get(link, headers=headers)

    def encrypted_id(self,sfid):
        byte1 = bytearray('3go8&$8*3*3h0k(2)2')
        byte2 = bytearray(id)
        byte1_len = len(byte1)
        for i in xrange(len(byte2)):
            byte2[i] = byte2[i]^byte1[i%byte1_len]
        m = md5.new()
        m.update(byte2)
        result = m.digest().encode('base64')[:-1]
        result = result.replace('/', '_')
        result = result.replace('+', '-')
        return result
