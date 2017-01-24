from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('workflow.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^employee/', include('employee.urls')),
]
