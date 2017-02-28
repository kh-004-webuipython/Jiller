import django_filters
from django.contrib.auth.models import Group
from django import forms

from employee.models import Employee



class EmployeeFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains')
    year_joined = django_filters.NumberFilter(name='date_joined',
                                              lookup_expr='year')
    groups = django_filters.ModelMultipleChoiceFilter(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'last_activity',
                  'date_joined','groups']
