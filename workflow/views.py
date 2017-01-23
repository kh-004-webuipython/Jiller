from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Issue, Sprint, Project

# Create your views here.


def index(request):
    return render(request, 'workflow/index.html')


def issue(request, prkey, issuekey):
    current_issue = get_object_or_404(Issue, pk=issuekey, project=prkey)
    return render(request, 'workflow/issue.html', {
        'issue': current_issue,
    })


def profile(request):
    current_user = request.user
    return render(request, 'workflow/profile.html', {
        'user': current_user
    })

class ProjectListView(ListView):
    model = Project
    paginate_by = 10
    template_name = 'workflow/projects.html'


class SprintView(DetailView):
    model = Sprint
    template_name = 'workflow/sprint.html'
    query_pk_and_slug = True
    pk_url_kwarg = 'sprintkey'
    slug_field = 'project'
    slug_url_kwarg = 'prkey'

    def get_context_data(self, **kwargs):
        context = super(SprintView, self).get_context_data(**kwargs)
        context['new_issues'] = Issue.objects.filter(status="new", project_id=self.kwargs['prkey'],
                                                     sprint_id=self.kwargs['sprintkey'])
        context['in_progress_issues'] = Issue.objects.filter(status="in progress", project_id=self.kwargs['prkey'],
                                                             sprint_id=self.kwargs['sprintkey'])
        context['resolved_issues'] = Issue.objects.filter(status="resolved", project_id=self.kwargs['prkey'],
                                                          sprint_id=self.kwargs['sprintkey'])
        return context
