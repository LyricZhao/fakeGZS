#-*-coding:utf-8-*-

from log import logger

import os
import re
import sqlite3

console = logger()

class sqldb:
    def __init__(self, db_path, clean):
        self.dict = {}
        self.counter = 0
        self.commit_rate = 50

        # database
        if clean:
            if os.path.exists(db_path):
                os.remove(db_path)
                console.log('The previous database has been deleted.', console.info)
        if os.path.exists(db_path): rebuild = False
        else: rebuild = True

        try:
            self.db = sqlite3.connect(db_path)
        except:
            console.log('Error while opening the database: ' + db_path, console.error)
            exit(0)
        console.log('Database has been opened successfull: ' + db_path, console.info)

        if rebuild == False:
            return

        # rebuild database
        cursor = self.db.cursor()
        cursor.execute("CREATE TABLE pages (id int primary key, url text, title text, time text, content text, keys text)")
        cursor.execute("CREATE TABLE dicts (word text, id int)")

    def save(self, url, title, time, content, global_word_list, key_list):
        self.counter += 1
        self.dict[url] = self.counter
        console.log('The ID will be ' + str(self.counter), console.info)
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO pages VALUES (?, ?, ?, ?, ?, ?)", [self.counter, url, title, time, content, "+".join(key_list)])
        for word in global_word_list:
            cursor.execute("INSERT INTO dicts VALUES (?, ?)", [word, self.counter])
        console.log('The entry has been inserted.', console.info)
        if self.counter % self.commit_rate == 0:
            console.log('Commit data for database.', console.info)
            self.commit_only()

    def commit_only(self):
        self.db.commit()

    def flush(self):
        self.db.commit()
        self.db.close()
