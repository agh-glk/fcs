from django.conf.urls import patterns, url, include
import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login_user, name='login'),
    url(r'^logout',views.logout_user, name='logout'),
    url(r'^change_password', views.change_password, name='change_password'),
    url(r'^accounts/', include('registration.backends.default.urls')),
)