# -*- coding:utf-8 -*-
import subprocess
import re
import json
import os
import config
import shutil
import random, string
import HTMLParser




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
