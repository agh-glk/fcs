from django.conf.urls import patterns, url, include, handler404
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import views
from userena import views as userena_views
from accounts import views as account_views
from accounts import forms as account_forms

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),

    url(r'^login', userena_views.signin, {'template_name': 'login.html' },
        name='login'),
    url(r'^registration_complete', account_views.registration_complete, name='registration_complete'),
    url(r'^register', userena_views.signup, {'template_name': 'registration_form.html',
                                             'success_url': 'registration_complete'}, name='register'),
    url(r'^logout', userena_views.signout, {'next_page': 'index'}, name='logout'),
    url(r'^accounts/password/complete/', account_views.password_change_complete,
        name='change_password_complete'),
    url(r'^accounts/(?P<username>\w+)/password/$', userena_views.password_change,
        {'template_name': 'change_password.html', 'success_url': 'change_password_complete'}, name='change_password'),
    url(r'^accounts/(?P<username>\w+)/edit/$', account_views.edit_user_data, name='edit_user_data'),
    url(r'^accounts/(?P<username>\w+)/disabled/$', account_views.account_disabled, name='account_disabled'),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$', userena_views.activate, {'success_url': 'index'},
        name='userena_activate'),
    url(r'^accounts/signup/$', handler404),
    url(r'^accounts/signin/$', handler404),
    url(r'^accounts/signout/$', handler404),
    url(r'^accounts/(?P<username>[\.\w-]+)/email', handler404),
    url(r'^accounts/(?P<username>[\.\w-]+)/password', handler404),
    url(r'^accounts/', include('userena.urls')),

    url(r'^api_keys/', views.api_keys, name='api_keys'),
    url(r'^show_quota/', views.show_quota, name='show_quota'),

    url(r'^tasks/list/', views.list_tasks, name='list_tasks'),
    url(r'^tasks/add/', views.add_task, name='add_task'),
    url(r'^tasks/show/(?P<task_id>\d+)/$', views.show_task, name='show_task'),
    url(r'^tasks/pause/(?P<task_id>\d+)/$', views.pause_task, name='pause_task'),
    url(r'^tasks/resume/(?P<task_id>\d+)/$', views.resume_task, name='resume_task'),
    url(r'^tasks/stop/(?P<task_id>\d+)/$', views.stop_task, name='stop_task'),
    
    url(r'^api/', include('fcs.manager.apiurls', namespace='api')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    url(r'^tasks/get_data/(?P<task_id>\d+)/$', views.get_data, name='get_data')
)

urlpatterns += staticfiles_urlpatterns()
