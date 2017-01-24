from django.conf.urls import url

from . import views

app_name = 'employee'
urlpatterns = [
    url(r'^$', views.employee_index_view, name='index'),
    url(r'^(?P<employee_id>[0-9]+)/$', views.employee_detail_view, name='detail'),

]