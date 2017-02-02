from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('general.urls', namespace='general')),
    url(r'^project/', include('project.urls', namespace='project')),
    url(r'^employee/', include('employee.urls', namespace='employee')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

try:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass
