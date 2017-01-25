from django.conf.urls import url
from . import views

app_name = 'workflow'
urlpatterns = [
    url(r'^project/(?P<project_id>\w+)/issue/create/$', views.create_issue, name='create_issue'),
    url(r'^project/(?P<project_id>\w+)/issue/(?P<issue_id>\w+)/edit/$', views.edit_issue, name='edit_issue'),
    url(r'^project/(?P<project_id>\w+)/team/$', views.team, name='team'),

    url(r'^$', views.index, name='index'),

    url(r'^login/$', views.login_form, name='login'),
    url(r'^registration/$', views.registration_form, name='registration'),

    url(r'^profile/$', views.profile, name='profile'),
    url(r'^project/$', views.ProjectListView.as_view(), name='projects'),

    # /project/create/
    url(r'^project/create/$', views.ProjectCreate.as_view(),
        name='project_create'),

    # /project/[pr_id]/
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(),
        name='project_detail'),

    # /project/update/[pr_id]/
    url(r'^project/update/(?P<pk>\d+)/$', views.ProjectUpdate.as_view(),
        name='project_update'),

    # /project/delete/[pr_id]/
    url(r'^project/delete/(?P<pk>\d+)/$', views.ProjectDelete.as_view(),
        name='project_delete'),

    url(r'^project/(?P<pr_id>[0-9]+)/backlog/$', views.backlog,
        name='backlog'),
    url(r'^project/(?P<project_id>\w+)/issue/create/$',
        views.create_issue, name='create_issue'),
    url(r'^project/(?P<project_id>[0-9]+)/issue/(?P<issue_id>[0-9]+)/$',
        views.issue, name='issue'),
    url(r'^project/(?P<project_id>\w+)/issue/(?P<issue_id>\w+)/edit/$',
        views.edit_issue, name='edit_issue'),
    url(r'^project/(?P<project_id>\w+)/team/$', views.team, name='team'),
    url(r'^project/(?P<pr_id>[0-9]+)/sprint/$',
        views.sprints_list, name='sprints_list'),
    url(r'^project/(?P<project_id>[0-9]+)/sprint/(?P<sprint_id>[0-9]+)/$',
        views.SprintView.as_view(), name='sprint'),

    url(r'^employee/$', views.employee_index_view, name='employee-index'),
    url(r'^employee/(?P<employee_id>[0-9]+)/$', views.employee_detail_view,
        name='employee-detail'),

]
