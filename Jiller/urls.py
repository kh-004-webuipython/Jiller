from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('general.urls', namespace='general')),
    url(r'^project/', include('project.urls', namespace='project')),
    url(r'^employee/', include('employee.urls', namespace='employee')),
    url(r'^accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

try:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass


handler400 = 'general.views.handler400'
handler404 = 'general.views.handler404'
handler403 = 'general.views.handler403'
handler500 = 'general.views.handler500'
