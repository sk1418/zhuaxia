# -*- coding:utf-8 -*-

####################################################################
# taken from https://gist.github.com/lepture/1014329
####################################################################
#
# Copyright (c) 2011, lepture.com
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#    * Neither the name of the author nor the names of its contributors
#      may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import urllib
import httplib
from contextlib import closing
from Cookie import SimpleCookie

ua = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'
#ua = 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'

checkin_headers = {
    'User-Agent': ua,
    'Content-Length': '0',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'www.xiami.com',
    'Origin': 'http://www.xiami.com/',
    'Referer': 'http://www.xiami.com/',
    'Content-Length': '0',
}

class xiami_login(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self._auth = None

    def login(self):
        print 'login ....'
        _form = {
            'email': self.email,
            'password': self.password,
            'LoginButton': '登录',
        }
        data = urllib.urlencode(_form)
        headers = {'User-Agent': ua}
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

####################################################################
