from django.conf.urls import patterns, url, include
import api_views

urlpatterns = patterns('',
    url(r'^task/add/', api_views.add_task, name='add_task'),
    url(r'^task/delete/', api_views.delete_task, name='delete_task'),
    url(r'^task/pause/', api_views.pause_task, name='pause_task'),
    url(r'^task/resume/', api_views.resume_task, name='resume_task'),
)