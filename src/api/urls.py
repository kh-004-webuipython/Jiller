from django.conf.urls import url
from django.contrib import admin

from .views import (
    IssueCreateAPIView,
    # IssueDeleteAPIView,
    IssueDetailAPIView,
    IssueListAPIView,
    IssueUpdateAPIView,
    )

urlpatterns = [
    url(r'^$', IssueListAPIView.as_view(), name='list'),
    url(r'^create/$', IssueCreateAPIView.as_view(), name='create'),
    url(r'^(?P<pk>[\w-]+)/$', IssueDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>[\w-]+)/edit/$', IssueUpdateAPIView.as_view(), name='update'),
    # url(r'^(?P<slug>[\w-]+)/delete/$', IssueDeleteAPIView.as_view(), name='delete'),
]