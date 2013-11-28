from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register', views.register, name='register'),
    url(r'^reg_scs', views.registration_successful),
    url(r'^login', views.login_user, name='login'),
    url(r'^logout',views.logout_user, name='logout'),

)