from django.conf.urls import url
from django.contrib import admin

from . import views

#Namespacing URL names
app_name = 'comments'

urlpatterns = [
    url(r'^(?P<id>\d+)/$', views.comment_thread, name='thread'),
    url(r'^(?P<id>[\w-]+)/delete/$', views.comment_delete, name= 'delete'),

    #TODO
    #url(r'^(?P<slug>[\w-]+)/edit/$', views.comment_update, name= 'update'),
]
