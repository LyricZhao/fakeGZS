#-*-coding:utf-8-*-

from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response

from . import sqldb_server

print 'Starting searching engine core ...'
engine = sqldb_server.sqldb('../pages.db')
engine.load_to_memory()
print 'Done!'

def index(request):
    return render_to_response('search.html')

def search(request):
    request.encoding = 'utf-8'
    if 'text' in request.GET:
        print request.GET['text']
    else: return HttpResponse('ERROR #1')

    text = request.GET['text']
    if len(text) == 0:
        return render_to_response('search.html')
    ids = engine.search_item(text)
    # print ids

    return HttpResponse('ERROR #2')

def page(request):
    request.encoding = 'utf-8'
    if 'id' in request.GET:
        pass
    else: return HttpResponse('ERROR #1')
    if not engine.judge_id(str(request.GET['id'])):
        return HttpResponse('Error #2')

    id = int(request.GET['id'])
    engine.visit(id)
    mapped = {}
    mapped['news_title'] = engine.get_title(id)
    mapped['keywords'] = engine.get_keys_merged(id)
    mapped['mod_date'] = engine.get_time(id)
    mapped['main_content'] = engine.get_content(id)
    mapped['extend_list'] = engine.get_extend_list()

    return render(request, 'page.html', mapped)
