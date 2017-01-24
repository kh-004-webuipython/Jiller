from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Issue, Sprint, Project

# Create your views here.


def index(request):
    return render(request, 'workflow/index.html')


def profile(request):
    current_user = request.user
    return render(request, 'workflow/profile.html', {
        'user': current_user
    })

class ProjectListView(ListView):
    model = Project
    paginate_by = 10
    template_name = 'workflow/projects.html'



