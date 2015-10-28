# -*- coding:utf-8 -*-
import time
import log, config, util
from os import path

LOG = log.get_logger("zxLogger")



Song_Type={0:'unknown',1:u"虾米", 2:"网易"}

class Handler(object):
    """
    handler class encapsulate xiami or netease object
    """
    def __init__(self, proxies = None):
        self.proxies = proxies
        self.need_proxy_pool = self.proxies != None

class Song(object):
    """
    General Song class, if song_json was given, 
    the group_dir and abs_path of the object needs to be set by the caller
    """


    def __init__(self):
        self.song_type=0
        self.url = ''
        self.group_dir = ''
        self.song_id = ''
        self.song_name=''
        self.dl_link = ''

        # lyrics link
        self.lyric_link = ''
        self.lyric_text = ''
        self.lyric_filename = ''
        self.lyric_abs_path = ''
        # artist_name
        self.artist_name = ''
        # album  name
        self.album_name = ''

        #used only for album/collection etc. create a dir to group all songs
        self.group_dir = None

        self.filename = ''
        
    def type_txt(self):
        return Song_Type[self.song_type]

    def post_set(self):
        """ set type_txt, filename, abs_path """
        if self.song_name:
            self.filename = self.song_name + u'.mp3'
            self.lyric_filename = self.song_name + u'.lrc'

            if not self.group_dir:
                self.filename = (self.artist_name + u"_" if self.artist_name  else "" ) + self.filename
                self.lyric_filename = (self.artist_name + u"_" if self.artist_name  else "" ) + self.lyric_filename

            #replace slash if there is
            self.filename = self.filename.replace('/','_')
            self.lyric_filename = self.lyric_filename.replace('/','_')
            
            if self.group_dir:
                self.abs_path = path.join(config.DOWNLOAD_DIR, self.group_dir, self.filename)
                self.lyric_abs_path = path.join(config.DOWNLOAD_DIR, self.group_dir, self.lyric_filename)
            else:
                # abs path for mp3 and lyric
                self.abs_path = path.join(config.DOWNLOAD_DIR,self.filename)
                self.lyric_abs_path = path.join(config.DOWNLOAD_DIR,self.lyric_filename)



