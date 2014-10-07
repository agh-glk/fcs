from django.conf.urls import patterns, url, include, handler404
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework_swagger.views import SwaggerUIView
from userena import views as userena_views
from fcs.manager import autoscale_views

import views
from accounts import views as account_views
from accounts import forms as account_forms


urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),

                       url(r'^login', userena_views.signin, {'template_name': 'login.html'},
                           name='login'),
                       url(r'^logout', userena_views.signout, {'next_page': 'index'}, name='logout'),

                       #Registration
                       url(r'^registration_complete', account_views.registration_complete,
                           name='registration_complete'),
                       url(r'^register', userena_views.signup, {'template_name': 'registration_form.html',
                                                                'success_url': 'registration_complete'},
                           name='register'),

                       #Account management
                       url(r'^accounts/password/complete/', account_views.password_change_complete,
                           name='change_password_complete'),
                       url(r'^accounts/(?P<username>\w+)/password/$', userena_views.password_change,
                           {'template_name': 'change_password.html', 'success_url': 'change_password_complete'},
                           name='change_password'),
                       url(r'^accounts/(?P<username>\w+)/edit/$', account_views.edit_user_data, name='edit_user_data'),
                       url(r'^accounts/(?P<username>\w+)/disabled/$', account_views.account_disabled,
                           name='account_disabled'),
                       url(r'^accounts/activate/(?P<activation_key>\w+)/$', userena_views.activate,
                           {'success_url': 'index'},
                           name='userena_activate'),
                       url(r'^accounts/signup/$', handler404),
                       url(r'^accounts/signin/$', handler404),
                       url(r'^accounts/signout/$', handler404),
                       url(r'^accounts/(?P<username>[\.\w-]+)/email', handler404),
                       url(r'^accounts/', include('userena.urls')),

                       #API keys & quota
                       url(r'^api_keys/', views.api_keys, name='api_keys'),
                       url(r'^show_quota/', views.show_quota, name='show_quota'),

                       #Tasks
                       url(r'^task/', include(patterns('fcs.manager.views',
                                                       url(r'^list/$', 'list_tasks', name='list_tasks'),
                                                       url(r'^add/$', 'add_task', name='add_task'),
                                                       url(r'^show/(?P<task_id>\d+)/$', 'show_task', name='show_task'),
                                                       url(r'^pause/(?P<task_id>\d+)/$', 'pause_task',
                                                           name='pause_task'),
                                                       url(r'^resume/(?P<task_id>\d+)/$', 'resume_task',
                                                           name='resume_task'),
                                                       url(r'^stop/(?P<task_id>\d+)/$', 'stop_task', name='stop_task'),
                                                       url(r'^get_data/(?P<task_id>\d+)/$', 'get_data',
                                                           name='get_data'),
                                                       url(r'^get_data/(?P<task_id>\d+)/(?P<size>\d+)/$', 'get_data',
                                                           name='get_data'),
                                                       url(r'^send_feedback/(?P<task_id>\d+)/$',
                                                           'send_feedback', name='send_feedback'),
                       ))),

                       #REST API
                       url(r'^api/', include('fcs.manager.apiurls', namespace='api')),
                       url(r'^auth/', include('oauth2_provider.urls', namespace='oauth2_provider')),

                       #Swagger REST API documentation
                       url(r'^docs/$', SwaggerUIView.as_view(), name='api_docs_ui'),
                       url(r'^docs/api-docs/$', views.api_docs_resources, name='api_docs_resources'),
                       url(r'^docs/api-docs/(?P<path>.*)/?$', views.api_docs_declaration, name='api_docs_declaration'),

                       #Autoscaling module
                       url(r'^autoscale/server/register/$', autoscale_views.register_task_server, name='register_task_server'),
                       url(r'^autoscale/server/unregister/$', autoscale_views.unregister_task_server,
                            name='unregister_task_server'),
                       url(r'^autoscale/server/stop_task/$', autoscale_views.stop_task,
                           name='stop_task_by_server'),
                       url(r'^autoscale/crawler/register/$', autoscale_views.register_crawler,
                           name='register_task_server'),
                       url(r'^autoscale/crawler/unregister/$', autoscale_views.unregister_crawler,
                           name='unregister_task_server'),

)

urlpatterns += staticfiles_urlpatterns()
