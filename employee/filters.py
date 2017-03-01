import django_filters
from django.contrib.auth.models import Group
from django import forms
from django.forms.widgets import Input

from employee.models import Employee


class SearchInput(forms.widgets.Input):
   input_type = 'search'


class EmployeeFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(widget=SearchInput(),lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    year_joined = django_filters.NumberFilter(name='date_joined',
                                              lookup_expr='year')
    groups = django_filters.ModelMultipleChoiceFilter(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'last_activity',
                  'date_joined', 'groups']

    # @property
    # def qs(self):
    #     parent = super(EmployeeFilter, self).qs
    #     # search = get_query(self.request.search)
    #     search = parent.filter(first_name = self.request.search)
    #
    #     return search
    # #     # return parent.filter(is_published=True) \
    # #     #    | parent.filter(author=self.request.user)
