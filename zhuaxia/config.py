from os import path 
import os
import shutil, sys
import ConfigParser
import log


VERSION     = '1.0.0'                #software version
#the separator of tmux command output
PKG_PATH    = path.dirname(__file__)
APP_PATH    = path.join(PKG_PATH,"../")
USER_PATH   = path.join(os.getenv("HOME") , ".zhuaxia")
SAMPLE_CONF = path.join(PKG_PATH, 'conf','default.conf')
CONF_FILE   = path.join(USER_PATH, "zhuaxia.conf")

######user config####
XIAMI_LOGIN_EMAIL=''
XIAMI_LOGIN_PASSWORD=''
LOG_LVL_FILE = 'INFO'
LOG_LVL_CONSOLE = 'INFO'
THREAD_POOL_SIZE = 3
DOWNLOAD_DIR='/tmp'

def load_config():

    config_warn_msg = "Cannot load %s config, use default: %s"

    global LOG_LVL_FILE, LOG_LVL_CONSOLE, THREAD_POOL_SIZE, \
            XIAMI_LOGIN_EMAIL, XIAMI_LOGIN_PASSWORD
    """
        load config from config file 
        return True if sucessful, otherwise False
    """
    cf = ConfigParser.ConfigParser()
    
    # if conf file doesn't exist, cp default conf there
    if not path.exists(CONF_FILE):
        init_config()

    cf.read(CONF_FILE);

    #load options here
    try:
        download_dir = cf.get('settings','download.dir')
        lvl_file = cf.get('settings','log.level.file')
        lvl_console = cf.get('settings','log.level.console')
        pool_size = cf.getint('settings', 'thread.pool.size')
        XIAMI_LOGIN_EMAIL = cf.get('settings','xiami.auth.email')
        XIAMI_LOGIN_PASSWORD = cf.get('settings','xiami.auth.password')

        #TODO
        #read download dir, if not exists, create the dir

        if not pool_size: 
            log.print_warn(config_warn_msg % 'thread.pool.size',THREAD_POOL_SIZE)
        else:
            THREAD_POOL_SIZE = pool_size

        if lvl_file.lower() not in log.LVL_DICT.keys():
            log.print_warn(config_warn_msg % 'log.level.file',LOG_LVL_FILE)
        else:
            LOG_LVL_FILE = lvl_file

        if lvl_console.lower() not in log.LVL_DICT.keys():
            log.print_warn( config_warn_msg % 'log.level.console',LOG_LVL_CONSOLE)
        else:
            LOG_LVL_CONSOLE = lvl_console
    except:

        log.warn('Error occured when loading config, using all default values')
        return False
    return True;

def init_config():
    """
    create config under home
    """
    #mkdir and copy files
    os.makedirs(USER_PATH)
    shutil.copy(SAMPLE_CONF,CONF_FILE)
