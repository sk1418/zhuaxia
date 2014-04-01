# -*- coding:utf-8 -*-
import subprocess
import re
import json
import os
import config
import shutil
import random, string
import HTMLParser

def get_terminal_size(fd=1):
    """
      Returns height and width of current terminal. First tries to get
      size via termios.TIOCGWINSZ, then from environment. Defaults to 25
      lines x 80 columns if both methods fail.

      :param fd: file descriptor (default: 1=stdout)

      from: http://blog.taz.net.au/2012/04/09/getting-the-terminal-size-in-python/
  """
    try:
        import fcntl, termios, struct
        hw = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except Exception:
        try:
            hw = (os.environ['LINES'], os.environ['COLUMNS'])
        except Exception:
            hw = (25, 80)

    return hw

def random_str(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def get_line(s):
    """get a gui line with given char"""
    return str(s)*72

def create_dir(dir_name):
    """create dir if doesn't exist"""
    if dir_name:
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

def decode_html(s):
    return HTMLParser.HTMLParser().unescape(s)
