from django.conf.urls import patterns, url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    
    url(r'^login', views.login_user, name='login'),
    url(r'^logout',views.logout_user, name='logout'),
    url(r'^change_password', views.change_password, name='change_password'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^api_keys/', views.api_keys, name='api_keys'),
    
    url(r'^tasks/list/', views.list_tasks, name='list_tasks'),
    url(r'^tasks/add/',views.add_task, name='add_task'),
    url(r'^tasks/show/(?P<task_id>\d+)/$', views.show_task, name='show_task'),
    
    url(r'^api/', include('fcs.manager.apiurls', namespace='api')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

urlpatterns += staticfiles_urlpatterns()
