# -*- coding:utf-8 -*-
import time
import urllib
import httplib
from contextlib import closing
from Cookie import SimpleCookie
from os import path

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
    def init(self,url):
        self.url = url

        
class Album(object):
    """The xiami album object"""
    def __init__(self, url):
        self.url = url 
        self.album_id = album_id

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
        self._auth = None
        self.cookie_file = cookie_file
        self.member_auth = ""

    def login_with_cookie(self):
        ts = str(int(time.time()))
        cookie_member_auth = None
        if path.exists(self.cookie_file):
            print 'read member_auth from cookie file ...'
            with open(self.cookie_file) as f:
                cif = f.read().split(' ')
                tm_valid = (int(ts) - int(cif[0])) > 18000 
                self._auth = cif[1]
                cookie_member_auth = self._auth
                auth = self.checkin()
                if auth != '0' or tm_valid:
                    cookie_member_auth = self.write_cookie(ts)
        else:
           cookie_member_auth = self.write_cookie(ts)
        self.member_auth = cookie_member_auth

    def write_cookie(self, ts):
        cookie_auth = self.login()
        print 'Writing cookie file ...'
        with open(self.cookie_file, 'w') as f:
            f.write(ts + ' ' + cookie_auth)
        return cookie_auth


    def login(self):
        print 'login with email and password....'
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
            conn.request('POST', '/web/login', data, headers)
            res = conn.getresponse()
            cookie = res.getheader('Set-Cookie')
            self._auth = SimpleCookie(cookie)['member_auth'].value
            print 'login success'
            return self._auth

    def checkin(self):
        if not self._auth:
            self.login()
        headers = checkin_headers
        headers['Cookie'] = 'member_auth=%s; t_sign_auth=1' % self._auth
        with closing(httplib.HTTPConnection('www.xiami.com')) as conn:
            conn.request('POST', '/task/signin', None, headers)
            res = conn.getresponse()
            return res.read()

if __name__ == '__main__':
    xm = Xiami('kent.yuan@gmail.com', '######','/tmp/test/xm.cookie')
    xm.login_with_cookie();
