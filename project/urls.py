from django.conf.urls import url
from . import views

app_name = 'project'
urlpatterns = [
    # project
    url(r'^$', views.ProjectListView.as_view(), name='list'),

    url(r'^create/$', views.ProjectCreateView.as_view(),
        name='create'),
    url(r'^(?P<pk>\d+)/$', views.ProjectDetailView.as_view(),
        name='detail'),
    url(r'^update/(?P<pk>\d+)/$', views.ProjectUpdateView.as_view(),
        name='update'),
    url(r'^delete/(?P<pk>\d+)/$', views.ProjectDeleteView.as_view(),
        name='delete'),

    # backlog
    url(r'^(?P<project_id>[0-9]+)/backlog/$', views.backlog,
        name='backlog'),

    # sprint
    url(r'^(?P<project_id>\d+)/sprint/$',
        views.sprints_list, name='sprints_list'),
    url(r'^(?P<project_id>[0-9]+)/sprint/(?P<sprint_id>[0-9]+)/$',
        views.SprintView.as_view(), name='sprint_detail'),
    url(r'^(?P<pk>\d+)/sprint/create/$',
        views.SprintCreate.as_view(), name='sprint_create'),
    # url for delete sprint. Hidden until create field is_active in Sprint model
    # url(r'^project/(?P<pk>\d+)/sprint/delete/$',
    # views.SprintDelete.as_view(), name='sprint_delete'),

    # active_sprint
    url(r'^(?P<pk>\d+)/activesprint/$',
        views.ActiveSprintView.as_view(), name='active_sprint'),
    url(r'^(?P<project_id>\d+)/(?P<issue_id>\d+)/(?P<slug>left|right)/$',
        views.push_issue_in_active_sprint, name='issue_push'),

    # issue
    url(r'^(?P<project_id>\d+)/issue/create/$',
        views.issue_create_view, name='issue_create'),
    url(r'^(?P<project_id>[0-9]+)/issue/(?P<issue_id>[0-9]+)/$',
        views.issue, name='issue_detail'),
    url(r'^(?P<project_id>\d+)/issue/(?P<issue_id>\d+)/edit/$',
        views.issue_edit_view, name='issue_edit'),

    # team
    url(r'^(?P<project_id>\d+)/team/$', views.team_view, name='team'),


]
