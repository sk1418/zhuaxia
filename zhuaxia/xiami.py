# -*- coding:utf-8 -*-
import time
import re
import requests
import log, config, util, proxypool
import urllib
from os import path
import sys
import downloader
from obj import Song, Handler
from bs4 import BeautifulSoup

LOG = log.get_logger("zxLogger")

if config.LANG.upper() == 'CN':
    import i18n.msg_cn as msg
else:
    import i18n.msg_en as msg
#----------------------------------------------
#|                 xiami api                  |
#----------------------------------------------
xm_type_dict={
        'song':'0',
        'album':'1',
        'artist':'2',
        'collection':'3',
        'random':'7',
        'favorite':'0',
        'recommendation':'8'
    }
url_xiami="http://www.xiami.com"
url_login="https://login.xiami.com/member/login"
url_parts = ('http://www.xiami.com/song/playlist/id/%s/type/', '/cat/json')
url_song =  xm_type_dict['song'].join(url_parts)
url_album = xm_type_dict['album'].join(url_parts)
url_artist_top_song= xm_type_dict['artist'].join(url_parts)
url_collection= xm_type_dict['collection'].join(url_parts)
url_fav = "http://www.xiami.com/space/lib-song/u/%s/page/%s"

#agent string for http request header
AGENT= 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'


class XiamiSong(Song):
    """
    xiami Song class, if song_json was given, 
    Song.post_set() needs to be called for post-setting 
    abs_path, filename, etc.
    """

    def __init__(self,xiami_obj,url=None,song_json=None):
        Song.__init__(self)
        # self.lyric_text = ''
        self.song_type=1
        self.handler = xiami_obj
        # self.group_dir = None
        if url:
            self.url = url
            self.song_id = re.search(r'(?<=/song/)\d+', url).group(0)
            LOG.debug(msg.head_xm + msg.fmt_init_song % self.song_id)

            #get the song json data
            try:
                jsong = self.handler.read_link(url_song % self.song_id).json()['data']['trackList'][0]
            except Exception, err:
                LOG.error(msg.head_xm + msg.fmt_err_song_parse %url)
                LOG.debug(self.handler.read_link(url_song % self.song_id).text)
                raise
                

            self.init_by_json(jsong)
            #used only for album/collection etc. create a dir to group all songs
            self.group_dir = None

            #set filename, abs_path etc.
            self.post_set()
            LOG.debug(msg.head_xm + msg.fmt_init_song_ok % self.song_id)
        elif song_json:
            self.init_by_json(song_json)
        
        #if is_hq, get the hq location to overwrite the dl_link
        if self.handler.is_hq:
            try:
                self.dl_link = self.handler.get_hq_link(self.song_id)
            except:
                #if user was not VIP, don't change the dl_link
                pass


    def init_by_json(self, song_json ):
        """ the group dir and abs_path should be set by the caller"""

        self.song_id = song_json['song_id']
        self.album_id = song_json['album_id']
        self.song_name = util.decode_html(song_json['title'])
        location = song_json['location']
        #decode download link
        self.dl_link = self.handler.decode_xiami_link(location)
        # set lyrics link if dl_lyric flag is true
        self.lyric_link = song_json['lyric_url'] if self.handler.dl_lyric else ''
        # artist_name
        self.artist_name = song_json['artist']
        # album id, name
        self.album_name = util.decode_html(song_json['album_name'])


class Album(object):
    """The xiami album object"""
    def __init__(self, xm_obj, url):
        self.handler = xm_obj
        self.url = url 
        self.album_id = re.search(r'(?<=/album/)\d+', self.url).group(0)
        LOG.debug(msg.head_xm + msg.fmt_init_album % self.album_id)
        self.year = None
        self.track=None
        self.songs = [] # list of Song
        self.init_album()

    def init_album(self):
        j = self.handler.read_link(url_album % self.album_id).json()['data']['trackList']
        j_first_song = j[0]
        #name
        self.album_name = util.decode_html(j_first_song['album_name'])
        #album logo
        self.logo = j_first_song['album_pic']
        # artist_name
        self.artist_name = j_first_song['artist']

        #description
        html = self.handler.read_link(self.url).text
        soup = BeautifulSoup(html,'html.parser')
        self.album_desc = soup.find('span', property="v:summary").text

        #handle songs
        for jsong in j:
            song = XiamiSong(self.handler, song_json=jsong)
            song.group_dir = self.artist_name + u'_' + self.album_name
            song.group_dir = song.group_dir.replace('/','_')
            song.post_set()
            self.songs.append(song)

        d = path.dirname(self.songs[-1].abs_path)
        #creating the dir
        LOG.debug(msg.head_xm + msg.fmt_create_album_dir % d)
        util.create_dir(d)

        #download album logo images
        LOG.debug(msg.head_xm + msg.fmt_dl_album_cover % self.album_name)
        downloader.download_url(self.logo, path.join(d,'cover.' +self.logo.split('.')[-1]))

        LOG.debug(msg.head_xm + msg.fmt_save_album_desc % self.album_name)
        if self.album_desc:
            self.album_desc = re.sub(r'&lt;\s*[bB][rR]\s*/&gt;','\n',self.album_desc)
            self.album_desc = re.sub(r'&lt;.*?&gt;','',self.album_desc)
            self.album_desc = util.decode_html(self.album_desc)
            import codecs
            with codecs.open(path.join(d,'album_description.txt'), 'w', 'utf-8') as f:
                f.write(self.album_desc)




