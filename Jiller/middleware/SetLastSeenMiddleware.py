from datetime import timedelta as td
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.conf import settings
from employee.models import Employee

class SetLastSeenMiddleware(object):
    KEY = "last-activity"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated():
            str_last_activity = request.session.get(self.KEY)
            if str_last_activity:
                last_activity = parse_date(str_last_activity)
            else:
                last_activity = None

            # If key is old enough, update database.
            too_old_time = timezone.now() - td(seconds=settings.LAST_ACTIVITY_INTERVAL_SECS)
            if not last_activity or last_activity < too_old_time:
                user = Employee.objects.get(pk=request.user.pk)
                user.last_activity = timezone.now()
                user.save()

            request.session[self.KEY] = str(timezone.now())

        response = self.get_response(request)

        return response
