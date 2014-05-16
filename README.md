
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
                     -- 抓取 xiami.com 音乐

##Introduction / 简介

zhuaxia(抓虾) (MIT Licensed) is a little tool to batch download music resources in multiple threads from www.xiami.com. Due to the site is a Chinese website, the output/log messages contains Chinese. Also this readme would be written in Chinese as well. All comments in codes are in English.

zhuaxia 是一个基于命令行的虾米(xiami.com)音乐多线程批量下载工具

**zhuaxia** was written and tested with:
- python 2.7.6

##Dependencies / 依赖
- requests module
- mutagen module

##Features / 功能
- 自动解析URL (目前支持：歌曲，专辑， 用户收藏，精选集)
- 支持混合类型URL作为输入文件来批量下载资源 (`-f` 参数)
- 多线程(可配置线程池)解析URL
- 多线程(可配置线程池)下载歌曲
- 支持以VIP账户登录下载高音质(320kbps) mp3, 并不消耗VIP的下载额度
- 进度显示 (色彩高亮，终端宽度改变自动适应，总进度，下载线程进度...)
- 更新mp3 meta信息，自动下载封面...等等

##Todos
- [x] 对于专辑，也下载专辑介绍保存文本文件
- [x] 目前只能下载一般质量的mp3,因为我个人没有vip帐号，不知道HQ的地址什么格式。但是登录以及获取cookie都已经写好并测试。只差可用的vip账户来看看格式
- [ ] 对于用户收藏，每次下载做增量下载，即不下载曾经下载过的歌曲，当然有选项开关.这样更便于随时把收藏的歌拉到本地
- [ ] 保存下载/解析历史，对于重复的下载可以更快获得下载地址
- [ ] 完善Error Handling(错误处理)

##Installation / 安装

Archlinux 用户, zhuaxia可以从AUR中获取, 比如

	yaourt -S zhuaxia

其他用户:

	sudo python setup.py install

##Usage / 使用

- 配置文件， 第一次运行`zx`后， 在`$HOME/.zhuaxia/` 会有配置文件 `zhuaxia.conf` 配置参数有中文说明

- 使用：

		[CONFIG FILE] 
			$HOME/.zhuaxia/zhuaxia.conf

		[OPTION] 
			-H
				首选HQ质量(320kbps), 
					- 配置文件中需给出正确登录信箱和密码
					- 登录用户需拥有VIP身份
					- 用户需在xiami vip设置页面设置默认高音质
					- 此选项对不满足上3点情况无效，仍下载128kbps资源

		[USAGE] 

			zx [OPTION] <URL>
				: 下载指定URL资源 (歌曲，专辑，精选集，用户收藏)
				例子： 
				  zx "http://www.xiami.com/space/lib-song/u/25531126"

			zx [OPTION] -f <file> 
				: 多个URL在一个文件中，每个URL一行。 URLs可以是不同资源类型。例子：
				  $ zx -f /tmp/foo.txt

				  $ cat /tmp/foo.txt
				  http://www.xiami.com/album/51786
				  http://www.xiami.com/space/lib-song/u/25531126

			zx -h ：显示帮助

			zx -v ：显示版本信息

- 例子

			zx -H -f "tmp/in.txt"
			zx  "http://www.xiami.com/song/123456"
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

		