class Favorite(object):
    """ xiami Favorite songs by user"""
    def __init__(self,xm_obj, url, verbose):
        self.verbose = verbose
        self.url = url
        self.handler = xm_obj
        #user id in url
        self.uid = re.search(r'(?<=/lib-song/u/)\d+', self.url).group(0)
        self.songs = []
        self.init_fav()

    def init_fav(self):
        """ parse html and load json and init Song object
        for each found song url"""
        page = 1
        user = ''
        total = 0
        cur = 1 #current processing link
        LOG.debug(msg.head_xm + msg.fmt_init_fav % self.uid)
        while True:
            html = self.handler.read_link(url_fav%(self.uid,page)).text
            soup = BeautifulSoup(html,'html.parser')
            if not user:
                user = soup.title.string
            if not total:
                total = soup.find('span', class_='counts').string

            links = [link.get('href') for link in soup.find_all(href=re.compile(r'xiami.com/song/\d+')) if link]
            if links:
                for link in links:
                    LOG.debug(msg.head_xm + msg.fmt_parse_song_url % link)
                    if self.verbose:
                        sys.stdout.write(log.hl('[%d/%s] parsing song ........ '%(cur, total), 'green'))
                        sys.stdout.flush()
                    try:
                        cur += 1
                        song = XiamiSong(self.handler, url=link)
                        #time.sleep(2)
                        if self.verbose:
                            sys.stdout.write(log.hl('DONE\n', 'green'))
                    except:
                        sys.stdout.write(log.hl('FAILED\n', 'error'))
                        continue
                    #rewrite filename, make it different
                    song.group_dir = user
                    song.post_set()
                    self.songs.append(song)
                page += 1
            else:
                break

        if len(self.songs):
            #creating the dir
            util.create_dir(path.dirname(self.songs[-1].abs_path))
        LOG.debug(msg.head_xm + msg.fmt_init_fav_ok % self.uid)

class Collection(object):
    """ xiami song - collections made by user"""
    def __init__(self,xm_obj, url):
        self.url = url
        self.handler = xm_obj
        #user id in url
        self.collection_id = re.search(r'(?<=/collect/)\d+', self.url).group(0)
        self.songs = []
        self.init_collection()

    def init_collection(self):
        LOG.debug(msg.head_xm + msg.fmt_init_collect % self.collection_id)
        j = self.handler.read_link(url_collection % (self.collection_id) ).json()['data']['trackList']
        j_first_song = j[0]
        #read collection name
        self.collection_name = self.get_collection_name()
        for jsong in j:
            song = XiamiSong(self.handler, song_json=jsong)
            #rewrite filename, make it different
            song.group_dir = self.collection_name
            song.post_set()
            self.songs.append(song)
        if len(self.songs):
            #creating the dir
            util.create_dir(path.dirname(self.songs[-1].abs_path))
        LOG.debug(msg.head_xm + msg.fmt_init_collect_ok % self.collection_id)

    def get_collection_name(self):
        if not self.url:
            return 'collection' + self.collection_id
        else:
            html = self.handler.read_link(self.url).text
            soup = BeautifulSoup(html,'html.parser')
            title = soup.title.string
            if title:
                return re.sub(r'_[^_]*$', '', title)
            else: 
                return 'collection' + self.collection_id

class TopSong(object):
    """download top songs of given artist"""
    def __init__(self, xm_obj, url):
        self.url = url
        self.handler = xm_obj
        #artist id
        id_regexs=(
                r'(?<=/artist/top/id/)\d+',
                r'(?<=/artist/top-)\d+',
                r'(?<=/artist/)\d+'
                )
        for id_regex in id_regexs:
            matched = re.search(id_regex, self.url)
            if matched:
                self.artist_id = matched.group(0)
                break

        self.artist_name = ""
        self.songs = []
        self.init_topsong()

    def init_topsong(self):
        LOG.debug(msg.head_xm + msg.fmt_init_artist% self.artist_id)
        j = self.handler.read_link(url_artist_top_song % (self.artist_id)).json()['data']['trackList']
        for jsong in j:
            song = XiamiSong(self.handler, song_json=jsong)
            if not self.artist_name:
                self.artist_name = song.artist_name
            song.group_dir = self.artist_name + '_TopSongs'
            song.post_set()
            self.songs.append(song)
            #check config for top X
            if config.DOWNLOAD_TOP_SONG>0 and len(self.songs) >= config.DOWNLOAD_TOP_SONG:
                break

        if len(self.songs):
            #set the artist name
            self.artist_name = self.songs[-1].artist_name
            #creating the dir
            util.create_dir(path.dirname(self.songs[-1].abs_path))
        LOG.debug(msg.head_xm + msg.fmt_init_artist_ok % self.artist_id)

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


class Xiami(Handler):

    def __init__(self, email, password, option):
        self.token = None
        self.uid = ''
        self.user_name = ''
        self.email = email
        self.password = password
        self.skip_login = False
        self.session = None
        self.is_hq = option.is_hq
        self.dl_lyric = option.dl_lyric
        self.proxy = option.proxy
        Handler.__init__(self,option.proxy_pool)

        #if either email or password is empty skip login
        if not email or not password or not self.is_hq:
            self.skip_login = True
            
        self.member_auth = ''
        #do login
        if self.skip_login:
            LOG.warning(msg.head_xm + msg.dl_128kbps_xm)
            is_hq = False
        else:
            if self.login():
                LOG.info( msg.head_xm + msg.fmt_login_ok_xm % (self.user_name.decode('utf-8'),self.uid) )
            else:
                self.is_hq = False

    def login(self):
        LOG.info( msg.head_xm + msg.login_xm)
        _form = {
            'email': self.email,
            'password': self.password,
            'submit': '登 录',
        }
        headers = {'User-Agent': AGENT}
        headers['Referer'] = url_login
        # do http post login
        try:
            sess = requests.Session()
            sess.headers['User-Agent'] = AGENT
            sess.verify = False
            sess.mount('https://', requests.adapters.HTTPAdapter())
            self.session = sess
            res = sess.post(url_login, data=_form)
            self.memeber_auth = sess.cookies['member_auth']
            self.uid, self.user_name = urllib.unquote(sess.cookies['user']).split('"')[0:2]
            self.token = sess.cookies['_xiamitoken']
            return True
        except:
            LOG.warning(msg.head_xm + msg.login_err_xm)
            self.is_hq = False
            return False

    def read_link(self, link):
        headers = {'User-Agent':AGENT}
        #headers['Referer'] = 'http://img.xiami.com/static/swf/seiya/player.swf?v=%s'%str(time.time()).replace('.','')


        requests_proxy = None
        if self.proxy:
            requests_proxy = { 'http':self.proxy}

        if self.need_proxy_pool:
            requests_proxy = {'http':self.proxy_pool.get_proxy()}

        retVal = None
        if self.need_proxy_pool:
            while True:
                try:
                    if self.skip_login:
                        retVal =  requests.get(link, headers=headers, proxies=requests_proxy)
                    else:
                        retVal =  self.session.get(link,headers=headers, proxies=requests_proxy)
                    break 
                except requests.exceptions.ConnectionError:
                    LOG.debug('invalid proxy detected, removing from pool')
                    self.proxies.del_proxy(requests_proxy['http'])
                    if self.proxies:
                        requests_proxy['http'] = self.proxies.get_proxy()
                    else:
                        LOG.debug('proxy pool is empty')
                        raise
                        break
        else:
            if self.skip_login:
                retVal =  requests.get(link, headers=headers, proxies=requests_proxy)
            else:
                retVal =  self.session.get(link,headers=headers, proxies=requests_proxy)

        return retVal


    def get_hq_link(self, song_id):
        mess = self.read_link(url_hq%song_id).json()['location']
        return self.decode_xiami_link(mess)

    def decode_xiami_link(self,mess):
        """decode xm song link"""
        rows = int(mess[0])
        url = mess[1:]
        len_url = len(url)
        cols = len_url / rows
        re_col = len_url % rows # how many rows need to extend 1 col for the remainder

        l = []
        for row in xrange(rows):
            ln = cols + 1 if row < re_col else cols
            l.append(url[:ln])
            url = url[ln:]

        durl = ''
        for i in xrange(len_url):
            durl += l[i%rows][i/rows]

        return urllib.unquote(durl).replace('^', '0')
