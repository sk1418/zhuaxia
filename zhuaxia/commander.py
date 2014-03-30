# -*- coding:utf-8 -*-

import sys
import config ,util ,logging ,log,downloader
import xiami as xm

LOG = log.get_logger("zxLogger")

dl_songs = []


def from_file(xm_obj, input):
    """ download objects (songs, albums...) from an input file.  """
    pass


def parse_and_prepare(xm_obj, url, verbose=False):
    """ parse the input string (xiami url), and do download"""
    if '/song/' in url:
        song = xm.Song(xm_obj, url=url)
        LOG.info('Parsing "%s" ..... [Song] %s'% url, song.song_name)
        dl_songs.append(song)
    if '/album/' in url:
        album = xm.Album(xm_obj, url)
        msg = ['Parsing: "%s" ..... [Album] %s'% (url,album.album_name)]
        if verbose:
            for s in album.songs:
                msg.append('[Song] %s'%s.song_name)
            LOG.info('\n    |-> '.join(msg))
        else:
            msg.append('%d Songs.' % len(album.songs))
            LOG.info( ' | '.join(msg))
        dl_songs.append(album.songs)
    if '/lib-song/u/' in url:
        fav = xm.Favorite(xm_obj.url)
        msg = ['Parsing: "%s" ..... [Favorite] %s'% (url,album.album_name)]
        if verbose:
            for s in fav.songs:
                msg.append('[Song] %s'%s.song_name)
            LOG.info('\n    |-> '.join(msg))
        else:
            msg.append('%d Songs.' % len(fav.songs))
            LOG.info( ' | '.join(msg))
        dl_songs.append(album.songs)

    else:
        pass
