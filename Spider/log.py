#-*-coding:utf-8-*-

import time

def currentTime():
    return time.asctime(time.localtime(time.time()))

class logger:

    def log(self, show, type = 0): #
        if type == 0: suffix = "\033[1;32m[ INFO,"
        if type == 1: suffix = "\033[1;41m[ERROR,"
        if type == 2: suffix = "\033[1;34m[DEBUG,"
        print suffix, currentTime(), "]\033[0m ", show


    def __init__(self):
        self.info = 0
        self.error = 1
        self.debug = 2
