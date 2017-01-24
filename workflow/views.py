from django.http import Http404
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.views import generic
from workflow.models import Project
from django.urls import reverse_lazy


def index(request):
    return render(request, 'workflow/index.html')


def project_detail(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'workflow/project_detail.html', {'project': project})


def projtest(request):
    return render(request, 'workflow/project_navbar.html')


class ProjectDetail(DetailView):
    queryset = Project.objects.all()

    def get_object(self):
        object = super(ProjectDetail,self).get_object()
        return object


class ProjectCreate(CreateView):
    model = Project
    fields = ['title', 'end_date']
    template_name_suffix = '_create_form'


class ProjectUpdate(UpdateView):
    model = Project
    fields = ['title', 'end_date']
    template_name_suffix = '_update_form'


class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('author-list')
    template_name_suffix = '_delete_form'