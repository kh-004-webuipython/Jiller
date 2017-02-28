import re
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, \
    render_to_response
from django.template import RequestContext

from employee.filters import EmployeeFilter
from project.models import Issue
from .models import Employee
from .tables import EmployeeTable
from django_tables2 import RequestConfig
from django.conf import settings


def employee_index_view(request):
    queryset = Employee.objects.all()
    # employee_filter = EmployeeFilter(request.GET, queryset=queryset)
    query_string = ''
    found_entries = None
    # if ('q' in request.GET) and request.GET['q'].strip():
    query_string = 'Ivan'  # request.GET['q']

    entry_query = get_query(query_string,
                            ['first_name', 'last_name', 'date_joined', ])

    found_entries = Employee.objects.filter(entry_query)

    table = EmployeeTable(found_entries)
    RequestConfig(request,
                  paginate={'per_page': settings.PAGINATION_PER_PAGE}).configure(
        table)
    return render(request, 'employee/list.html', {'table': table})


def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    online_status = employee.online_status()
    return render(request, 'employee/detail.html', {'employee': employee,
                                                    'online_status': online_status})


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in
            findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

# def search(request):
#     query_string = ''
#     found_entries = None
#     if ('q' in request.GET) and request.GET['q'].strip():
#         query_string = request.GET['q']
#
#         entry_query = get_query(query_string, ['title', 'body', ])
#
#         found_entries = Employee.objects.filter(entry_query).order_by('-pub_date')
#
#     return render_to_response('/search_results.html',
#                               {'query_string': query_string,
#                                'found_entries': found_entries},
#                               context_instance=RequestContext(request))
