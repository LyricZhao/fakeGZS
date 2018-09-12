#-*-coding:utf-8-*-

import re

import jieba
import jieba.analyse

from log import logger

console = logger()

class analyze:
    def handle(self, page):
        # page = title, time, content
        title = re.sub('\s', '', page[0])
        time = page[1].strip(' ')
        content = re.sub('\s','', page[2])

        if len(title) == 0:
            return None

        # cut
        title_word_list = jieba.cut_for_search(title)
        content_word_list = jieba.cut(content, cut_all = False)
        global_word_list = list(title_word_list) + list(content_word_list)
        key_list = jieba.analyse.extract_tags(content, topK = 10)

        # word filter
        word_set = set()
        for word in global_word_list:
            if not word.isspace(): word_set.add(word)
        global_word_list = []
        for word in word_set:
            filter_word = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*·（）：；【】“”]+".decode("utf8"), "".decode("utf8"), word)
            if len(filter_word):
                global_word_list.append(filter_word)

        console.log('Title: ' + title, console.debug)
        console.log('Time: ' + time, console.debug)
        console.log('Global words: ' + '/'.join(global_word_list), console.debug)
        console.log('Keys: ' + ' + '.join(key_list), console.debug)

        return [True, title, time, content, global_word_list, key_list] # ready to save in db
