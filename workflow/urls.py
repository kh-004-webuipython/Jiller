from django.conf.urls import url

from . import views

app_name = 'workflow'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_form, name='login'),
    url(r'^login_proceed/$', views.login_proceed, name='login_proceed'),
    url(r'^registration/$', views.registration_form, name='registration'),
    url(r'^registration_proceed/$', views.registration_proceed, name='registration_proceed'),
]