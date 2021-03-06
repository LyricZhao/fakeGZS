### fakeGZS Engine

#### Introduction

- A simple search engine in Python (Spider & Django front-end).
- Develop by LyricZ, 2017011362.
- A summer programming training project, 2018 Summer.
- Github: https://github.com/LyricZhao/fakeGZS

![](http://otxp6khet.bkt.clouddn.com/gzs/s2.jpeg)



#### Features

- [x] OOP Design Style, 1k LoC.
- [x] High-Effient Implement
- [x] Smooth User Experience
- [x] Comfortable Coding Style
- [x] Recommanding news system based on user's history
- [x] SQLite Database
- [x] Search with time filter
- [x] Mutli-keyword searching
- [x] Customizable Spider & Engine



#### Environments

- Local Compiling Environment

  - macOS 10.13.4
  - Python 2.7.15
  - Django 1.11.15
  - jieba 0.39


#### Index Page

![](http://otxp6khet.bkt.clouddn.com/gzs/s0.png)



#### How to use

- Spider

  - Just run the spider with command

    ```bash
    python spider.py
    ```

  - Note that: only *xinhuanet* can be crawled, the spider is customized to crawl the news of *xinhuanet*.

  - You can change the starting page by editing the parameters of the entrance of class Spider.

  - The parameters of Spider include [**starting page**], [**target pages**] and [**max depth**], because the spider is implemented using DFS (spider.py below).

    ```python
    spider = Spider(['http://www.xinhuanet.com', 100000, 5])
    ```

  - By default, the spider will clean the database, if you want to save data based on history, you can find the code (spider.py):

    ```python
    db = sqldb('./pages.db', True)
    ```

    - and change the database path or decide whether clean it.

  - The code is using jieba to cut the words, so if your jieba directory is not in the system path, you can add the path of jieba here (spider.py):

    ```python
    sys.path.append('/Library/Python/2.7/site-packages/')
    ```

  - Because the news of xinhuanet are divided into several parts, the spider can be customized to crawl specific parts, you can change the setting in parse.py.

    ```python
    self.allowed_part = ['politics', 'local', 'legal', 'world', 'mil', 'gangao', 'tw', 'fortune', 'auto', 'house', 'tech', 'energy']
    self.forbidden_part = ['leaders', 'renshi', 'xhll', 'video', 'overseas', 'photo', 'comments', 'caipiao', 'money', 'sports', 'foods', 'travel', 'health', 'datanews', 'gongyi', 'expo', 'abroad', 'power', 'culture', 'jiadian', 'jiaju', 'foto', 'city']
    ```

  - Also, the committing rate of the database can be set in the sqldb.py:

    ```python
    self.commit_rate = 50
    ```

- Searching Engine

  - Just run the server by command: 

    ```bash
    python manage.py runserver addr:port
    ```

  - While the server is starting, the server will load several data into memory to accelerate, so you can set the path of the database in view.py:

    ```python
    engine = sqldb_server.sqldb('../pages.db')
    ```

  - Set the number of the items per page by editing: (view.py)

    ```python
    max_arts_per_page = 10
    ```

  - The core of the engine is implemented in sqldb_server.py, here are several parameters that can be changed:

    ```python
    self.keys_score = [20, 18, 16, 14, 4, 3, 2, 1, 1, 1]
    self.keys_limit = 0.55
    self.title_ratio = 0.4
    self.keys_ratio = 0.4
    self.content_ratio = 0.2
    self.user_freq = []
    self.freq_max = 40
    self.max_brief_length = 75
    ```

    - First there is the page rating function which means that you give the function a page id and several keywords (sorted in importance), the function will return a value that shows the degree of correlation (the value is between 0 and 1).
    - *keys_score*, *title_ratio* and *content_ratio* are the parameters of the functions which I will explain later.
    - If the value of the function is greater than *self.keys_limit*, the page will be an item of the result.
    - The *self.freq_max* is the parameter of the recommanding system which means the length of the keyword history, the recommanded news will be based on the history, by changing the parameters you can also let the recommanded pages only related to current page.
    - *self.max_brief_length* is the max length of the brief content of a news that will be showed in the result page.

  - To use the time filter while searching, the method is to add the interval of the time in your input. For example, if you want to search the news about '习近平' in a time interval of 2018.01.01 to 2018.09.13, you should input '**[2018.01.01 to 2018.09.13] 习近平**'.



#### About the Design

- Spider
  - The global strategy of the spider is using DFS, which I do not think is a great method.
  - While crawling a page, the spider will first put the page into a filter to judge whether it is an in-site page or the forbidden part of the website.
  - Then the page will be throwed into an analyzer to analyze the content of page.
    - If the page is a news, analyzer will return the analyzed data to the spider.
    - If not, analyzer will return the urls which the page related to, and the spider will continue to crawl the urls.
  - When the spider receive data of a news page, the spider will call class sqldb to save the data into a cache, when the number of the pending data is reaching a value, the sqldb will cut the words of the title and content and then commit to the database file.
  - The database has two tables including the content table and the dictionary table.
    - The connent table will record the detailed data of the pages.
    - The dictionary table will record entries like (keyword, page-id), which is used for inverted indexing algorithm.
  - An interesting thing is that shuffling the urls will accelerate the process.
  - The *pages.db* is a result of 2 hours' running of the spider, all the parts I specified are crawled.
    - The number of the pages is about 5k.
    - The number of entries in the dictionary is about 1500k.

![](http://otxp6khet.bkt.clouddn.com/gzs/s1.png)



- Engine

  - After user inputs a sentence, the engine will call jieba to cut the sentence to words, and each word will look up in the dictionary and get the set of entries. Finally these sets will be merged into one, then go through the filter function and return.

  - The filter function is used to describe the simarlity of a news and the keywords given. The function is defined like this:

    $f(page, keywords) = ((\Sigma_{key}t(page, key) * title\_ratio) + (\Sigma_{key}c(page, key) * content\_ratio)+(\Sigma_{key}k(page, key) * key\_ratio ))/key\_tot$

    $t(page, key)=page.title.count(key)$

    $c(page,key)=[page.content.count(key)>1]$

    $k(page, key)= if(key\ in\ page.key)\ importance(key)\ else\ 0$

    - And finally if the value is greater than the value you set, the result will be showed.
    - The function is the one that I tried without thinking ... but the final effect is pretty good.
    - $importance(key)$ is exactly the *key_score* array in sqldb_server.py.
    - I found that sometimes the information I wanna get is in the title, but also sometimes in the content, and even the keyword appearing in the content doesn't mean that it is very related, so I also let the similarity of the keywords themselves count for a part.
    - Extracting the keywords is using the jieba, **td-idf** algorithm.

  - For the recommanding system:

    -  I use a queue to maintain the keysword that the user recently or frequently visits, when a new word is put in the queue, if the size of queue is reaching max size, the new word will replace the lowest level word.
    - If a user visits a news page, the system will call the similarity function to find the highest five pages and recommand to the user.
    - I tested the system several times and always got a really good result.

    ![](http://otxp6khet.bkt.clouddn.com/gzs/s4.png)

  - For the CSS file and JavaScript, I haven't learned about this, all are copied from the website of apple.com...


#### About the code

- Spider
  - Spider/analyze.py: cut the content and analyze, but not processing format problem
  - Spider/log.py: logging system of spider
  - Spider/parse.py: parse the content from a page
  - Spider/spider.py: program entrance and core
- Engine
  - sqldb_server.py: searching core
  - view.py: handling user's request and return results



#### Performance

- The searching algorithm is $O(nlogn)$, where $n$ is the amount of the result pages.

- And I did several simple test:

  - macOS 10.13.6
  - Intel Core i7, 2.8 GHz

  | Keyword | Time used         | Entries found |
  | ------- | ----------------- | ------------- |
  | 朝鲜    | 0.000443935394287 | 12            |
  | 习近平  | 0.00294089317322  | 69            |
  | 经济    | 0.0130569934845   | 137           |
  | 中国    | 0.0205409526825   | 336           |

  ![](http://otxp6khet.bkt.clouddn.com/gzs/s3.png)

- Not so fast...

- In fact, I had already wrote an entire search engine before with Gu Yuxian, spider in Python, core in C++, 5k LoC, and that one is call GZ Searcher, that why I call this one fakeGZS.



#### Thanks for reading