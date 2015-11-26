# -*- coding:utf-8 -*-
head_xm                          = u'[虾]'
head_163                         = u'[易]'

fmt_insert_hist                  = u' 为成功下载建立历史记录...'
fmt_all_finished                 = u' 所有任务都已完成'
fmt_dl_lyric_start               = u' 开始下载歌词...'
fmt_dl_header                    = u' 保存目录:[%s] | 线程池:[%d]\n'
fmt_dl_progress                  = u'总进度[%d/%d]:'
fmt_dl_last_finished             = u'  最近%d个完成任务:\n'
fmt_dl_failed_jobs               = u'  失败的任务:\n'

fmt_quality_fallback             = u'歌曲(%s) 无法获取128kbps资源,尝试获取低质量资源'

fmt_init_song                    = u'开始初始化歌曲[%s]'
fmt_err_song_parse               = u'无法解析/下载歌曲链接: [%s]'
fmt_init_song_ok                 = u'初始化歌曲成功[%s]'
fmt_init_album                   = u'开始初始化专辑[%s]'
fmt_create_album_dir             = u'创建专辑目录[%s]'
fmt_dl_album_cover               = u'下载专辑[%s]封面'
fmt_save_album_desc              = u'保存专辑[%s]介绍'
fmt_init_fav                     = u'开始初始化用户收藏[%s]'
fmt_parse_song_url               = u'解析歌曲链接[%s]'
fmt_init_fav_ok                  = u'初始化用户收藏完毕[%s]'
fmt_init_collect                 = u'开始初始化精选集[%s]'
fmt_init_collect_ok              = u'初始化精选集完毕[%s]'
fmt_init_artist                  = u'初始化艺人TopSong[%s]'
fmt_init_artist_ok               = u'初始化艺人TopSong完毕[%s]'
dl_128kbps_xm                    = u' 不登录虾米进行下载, 虾米资源质量为128kbps.'
fmt_login_ok_xm                  = u'[Login] 用户: %s (id:%s) 登录成功.'
login_xm                         = u' 登录虾米...'
login_err_xm                     = u' 登录失败, 略过登录, 虾米资源质量为 128kbps.'

short_xm                         = head_xm + ' '
short_163                        = head_163 + ' '
fmt_parsing                      = u'解析: "%s" ..... [%s] %s'
fmt_has_song_nm                  = u'包含%d首歌曲.'
fmt_single_song                  = u'[曲目] %s'
init_proxypool                   = u'初始化proxy pool'
fmt_init_proxypool_done          = u'proxy pool:[%d] 初始完毕'
fmt_skip_dl_nm                   = u' 启用增量下载, %d首歌曲曾下载过,忽略下载'
fmt_total_dl_nm                  = u' 下载任务总数: %s\n 3秒后开始下载'
no_dl_task                       = u' 没有可下载任务,自动退出.'
fmt_skip_unknown_url             = u' 略过不能识别的url [%s].'
fmt_xm_unknown_url               = u'%s [虾]不能识别的url [%s].'
fmt_163_unknow_url               = u'%s [易]不能识别的url [%s].'
song                             = u'曲目'
album                            = u'专辑'
playlist                         = u'歌单'
artistTop                        = u'艺人热门歌曲'
collection                       = u'精选集'
favorite                         = u'用户收藏'
warning_many_collections         = u'[虾]如用户收藏较多，解析歌曲需要较长时间，请耐心等待'
fmt_links_in_file                = u' 文件包含链接总数: %d'

experimental                     = u'-p 选项为实验性选项. 自动获取代理服务器池解析/下载。因代理服务器稳定性未知，下载可能会慢或不稳定。'
ver_text                         = u'zhuaxia (抓虾) '
help_info                        = u""" %(cyan)s
    zhuaxia (抓虾) -- 抓取[虾米音乐]和[网易云音乐]的 mp3 音乐%(clear)s

    [%(uline)sCONFIG FILE:%(clear)s]   $HOME/.zhuaxia/zhuaxia.conf

    [%(uline)sOPTIONS%(clear)s]
        %(bold)s-H%(clear)s : 首选HQ质量(320kbps),
            > 虾米音乐 <
                - 配置文件中需给出正确登录信箱和密码, 登录用户需拥有VIP身份
                - 用户需在xiami vip设置页面设置默认高音质
                - 此选项对不满足上两项情况无效，仍下载128kbps资源
            > 网易音乐 <
                -无需特殊要求,直接下载高音质资源

        %(bold)s-p%(clear)s : (实验性选项)使用代理池下载
            在下载/解析量大的情况下，目标服务器会对禁止频繁的请求，所以zhuaxia可以自动获取
            代理来解析和下载资源。因为获取的代理速度/可靠性不一，下载可能会缓慢或不稳定。

        %(bold)s-h%(clear)s ：显示帮助
        %(bold)s-l%(clear)s ：下载歌曲的lrc格式歌词
        %(bold)s-f%(clear)s ：从文件下载
        %(bold)s-v%(clear)s ：显示版本信息

    [%(uline)sUSAGE%(clear)s]

        %(bold)szx [OPTION] <URL>%(clear)s
            : 下载指定URL资源, 抓虾自动识别链接, 支持
                - [虾] 歌曲，专辑，精选集，用户收藏,艺人TopN
                - [易] 歌曲，专辑，歌单，艺人TopN
            例子：
              zx "http://www.xiami.com/space/lib-song/u/25531126"
              zx "http://music.163.com/song?id=27552647"

        %(bold)szx [OPTION] -f <file>%(clear)s
            : 多个URL在一个文件中，每个URL一行。 URLs可以是混合[虾]和[易]的不同类型音乐资源。例子：
              >$ cat /tmp/foo.txt
                http://music.163.com/artist?id=5345
                http://www.xiami.com/song/1772130322
                http://music.163.com/album?id=2635059
                http://www.xiami.com/album/32449
              >$ zx -f /tmp/foo.txt
        """
