from django.conf.urls import url
from . import views

app_name = 'general'
urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^login/$', views.login_form_view, name='login'),
    url(r'^registration/$', views.registration_form_view, name='registration'),
    url(r'^logout/$', views.user_logout_view, name='logout'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^confirmation/(?P<username>[a-zA-Z0-9]+)/(?P<key>[a-zA-Z0-9]+)/$',
        views.email_confirmation, name='confirmation'),
    url(r'^sender/(?P<username>[a-zA-Z0-9]+)/$',
        views.send_to, name='sender'),
]
