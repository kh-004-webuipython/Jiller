from django.shortcuts import get_object_or_404, render

from .models import Issue

# Create your views here.


def index(request):
    return render(request, 'workflow/index.html')


def issue(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id, project=project_id)
    return render(request, 'workflow/issue.html', {
        'issue': current_issue, 'project_id': project_id, 'issue_id': issue_id
    })
