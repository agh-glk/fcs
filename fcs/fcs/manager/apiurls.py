from django.conf.urls import patterns, url, include
import api_views

urlpatterns = patterns('',
    url(r'^task/add/', api_views.add_task, name='add_task'),
    url(r'^task/delete/(?P<task_id>\d+)/', api_views.delete_task, name='delete_task'),
    url(r'^task/pause/(?P<task_id>\d+)/', api_views.pause_task, name='pause_task'),
    url(r'^task/resume/(?P<task_id>\d+)/', api_views.resume_task, name='resume_task'),
    url(r'^task/get_data/(?P<task_id>\d+)/(?P<size>\d+)/', api_views.get_data_from_crawler, name='get_data_from_crawler'),
)