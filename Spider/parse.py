#-*-coding:utf-8-*-

from log import logger
from analyze import analyze

import re
import urllib
import urllib2

from urllib2 import Request
from HTMLParser import HTMLParser

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

console = logger()
analyzer = analyze()

class my_htmlparser(HTMLParser):
    def __init__(self, i_my_url):
        HTMLParser.__init__(self)
        self.para = False
        self.my_url = i_my_url
        self.title = ''; self.pro_title = False
        self.mtime = ''; self.pro_mtime = False
        self.mtext = ''; self.pro_mtext = 0
        self.next_urls = []

    def match_http(self, url):
        return re.match('https?://[^\s]*', url) != None

    def url_process(self, url):
        if self.match_http(url):
            return url
        return self.my_url + "/" + url

    def judge_tag(self, tag, attrs, m_tag, m_var, m_val, no_val = False):
        if tag == m_tag:
            if len(attrs) == 0: pass
            else:
                for (var, val) in attrs:
                    if var == m_var and (val == m_val or no_val):
                        if no_val: return val
                        return True
        return False

    def handle_starttag(self, tag, attrs):
        next_url = self.judge_tag(tag, attrs, 'a', 'href', '', True)
        if next_url != False:
            self.next_urls.append(self.url_process(next_url))

        if self.judge_tag(tag, attrs, 'div', 'class', 'h-title'): self.pro_title = True
        if self.judge_tag(tag, attrs, 'span', 'class', 'h-time'): self.pro_mtime = True
        if self.judge_tag(tag, attrs, 'div', 'id', 'p-detail'): self.pro_mtext = 1

        if tag == 'p': self.para = True
        if tag == 'div' and self.pro_mtext > 0: self.pro_mtext += 1

    def handle_data(self, data):
        if self.pro_title:
            self.title = data
            self.pro_title = False
        if self.pro_mtime:
            self.mtime = data
            self.pro_mtime = False

        if self.pro_mtext > 0 and self.para == True:
            self.mtext += data + '\n'

    def handle_endtag(self, tag):
        if tag == 'p': self.para = False
        if tag == 'div' and self.pro_mtext > 0:
            self.pro_mtext -= 1
            if self.pro_mtext == 1: # last div tag
                self.pro_mtext = 0

class contentparser:
    def __init__(self):
        self.allowed_part = ['politics', 'local', 'legal', 'world', 'mil', 'gangao', 'tw', \
                             'fortune', 'auto', 'house', 'tech', 'energy']
        self.forbidden_part = ['leaders', 'renshi', 'xhll', 'video', 'overseas', 'photo', \
                          'comments', 'caipiao', 'money', 'sports', 'foods', \
                          'travel', 'health', 'datanews', 'gongyi', 'expo', 'abroad', \
                          'power', 'culture', 'jiadian', 'jiaju', 'foto', 'city']

    def not_in_site(self, url):
        return re.match('https?://www\.xinhuanet\.com[^\s]*', url) == None

    def not_news_format(self, url):
        matches = re.match('https?://www\.xinhuanet\.com/\w+/\d{4}-\d{2}/\d{2}/[a-zA-Z]_\d+\.html?', url)
        if matches == None: return True
        for part in self.forbidden_part:
            if part in url: return True
        for part in self.allowed_part:
            if part in url: return False
        return True

    def handle(self, url):
        # matches site reg
        if self.not_in_site(url):
            return None

        # try to connect
        try:
            response = urllib.urlopen(url)
        except:
            console.log('Error while getting page data.', console.error)
            return None
        else:
            console.log('Page downloaded.', console.debug)

        # extract data
        try:
            page_data = response.read().decode('utf-8')
        except UnicodeDecodeError, error:
            console.log('Unicode decoding error: ' + error.reason, console.error)
            return None
        parser = my_htmlparser(url)
        parser.feed(page_data)
        parser.close()

        # not news
        if self.not_news_format(url):
            return [False, parser.next_urls]

        # print for debug
        '''
        console.log('Title: ' + parser.title, console.debug)
        console.log('Time: ' + parser.mtime, console.debug)
        console.log('Content: ' + parser.mtext, console.debug)
        '''

        # analyzer
        return analyzer.handle([parser.title, parser.mtime, parser.mtext])
