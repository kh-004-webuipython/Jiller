from django.contrib import admin
from django.conf.urls import url

from .models import Project, Sprint, Issue, ProjectTeam, IssueLog, Employee
# Register your models here.

admin.site.register(Project)
admin.site.register(Sprint)
admin.site.register(Employee)
admin.site.register(Issue)
admin.site.register(ProjectTeam)