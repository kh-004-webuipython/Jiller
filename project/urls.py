from django.conf.urls import url
from . import views

app_name = 'project'
urlpatterns = [
    # project
    url(r'^$', views.ProjectListView.as_view(), name='list'),

    url(r'^create/$', views.ProjectCreateView.as_view(),
        name='create'),
    url(r'^(?P<project_id>\d+)/$', views.ProjectDetailView.as_view(),
        name='detail'),
    url(r'^update/(?P<project_id>\d+)/$', views.ProjectUpdateView.as_view(),
        name='update'),
    url(r'^delete/(?P<project_id>\d+)/$', views.ProjectDeleteView.as_view(),
        name='delete'),

    # backlog
    url(r'^(?P<project_id>[0-9]+)/backlog/$', views.backlog,
        name='backlog'),

    # sprint
    url(r'^(?P<project_id>\d+)/sprint/$',
        views.sprints_list, name='sprints_list'),
    url(r'^(?P<project_id>\d+)/sprint/create/$',
        views.SprintCreate.as_view(), name='sprint_create'),
    url(r'^(?P<project_id>\d+)/sprint/(?P<sprint_id>\d+)/$',
        views.SprintView.as_view(), name='sprint_detail'),
    url(r'^(?P<project_id>\d+)/sprint/(?P<sprint_id>\d+)/activate/$',
        views.SprintStatusUpdate.as_view(), name='sprint_activate'),
    #url(r'^(?P<project_id>\d+)/sprint/(?P<sprint_id>\d+)/delete/$',
    #    views.SprintDelete.as_view(), name='sprint_delete'),

    # active_sprint
    url(r'^(?P<project_id>\d+)/sprint/active/$',
        views.ActiveSprintView.as_view(), name='sprint_active'),
    url(r'^(?P<project_id>\d+)/(?P<issue_id>\d+)/(?P<slug>left|right)/$',
        views.push_issue_in_active_sprint, name='issue_push'),

    # issue
    url(r'^(?P<project_id>\d+)/issue/create/$',
        views.issue_create_view, name='issue_create'),
    url(r'^(?P<project_id>[0-9]+)/issue/(?P<issue_id>[0-9]+)/$',
        views.issue_detail_view, name='issue_detail'),
    url(r'^(?P<project_id>\d+)/issue/(?P<issue_id>\d+)/edit/$',
        views.issue_edit_view, name='issue_edit'),

    # team
    url(r'^(?P<project_id>\d+)/team/$', views.team_view, name='team'),

    # processing AJAX
    url(r'^issue_order/$', views.issue_order, name='issue_order'),

]
