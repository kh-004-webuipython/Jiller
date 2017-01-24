from django.contrib import admin

from workflow.models import Project, ProjectTeam, Issue, Employee, Sprint

admin.site.register(Project)
admin.site.register(ProjectTeam)
admin.site.register(Issue)
admin.site.register(Employee)
admin.site.register(Sprint)