from django.conf.urls import url

from . import views

app_name = 'workflow'
urlpatterns = [

    url(r'^$', views.index, name='index'),
]
