from django.conf.urls import url
from . import views

app_name = 'workflow'
urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^project/(?P<pk>\d+)/activesprint/$',
        views.ActiveSprintView.as_view(), name='active_sprint'),

    url(r'^project/(?P<pk>\d+)/sprint/create/$',
        views.SprintCreate.as_view(), name='sprint_create'),

    #url for delete sprint. Hidden until create field is_active in Sprint model
    #url(r'^project/(?P<pk>\d+)/sprint/delete/$',
    #views.SprintDelete.as_view(), name='sprint_delete'),

    url(r'^(?P<project_id>\d+)/(?P<issue_id>\d+)/(?P<slug>left|right)/$',
        views.push_issue_in_active_sprint, name='issue_push'),

    url(r'^login/$', views.login_form, name='login'),
    url(r'^registration/$', views.registration_form, name='registration'),

    url(r'^profile/$', views.profile, name='profile'),
    url(r'^project/$', views.ProjectListView.as_view(), name='projects'),
    url(r'^project/create/$', views.ProjectCreateView.as_view(),
        name='project_create'),

    url(r'^project/(?P<pk>\d+)/$', views.ProjectDetailView.as_view(),
        name='project_detail'),

    url(r'^project/update/(?P<pk>\d+)/$', views.ProjectUpdateView.as_view(),
        name='project_update'),
    url(r'^project/delete/(?P<pk>\d+)/$', views.ProjectDeleteView.as_view(),
        name='project_delete'),

    url(r'^project/(?P<project_id>[0-9]+)/backlog/$', views.backlog,
        name='backlog'),
    url(r'^project/(?P<project_id>\d+)/issue/create/$',
        views.create_issue, name='create_issue'),
    url(r'^project/(?P<project_id>[0-9]+)/issue/(?P<issue_id>[0-9]+)/$',
        views.issue, name='issue'),
    url(r'^project/(?P<project_id>\d+)/issue/(?P<issue_id>\d+)/edit/$',
        views.edit_issue, name='edit_issue'),
    url(r'^project/(?P<project_id>\d+)/team/$', views.team, name='team'),
    url(r'^project/(?P<project_id>\d+)/sprint/$',
        views.sprints_list, name='sprints_list'),
    url(r'^project/(?P<project_id>[0-9]+)/sprint/(?P<sprint_id>[0-9]+)/$',
        views.SprintView.as_view(), name='sprint'),
    url(r'^project/(?P<project_id>\d+)/issue/(?P<issue_id>\d+)/edit/$', views.edit_issue, name='edit_issue'),
    url(r'^project/(?P<project_id>\d+)/issue/create/$', views.create_issue, name='create_issue'),
    url(r'^project/(?P<project_id>\d+)/team/$', views.team, name='team'),


    url(r'^employee/$', views.employee_index_view, name='employee-index'),
    url(r'^employee/(?P<employee_id>[0-9]+)/$', views.employee_detail_view,
        name='employee-detail'),

]
