from django.contrib import admin

from .models import Project, Sprint, Issue, ProjectTeam, IssueComment

admin.site.register(Project)
admin.site.register(Sprint)
admin.site.register(Issue)
admin.site.register(ProjectTeam)
admin.site.register(IssueComment)

