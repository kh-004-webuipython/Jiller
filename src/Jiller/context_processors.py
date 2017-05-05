from project.models import Project


def project_list(request):
    projects = Project.objects.get_user_projects(
            request.user).order_by('-start_date')
    return {'project_list': projects}
