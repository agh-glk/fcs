from django.conf.urls import patterns, url, include
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login_user, name='login'),
    url(r'^logout',views.logout_user, name='logout'),
    url(r'^change_password', views.change_password, name='change_password'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^tasks/list/', views.list_tasks, name='list_tasks'),
    url(r'^tasks/add/', views.add_task, name='add_task'),
    url(r'^tasks/show/(?P<task_id>\d+)/$', views.show_task, name='show_task'),
)