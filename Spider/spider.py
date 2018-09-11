#-*-coding:utf-8-*-

import sys
sys.path.append('/Library/Python/2.7/site-packages/')

from log import logger
from parse import contentparser
from sqldb import sqldb

import time

console = logger()
parser = contentparser()
db = sqldb('./pages.db', True)

class Spider:
    def __init__(self, arg):
        self.set = set()
        self.arg = arg
        self.root_page = arg[0]
        self.target = arg[1]
        self.m_depth = arg[2]
        self.tot_counter = 0
        console.log('Root Page: ' + self.root_page)
        console.log('Target: ' + str(self.target) + ' pages')
        console.log('Max depth: ' + str(self.m_depth) + ' pages')
        console.log('Initialization done!', console.info)

    def crawl(self, url, depth):

        # time.sleep(1)
        self.tot_counter += 1
        console.log('Crawling page (Global Id = ' + str(self.tot_counter) + '): ' + url)
        console.log('Current depth: ' + str(depth))
        if url in self.set:
            console.log('Already crawled and return.', console.debug)
            console.log('')
            return
        if self.counter == self.target:
            console.log('Reaching target and return.', console.debug)
            console.log('')
            return

        # parsing
        self.set.add(url)
        content = parser.handle(url)
        if content == None: # Not in site
            console.log('Page is not in site or network is down or not allowed to crawl.', console.error)
            console.log('')
            return
        if content[0] == True: # news
            self.counter += 1
            db.save(url, content[1], content[2], content[3], content[4], content[5])
            console.log('')
        if content[0] == False: # an in-site page
            console.log('The page is an in-site page, but not news or not allowed to crawl, going deeper.', console.error)
            if depth + 1 == self.m_depth:
                console.log('Reaching max depth and return.', console.debug)
                console.log('')
                return
            console.log('')
            for next_url in content[1]:
                self.crawl(next_url, depth + 1)

    def run(self):
        console.log('Starting to grab ...')
        self.counter = 0
        self.crawl(self.root_page, 0) # root page

if __name__ == "__main__":
    console.log("Starting Spider ...", console.info)
    debug_mode = False
    if debug_mode: spider = Spider(['http://www.xinhuanet.com/world/2018-09/11/c_129950763.htm', 1, 1])
    else: spider = Spider(['http://www.xinhuanet.com', 1000, 10])
    spider.run()
    db.flush()
    console.log("Finished !", console.info)
