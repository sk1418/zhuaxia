
**zhuaxia** README file

                                 ##             
        ##         ###           ##   ##########
        ##  ##########           ##   ##########
        ##  ########          ########   ##     
        ##  ## ## ##          ########   ##     
     ###### ## ## ##          ## ## ##   ##     
     ###### ## ## ##          ## ## ##   ##     
        ##  ## ## ##          ## ## ##   ## ##  
        ##  ## ## ##          ## ## ##   ## ##  
        ### ## ## ##          ########   ##  ## 
     ###### ## ## ##          ########   ##  ## 
     #####  ## ##  ##         ## ##      ##   ##
        ##  ## ##  ##            ## ##   ##   ##
        ##  ## ##  ##            ## ##   ##     
        ##  ## ##   ##           ######  ##     
        ## ##  ##   ##        #########  ##     
      #### ##  ##    ##       ####   ##  ##     
      ### ##   ##     #                  ##     
			 -- 抓取[虾米网]和[网易云音乐]的音乐

##Introduction / 简介

zhuaxia(抓虾) (MIT Licensed) is a little tool to batch download music resources in multiple threads from www.xiami.com and music.163.com. Due to the localization of site, the output/log messages contain Chinese. Moreover, this readme was written in Chinese as well. However all comments in codes are in English.

zhuaxia 是一个基于命令行的虾米音乐 ( www.xiami.com 以下简称[虾])和网易云音乐( music.163.com 以下简称[易]) 多线程批量下载工具


**zhuaxia** was written and tested with:
- python 2.7.6


##Dependencies / 依赖
- requests module
- mutagen module

##Features / 功能
- 自动识别解析URL. 目前支持：
	- [虾] 歌曲，专辑，精选集，用户收藏, 歌手热门
	- [易] 歌曲，专辑，歌单，歌手热门
- 下载歌手热门歌曲:数量可配置(小于30) ，默认Top10。 配置项: `download.artist.topsong`，需要艺人页面链接
- 支持混合[虾]和[易]不同音乐类型URL作为输入文件来批量下载资源 (`-f` 参数)
- 多线程(可配置线程池)解析URL
- 多线程(可配置线程池)下载歌曲
- [虾]支持以VIP账户登录下载高音质(320kbps) mp3, 并不消耗VIP的下载额度 (`-H` 选项)
- [易]支持下载高音质(320kbps) mp3 (`-H` 选项)
- 进度显示 (色彩高亮，终端宽度改变自动适应，总进度，下载线程进度...)
- mp3文件重命名, 更新mp3 meta信息，自动下载专辑封面, 专辑文本介绍(仅[虾])...等等

##Todos
- [x] [虾]对于专辑，也下载专辑介绍保存文本文件
- [x] [虾]目前只能下载一般质量的mp3,因为我个人没有vip帐号，不知道HQ的地址什么格式。但是登录以及获取cookie都已经写好并测试。只差可用的vip账户来看看格式
- [x] 下载艺人的Top10热门歌曲
- [x] 支持网易云音乐的歌曲下载，通过URL自动区分网易和虾米
- [ ] 完善Error Handling(错误处理)


##Installation / 安装

Archlinux 用户, zhuaxia可以从AUR中获取, 比如

	yaourt -S zhuaxia

其他用户:

	sudo python setup.py install

##Usage / 使用

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

##Screenshots / 运行截图

- downloading (gif animation)
![progress](https://raw.github.com/sk1418/sharedResources/master/zhuaxia/progress.gif)

- parse input file
![file view](https://raw.github.com/sk1418/sharedResources/master/zhuaxia/fileParse.png)

- parse url
![url view](https://raw.github.com/sk1418/sharedResources/master/zhuaxia/urlParse.png)

## Contributions / 贡献，感谢

感谢 [lyj](https://github.com/ly0) 提供一个限时VIP测试帐号，这给HQ资源下载部分的完成很大帮助。

		
