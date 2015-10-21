from os import path 
import os
import shutil, sys
import ConfigParser
import log, util
import traceback

#the separator of tmux command output
PKG_PATH    = path.dirname(__file__)
APP_PATH    = path.join(PKG_PATH,"../")
USER_PATH   = path.join(os.getenv("HOME") , ".zhuaxia")
SAMPLE_CONF = path.join(PKG_PATH, 'conf','default.conf')
CONF_FILE   = path.join(USER_PATH, "zhuaxia.conf")


######user config####
LANG                 = 'CN'
XIAMI_PROXY_HTTP     = None
XIAMI_LOGIN_EMAIL    = None
XIAMI_LOGIN_PASSWORD = None
LOG_LVL_FILE         = 'INFO'
LOG_LVL_CONSOLE      = 'INFO'
THREAD_POOL_SIZE     = 3
DOWNLOAD_DIR         = '/tmp'
SHOW_DONE_NUMBER     = 5

#here check topx, if the value <= 0, there is no upper-bound 
DOWNLOAD_TOP_SONG    = 10

#a variable name dict for dynamic assignment
var_dict = {
        'xiami.proxy.http'        : ('XIAMI_PROXY_HTTP'    , 's'),
        'xiami.auth.email'        : ('XIAMI_LOGIN_EMAIL'   , 's'),
        'xiami.auth.password'     : ('XIAMI_LOGIN_PASSWORD', 's'),
        'download.dir'            : ('DOWNLOAD_DIR'        , 'p'),
        'log.level.file'          : ('LOG_LVL_FILE'        , 's'),
        'log.level.console'       : ('LOG_LVL_CONSOLE'     , 's'),
        'thread.pool.size'        : ('THREAD_POOL_SIZE'    , 'n'),
        'show.done.number'        : ('SHOW_DONE_NUMBER'    , 'n'),
        'download.artist.topsong' : ('DOWNLOAD_TOP_SONG'   , 'n'),
        'lang' : ('LANG'   , 's')
        }

def load_single_config(conf_parser, conf_key):
    config_warn_msg = "Cannot load config [%s], use default value: %s"
    try:
        v = conf_parser.get('settings', conf_key)
        if not v:
            raise Exception('ConfigError','invalid')
        gkey = var_dict[conf_key][0]
        ty = var_dict[conf_key][1]

        if ty == 'n':
            globals()[gkey] = int(v)
        else:
            if ty =='p':
                util.create_dir(v)
            globals()[gkey] = v
    except:
        if conf_key != 'xiami.proxy.http':
            log.warn(config_warn_msg % (conf_key, str(globals()[var_dict[conf_key][0]])))

def load_config():
    
    # if conf file doesn't exist, cp default conf there
    if not path.exists(CONF_FILE):
        init_config()

    cf = ConfigParser.ConfigParser()
    cf.read(CONF_FILE);

    for k in var_dict:
        load_single_config(cf, k)


def init_config():
    """
    create config under home
    """
    #mkdir and copy files
    os.makedirs(USER_PATH)
    shutil.copy(SAMPLE_CONF,CONF_FILE)
