#-*-coding:utf-8-*-

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response

from . import sqldb_server

import re
import time

print 'Starting searching engine core ...'
engine = sqldb_server.sqldb('../pages.db')
engine.load_to_memory()
print 'Done!'

max_arts_per_page = 10

def index(request):
    return render_to_response('index.html')

def debug(request):
    return render_to_response('result.html')
    return HttpResponse('How did you find here?')

def highlight(content, keys):
    for key in keys:
        if content.count(key):
            content = (u'<strong>' + key + u'</strong>').join(content.split(key))
    return content

def get_item_list(ids, l, r, keys):
    if len(ids) == 0: return None
    item_list = []
    for i in range(l, r):
        id = ids[i]
        item = {'url': u'page?id=' + str(id), 'title': engine.get_title(id), 'date': engine.get_time(id), 'brief': highlight(engine.get_brief(id), keys)}
        item_list.append(item)
    return item_list

def search(request):
    t0 = time.time()
    request.encoding = 'utf-8'
    if 'text' in request.GET:
        pass
    else: return HttpResponse('ERROR 404')

    text = request.GET['text']
    if len(text) == 0:
        return render_to_response('index.html')

    page_no = 1
    if 'pager' in request.GET:
        page_str = str(request.GET['pager'])
        if not page_str.isdigit():
            return HttpResponse('ERROR 404')
        page_no = int(request.GET['pager'])

    original_text = text
    matches = re.match('\[\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}\]', text)
    time_filter = None
    if matches:
        time_filter = (text[1 : 11], text[15 : 25])
        text = text[26 : len(text)]

    strongs, ids = engine.search_item(text, time_filter)
    strongs = list(strongs)
    total_pages = len(ids) / max_arts_per_page
    cur_arts_num = max_arts_per_page
    if len(ids) % max_arts_per_page > 0:
        total_pages += 1

    if page_no > total_pages and len(ids) != 0:
        return HttpResponse('ERROR 404')
    if page_no == total_pages:
        if len(ids) % max_arts_per_page > 0:
            cur_arts_num = len(ids) % max_arts_per_page
        else:
            cur_arts_num = max_arts_per_page

    rangeL = (page_no - 1) * max_arts_per_page
    rangeR = rangeL + cur_arts_num

    mapped = {}
    mapped['page_title'] = text + u"_fakeGZS搜索"
    mapped['user_input'] = original_text
    mapped['result_count'] = str(len(ids))
    mapped['item_list'] = get_item_list(ids, rangeL, rangeR, strongs)
    mapped['current_page'] = str(page_no)
    mapped['total_pages'] = str(total_pages)
    mapped['timer'] = str(time.time() - t0)

    return render(request, 'result.html', mapped)

def page(request):
    request.encoding = 'utf-8'
    if 'id' in request.GET:
        pass
    else: return HttpResponse('ERROR 404')
    if not engine.judge_id(str(request.GET['id'])):
        return HttpResponse('ERROR 404')

    id = int(request.GET['id'])
    engine.visit(id)
    mapped = {}
    mapped['news_title'] = engine.get_title(id)
    mapped['keywords'] = engine.get_keys_merged(id)
    mapped['mod_date'] = engine.get_time(id)
    mapped['main_content'] = engine.get_content(id)
    mapped['extend_list'] = engine.get_extend_list()

    return render(request, 'page.html', mapped)
