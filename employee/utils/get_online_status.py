from datetime import timedelta as td
from django.utils import timezone
from django.utils import formats


def get_online_status(last_activity):
    now = timezone.now()
    moreThanHourGap = now - td(hours=1)
    gap = now - td(seconds=900)
    if last_activity < moreThanHourGap and \
                    timezone.localtime(now).day != timezone.localtime(last_activity).day:
        status = 'last seen ' + str(formats.date_format(timezone.localtime(
            last_activity), 'DATE_FORMAT')) + ' at ' \
                 + str(formats.date_format(timezone.localtime(
            last_activity), 'TIME_FORMAT'))
    elif last_activity < moreThanHourGap:
        status = 'last seen today at ' + str(formats.date_format(timezone.localtime(
            last_activity), 'TIME_FORMAT'))
    elif last_activity <= gap:
        delta = now - last_activity
        status = 'last seen ' + str(td(seconds=delta.seconds).seconds / 60) + ' minutes ago'
    elif last_activity > gap:
        status = 'Online'

    return status