# -*- coding:utf-8 -*-
from obj import History
import log
import config
import datetime
import sqlite3 as sqlite

LOG = log.get_logger("zxLogger")
SELECT_PART="""Select id, song_id, song_name, hq, source, location, api_url, dl_time, times FROM History """
INSERT_STMT = """Insert into History (song_id, song_name, hq, source, location, api_url, dl_time )
    values(?,?,?,?,?,?,?)"""



def __getConnection():
    conn = sqlite.connect(config.HIST_DB)
    return conn

def insert_hist(songs):
    """
    insert histories entry if it is not yet exists (check unique constraint)
    otherwise skip insertion
    """
    conn = __getConnection()
    dao = HistDao(conn)
    for song in songs:
        if song.success:
            hist = dao.get_history(song)
            if hist:
                dao.update_history(hist,song)
            else:
                dao.insert_history(song)
    conn.commit()
    conn.close()
    
def filter_songs(songs):
    conn = __getConnection()
    dao = HistDao(conn)
    skipped = [song for song in songs if dao.get_history(song)]
    songs = [song for song in songs if song not in skipped]
    conn.close()
    return skipped


def empty_history():
    """
    remove all history data
    """
    conn = __getConnection()
    dao = HistDao(conn)
    dao.delete_all(conn)
    conn.commit()
    conn.close()



class HistDao(object):
    def __init__(self,conn):
        self.conn = conn

    def get_history(self,song):
        LOG.debug("get history for song:%s",song.song_name)
        sql = SELECT_PART + """ where song_id=? and source=? and hq=? """
        cur = self.conn.cursor()
        cur.execute(sql, (song.song_id, song.song_type, song.handler.is_hq))
        hist = self.__row2hist( cur.fetchone())
        cur.close()
        return hist
    
    def insert_history(self, song):
        sql = INSERT_STMT
        cur = self.conn.cursor()
        cur.execute(sql, (song.song_id, song.song_name, \
                         song.handler.is_hq, song.song_type, song.abs_path, \
                          song.dl_link, datetime.datetime.today() ))
        cur.close()

    def update_history(self, hist, song):
        sql = """update History set 
            times=times+1, dl_time=?, location, api_url
            where id=?"""
        cur = self.conn.cursor()
        cur.execute(sql, (datetime.datetime.today(), song.abs_pat, song.dl_link, hist.id ))
        cur.close()

    def delete_all(self):
        sql = """delete from History"""
        LOG.debug("empty history data")
        cur = self.conn.cursor()
        cur.execute(sql)
        cur.close()

    def __row2hist(self, row):
        if row:
            hist = History()
            (hist.id, hist.song_id, hist.song_name, \
             hist.hq, hist.source, hist.location, \
             hist.api_url, hist.dl_time, hist.times) = row
            return hist
        return None


