from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView

from .models import Issue, Sprint

# Create your views here.


def index(request):
    return render(request, 'workflow/index.html')


def issue(request, prkey, issuekey):
    current_issue = get_object_or_404(Issue, pk=issuekey, project=prkey)
    return render(request, 'workflow/issue.html', {
        'issue': current_issue,
    })


class SprintView(DetailView):
    model = Sprint
    template_name = 'workflow/sprint.html'
    query_pk_and_slug = True
    pk_url_kwarg =  'sprintkey'
    slug_field = 'project'
    slug_url_kwarg = 'prkey'


    def get_context_data(self, **kwargs):
        context = super(SprintView, self).get_context_data(**kwargs)
        cur_proj = self.kwargs['prkey']
        cur_spr = self.kwargs['sprintkey']
        issues_from_this_sprint = Issue.objects.filter(project_id=cur_proj, sprint_id=cur_spr)
        context['new_issues'] = issues_from_this_sprint.filter(status="new")
        context['in_progress_issues'] = issues_from_this_sprint.filter(status="in progress")
        context['resolved_issues'] = issues_from_this_sprint.filter(status="resolved")
        return context