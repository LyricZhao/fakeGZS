from django.conf.urls import url

from . import view

urlpatterns = [
    url(r'^$', view.all),
    url(r'^search$', view.search),
    url(r'^page$', view.page),
    url(r'^all$', view.all),
    url(r'^debug$', view.debug)
]
