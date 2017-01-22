from django.conf.urls import url

from . import views

app_name = 'workflow'
urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^project/(?P<prkey>[0-9]+)/issue/(?P<issuekey>[0-9]+)/$', views.issue, name='issue'),
    url(r'^project/(?P<prkey>[0-9]+)/sprint/(?P<sprintkey>[0-9]+)/$', views.SprintView.as_view(), name='sprint'),
]
