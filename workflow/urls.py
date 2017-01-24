from django.conf.urls import url

from . import views

from workflow.views import ProjectListView

app_name = 'workflow'
urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^$profile/$', views.profile, name='profile'),
    url(r'^$project/$', ProjectListView.as_view(), name='projects'),

]