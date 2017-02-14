from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

from celery.bin import worker


if __name__ == '__main__':
    worker = worker.worker(app=celery_app)

    options = {
        'broker': 'redis://localhost:6379',
        'loglevel': 'INFO',
        'traceback': True,
    }

    worker.run(**options)
