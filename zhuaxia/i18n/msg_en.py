# -*- coding:utf-8 -*-
head_xm                          = u'[xia]'
head_163                         = u'[163]'

#summary
fmt_summary_skip_title           = u'Incremental downloading skipped mp3:'
fmt_summary_skip_header          = u'Source\t  Last DL_Time  \tName\tLocation'
fmt_summary_success_title        = u'Successful Downloadings'
fmt_summary_success_header       = u'Name\tLocation'
fmt_summary_failed_title         = u'Failed Downloadings:'
fmt_summary_failed_header        = u'Name\tLocation'
summary_prompt                   = u'(q)uit/(v)iew summary/(s)ave summary. Please input [q/v/s]:'
summary_prompt_err               = u"Invalid input.\n" 
summary_saved                    = u" summary was saved at: %s" 

history_clear_confirm            = u" %d downloading histories found. Are you sure to remove all these histories? [y/n]" 
history_clearing                 = u" Clear zhuaxia downloading hisotory (other options will be ignored)" 
history_cleared                  = u" All zhuaxia download history has been cleared." 
history_exporting                = u" Exporting download history (other options will be ignored)..." 
history_exported                 = u" Zhuaxia download-history was exported to: %s" 

fmt_all_finished                 = u' All jobs are finished.'
fmt_insert_hist                  = u' Recording history for successful downloads...'
fmt_dl_lyric_start               = u' Start downloading lyrics...'

fmt_dl_header                    = u' Save to :[%s] | Threads Pool:[%d]\n'
fmt_dl_progress                  = u'Progress [%d/%d]:'
fmt_dl_last_finished             = u'  Latest %d finished task:\n'
fmt_dl_failed_jobs               = u'  Failed downloading task:\n'

fmt_quality_fallback             = u'cannot find 128kbps song (%s). Try to get lower quality resource'
fmt_init_song                    = u'start init song [%s]'
fmt_err_song_parse               = u'song url cannot be parsed/downloaded: [%s]'
fmt_init_song_ok                 = u'song initialized [%s]'
fmt_init_album                   = u'start init album [%s]'
fmt_create_album_dir             = u'creating album dir [%s]'
fmt_dl_album_cover               = u'downloading cover of album [%s]'
fmt_save_album_desc              = u'downloading description of album [%s]'
fmt_init_fav                     = u'start init user favorite [%s]'
fmt_parse_song_url               = u'parsing song url [%s]'
fmt_init_fav_ok                  = u'user favorite initialized [%s]'
fmt_init_collect                 = u'start init collection [%s]'
fmt_init_collect_ok              = u'collection initialized [%s]'
fmt_init_artist                  = u'start init artist TopSong [%s]'
fmt_init_artist_ok               = u' artist TopSong initialized [%s]'
dl_128kbps_xm                    = u' downloading without login. quality: 128kbps'
fmt_login_ok_xm                  = u'[Login] user: %s (id:%s) login successful'
login_xm                         = u'[xia] login...'
login_err_xm                     = u' login failed, skip login, using 128kbps quality.'
short_xm                         = head_xm + ' '
short_163                        = head_163 + ' '
fmt_parsing                      = u'Parsing: "%s" ..... [%s] %s'
fmt_has_song_nm                  = u'has %d songs.'
fmt_single_song                  = u'[song] %s'
init_proxypool                   = u'Init proxy pool'
fmt_init_proxypool_done          = u'proxy pool:[%d] init done'
fmt_skip_dl_nm                   = u' Incremental download is active, skipping %d already downloaded songs.'
fmt_total_dl_nm                  = u' Total downloading tasks: %s\n Downloading starts in 3 seconds'
no_dl_task                       = u' No downloading task, exit.'
fmt_skip_unknown_url             = u' Skipping unknown url [%s].'
fmt_xm_unknown_url               = u'%s [xia]unknown url [%s].'
fmt_163_unknow_url               = u'%s [163]unknown url [%s].'
song                             = u'song'
album                            = u'album'
playlist                         = u'playlist'
artistTop                        = u'artist TopN'
collection                       = u'collection'
favorite                         = u'user favorite'
warning_many_collections         = u'[xia] parsing can take some time if user favorite has many songs. Please stand by.'
fmt_links_in_file                = u' file contains urls: %d'

experimental                     = u'-p is an experimental option. Auto fetching proxy from proxy pool. Downloading could be slow or unstable due to the unknown proxy status.'
ver_text                         = u'zhuaxia '
help_info                        = u""" 
    zhuaxia -- download mp3 music from [xiami.com] and [music.163.com]

    [CONFIG FILE:]  $HOME/.zhuaxia/zhuaxia.conf
                    It will be automatically created when zhuaxia was started first time.

    [OPTIONS]
        -H : prefer High Quality(320kbps),
            > xiami <
                - xiami vip user email/password should be set in config
                - user should set HQ on xiami vip setting page
                - if any above requirements was not satisfied, 128kbps will be taken
            > 163 <
                - no special requirement

        -h : show this help

        -l : download lyric too (lrc format)

        -f : download from url file (see example in [USAGE])

        -i : incremental downloading
             zhuaxia will check download history and skip the mp3 if it has been downloaded before.
             To identify a downloaded mp3, the combination of these three attributes will be checked:
             song_id(id in xiami/netease), source (xiami/netease), quality (H/L)

        -e : export history data to file, if this option was given, other options will be ignored.

        -d : clear all history data, if this option was given, other options will be ignored.
             -e and -d cannot be used together.

        -v : show version information

        -p : auto choose proxy from proxy pool (experimental option)
             when frequency of request to target host is high enough, host could ban the client
             for some time. zhuaxia will auto take proxy from pool. However this may make
             downloading slow or unstable.

    [USAGE]

        zx [OPTION] <URL>

             auto recognize and download the given url resource, supports:
                - [xm] song, album, favorite, collection, artist TopN
                - [163]song, album, list, artist topN

        Example:
                zx "http://www.xiami.com/space/lib-song/u/25531126"
                zx "http://music.163.com/song?id=27552647"

        zx [OPTION] -f <file>

            download from url file. one url per line. The urls could be 163 and xm mixed. Example:

        Example:
              $ cat /tmp/foo.txt
                http://music.163.com/artist?id=5345
                http://www.xiami.com/song/1772130322
                http://music.163.com/album?id=2635059
                http://www.xiami.com/album/32449

              $ zx -f /tmp/foo.txt

        Other Examples:

                download lyrics with songs: 
                    zx -l "http://music.163.com/song?id=27552647"

                incremental download songs with lyrics: 
                    zx -li "http://music.163.com/song?id=27552647"

                export zhuaxia download history. File will be save under "download.dir" in config file:
                    zx -e

                clear(delete) all zhuaxia download history:
                    zx -d
                
        """

