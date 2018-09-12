#-*-coding:utf-8-*-

import os
import re
import gc
import Queue
import jieba
import sqlite3

class sqldb:
    def __init__(self, db_path):
        self.keys_score = [20, 18, 16, 14, 4, 3, 2, 1, 1, 1]
        self.keys_limit = 0.55
        self.title_ratio = 0.4
        self.keys_ratio = 0.4
        self.content_ratio = 0.2
        self.user_freq = []
        self.freq_max = 50
        self.max_brief_length = 75
        if not os.path.exists(db_path):
            raise RuntimeError('ERROR: The database file does not exist.')
        self.db = sqlite3.connect(db_path)

    def load_to_memory(self):
        cursor = self.db.cursor()

        # fetch pages
        cursor.execute('SELECT * from pages')
        self.pages = cursor.fetchall()
        print 'The size of database is', len(self.pages)
        '''
        self.key_dict = {}
        for page in pages:
            id = page[0]
            keys = page[5].split('+')
            for key in keys:
                if not self.key_dict.has_key(key):
                    self.key_dict[key] = [id]
                else:
                    self.key_dict[key].append(id)
        '''

        # fetch dict
        cursor.execute('SELECT * from dicts')
        dicts = cursor.fetchall()
        print 'The size of dictionary is', len(dicts)

        # build dict
        self.dict = {}
        for pair in dicts:
            if not self.dict.has_key(pair[0]):
                self.dict[pair[0]] = [pair[1]]
            else:
                self.dict[pair[0]].append(pair[1])

        # free temp memory
        del dicts
        gc.collect()

    def judge_id(self, id):
        if id.isdigit() == False: return False
        return 1 <= int(id) and int(id) <= len(self.pages)

    def format_url(self, title, link):
        return {'link': link, 'title': title}

    def get_url(self, id):
        return 'page?id=' + str(id)

    def get_title(self, id):
        return self.pages[id - 1][2]

    def get_brief(self, id):
        content = (self.pages[id - 1][4]).strip()
        content.encode('utf-8')
        return content[0 : min(self.max_brief_length, len(content))] + u"..."

    def get_time(self, id):
        return self.pages[id - 1][3]

    def get_content(self, id):
        return self.pages[id - 1][4].split()

    def get_keys_merged(self, id):
        keys_arr = self.pages[id - 1][5].split('+')
        return u'，'.join(keys_arr)

    def count_keys_in_page(self, keys, id):
        page = self.pages[id]
        cur = page[5].split('+')
        score = 0
        for i in range(0, len(cur)):
            if cur[i] in keys:
                score += self.keys_score[i]
        return score

    def count_sim(self, keys, id):
        title_count = 0
        content_count = 0
        keys_count = len(keys)
        rkeys_count = min(self.count_keys_in_page(keys, id), keys_count)
        title = self.pages[id][2]
        content = self.pages[id][4]
        for key in keys:
            title_count += title.count(key)
            content_count += (content.count(key) > 0)
        return (self.title_ratio * title_count + self.content_ratio * content_count + self.keys_ratio * rkeys_count) / (1.0 * keys_count)

    def pass_time_filter(self, item, time_filter):
        if time_filter == None: return True
        para_time = self.pages[item][3]
        return time_filter[0] <= para_time and para_time <= time_filter[1]

    def search_item(self, keyword, time_filter = None):
        keys = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*·（）：；【】“”]+".decode('utf8'), "".decode('utf8'), keyword)
        key_list = list(jieba.cut_for_search(keys))
        key_arr = []
        print 'Seaching for: ' + keys

        result_set = set()
        for key in key_list:
            if not self.dict.has_key(key): continue
            result_set = result_set | set(self.dict[key])
            key_arr.append(key)

        pairs = []
        keys_count = len(key_list)
        for item in result_set:
            if not self.pass_time_filter(item, time_filter): continue
            sim = self.count_sim(key_list, item - 1)
            if sim > self.keys_limit:
                pairs.append((sim, item))
        pairs.sort(reverse = True)
        result = [it[1] for it in pairs]
        return key_arr, result

    def recommand_news(self, keys):
        heap = Queue.PriorityQueue()
        for i in range(0, 5):
            heap.put((self.count_sim(keys, i), i + 1))
        for i in range(5, len(self.pages)):
            cur_count = self.count_sim(keys, i)
            heap.put(max(heap.get(), (cur_count, i + 1)))

        news = []
        for i in range(0, 5):
            news.append(heap.get()[1])
        news.reverse()
        return [self.format_url(self.get_title(it), self.get_url(it)) for it in news]

    def push_in_freq(self, key):
        for i in range(0, len(self.user_freq)):
            if self.user_freq[i][1] == key:
                self.user_freq[i] = (self.user_freq[i][0] + 1, key)
                return
        self.user_freq.append((1, key))

    def order_freq(self):
        self.user_freq.sort(reverse = True)
        if len(self.user_freq) <= self.freq_max: return
        self.user_freq = self.user_freq[0: self.freq_max]

    def visit(self, id):
        keys_arr = self.pages[id - 1][5].split('+')
        for key in keys_arr:
            self.push_in_freq(key)
        self.order_freq()

    def get_extend_list(self):
        user_appt = [it[1] for it in self.user_freq]
        return self.recommand_news(user_appt[0 : min(10, len(user_appt))])
