**zhuaxia** README file
		
<p><b><font color="red">针对[虾]更改链接以及API的修复</font></b></p>

因为[虾]变更了它的api链接以及处理方式，原zhuaxia(`version 2.1.x`)的[虾]下载部分无法正常工作。在`v2.2.0`版本做了相应的修复。目前修复的[虾]的功能有：

- [虾]曲下载
- [虾]辑下载，包括封面
- [虾]选集下载
- [虾]歌手热门下载 (max Top20)

**Todos / 待完成**

- [x] [虾]修复xiami更改api导致xiami部分功能无法正常使用的问题
- [ ] [虾]下载专辑时，下载专辑介绍保存本地
- [ ] [虾]修复用户收藏的下载

xiami还屏蔽海外ip的访问，这给修复和测试又带来难度。我会尽快解决剩下的问题。到目前为止，网易部分下载还正常。(从虾米屏蔽海外ip我就用网易了)


####Table of Contents

- [Introduction/简介](#introduction--%E7%AE%80%E4%BB%8B)
- [Dependencies/依赖](#dependencies--%E4%BE%9D%E8%B5%96)
- [Features/功能](#features--%E5%8A%9F%E8%83%BD)
	- [Todos](#todos--%E5%BE%85%E5%AE%8C%E6%88%90)
- [Installation/安装](#installation--%E5%AE%89%E8%A3%85)
- [Usage/使用](#usage--%E4%BD%BF%E7%94%A8)
	- [海外IP使用xiami代理支持](#%E6%B5%B7%E5%A4%96ip%E4%B8%8B%E8%BD%BDxiami%E8%B5%84%E6%BA%90)
- [Screenshots](#screenshots--%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE)
- [Contributions](#contributions)


## Introduction / 简介

zhuaxia(抓虾) (MIT Licensed) is a little tool to batch download music resources in multiple threads from www.xiami.com and music.163.com. Due to the localization of site, the output/log messages contain Chinese. Moreover, this readme was written in Chinese as well. However all comments in codes are in English.

zhuaxia 是一个基于命令行的虾米音乐 ( www.xiami.com 以下简称[虾])和网易云音乐( music.163.com 以下简称[易]) 多线程批量下载工具


**zhuaxia** was written and tested with:
- python 2.7.6


##Dependencies / 依赖

- requests module
- mutagen module
- beautifulsoup4 module

##Features / 功能

- 自动识别解析URL. 目前支持：
	- [虾] 歌曲，专辑，精选集，用户收藏[todo], 歌手热门
	- [易] 歌曲，专辑，歌单，歌手热门
- 下载歌手热门歌曲:数量可配置([虾]max:20) ，默认Top10。 配置项: `download.artist.topsong`，需要艺人页面链接
- 支持包含音乐资源URL的文件作为输入进行批量下载. URL可以是[虾]和[易]混合, 可以不同音乐类型混合 (`-f` 参数)
- 当以文件作为输入批量下载时, 多线程(可配置线程池)解析URL
- 多线程(可配置线程池)下载歌曲
- [虾]支持以VIP账户登录下载高音质(320kbps) mp3, 并不消耗VIP的下载额度 (`-H` 选项)
- [易]支持下载高音质(320kbps) mp3 (`-H` 选项)
- 进度显示 (色彩高亮，终端宽度改变自动适应，总进度，下载线程进度...)
- mp3文件重命名, 更新mp3 meta信息，自动下载专辑封面, 专辑文本介绍(仅[虾])...等等
- ***[虾]配置项`xiami.proxy.http=ip:port` 来设置国内的代理服务进行xiami连接的解析。详见："Usage -> 海外IP下载xiami资源" 一节



##Installation / 安装

Archlinux 用户, zhuaxia可以从AUR中获取, 比如

	yaourt -S zhuaxia

其他用户:

	sudo python setup.py install

## Usage / 使用

- 配置文件， 第一次运行`zx`后， 在`$HOME/.zhuaxia/` 会有配置文件 `zhuaxia.conf` 配置参数有中文说明

- 使用：

			
		[CONFIG FILE:]   
			$HOME/.zhuaxia/zhuaxia.conf

		[OPTION] 
			-H    
				:首选HQ质量(320kbps), 

				> 虾米音乐 <
					- 配置文件中需给出正确登录信箱和密码, 登录用户需拥有VIP身份
					- 用户需在xiami vip设置页面设置默认高音质
					- 此选项对不满足上两项情况无效，仍下载128kbps资源
				> 网易音乐 <
					无需特殊要求,直接下载高音质资源

		[USAGE] 

			zx [OPTION] <URL>
				: 下载指定URL资源, 自动识别链接, 支持
					- [虾] 歌曲，专辑，精选集，用户收藏,艺人TopN
					- [易] 歌曲，专辑，歌单，艺人TopN
				例子： 
				  zx "http://www.xiami.com/space/lib-song/u/25531126"
				  zx "http://music.163.com/song?id=27552647"

			zx [OPTION] -f <file> 
				: 多个URL在一个文件中，每个URL一行。 URLs可以是混合[虾]和[易]的不同类型音乐资源。例子：
				  $ cat /tmp/foo.txt
					http://music.163.com/artist?id=5345
					http://www.xiami.com/song/1772130322
					http://music.163.com/album?id=2635059
					http://www.xiami.com/album/32449

				  $ zx -f /tmp/foo.txt

			zx -h ：显示帮助

			zx -v ：显示版本信息


- 例子

			zx -H -f "tmp/in.txt"
			zx  "http://music.163.com/song?id=123456"
			zx -H "http://www.xiami.com/album/51786"

### 海外IP下载xiami资源

xiami.com屏蔽了海外ip的http请求。在配置文件中添加（如果不存在的话）`xiami.proxy.http=ip:port` 可以让zhuaxia通过代理来解析xiami资源。
例如：

	xiami.proxy.http=127.0.0.1:8080

这里`ip:port`构成的http代理是国内的代理服务器。 如果你的机器已经是国内的ip，请注释或删除这个选项。获取国内代理的简单方法：到http://proxy-list.org/ 搜索China的代理就好。

## Screenshots / 屏幕截图

- downloading (gif animation)
![progress](https://raw.github.com/sk1418/sharedResources/master/zhuaxia/progress.gif)

- parse input file
![file view](https://raw.github.com/sk1418/sharedResources/master/zhuaxia/fileParse.gif)

- parse url
![url view](https://raw.github.com/sk1418/sharedResources/master/zhuaxia/urlParse.png)

## Contributions

感谢 [lyj](https://github.com/ly0) 提供一个限时VIP测试帐号，这给HQ资源下载部分的完成很大帮助。
