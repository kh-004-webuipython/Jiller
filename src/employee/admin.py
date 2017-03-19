from django.contrib import admin

from .models import IssueLog, Employee

admin.site.register(Employee)
admin.site.register(IssueLog)
