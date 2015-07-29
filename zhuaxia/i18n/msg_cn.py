# -*- coding:utf-8 -*-
experimental=u'-p 选项为实验性选项：'
proxypool=u'为防止频繁请求被禁止，自动获取代理服务器池解析/下载。因代理服务器速度不同，下载可能会慢或不稳定。'
ver_text = u'zhuaxia (抓虾) '
help_info = u""" %(cyan)s
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
              $ cat /tmp/foo.txt
                http://music.163.com/artist?id=5345
                http://www.xiami.com/song/1772130322
                http://music.163.com/album?id=2635059
                http://www.xiami.com/album/32449

              $ zx -f /tmp/foo.txt
        """
