from __future__ import absolute_import

from celery import Celery
from celery import task

CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'


celery = Celery('articurate.celery',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND,
                include=['articurate.celery.tasks',
                		 'articurate.fd.celery_tasks',
                		 'articurate.nertagger.celery_tasks'])

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_CHORD_PROPAGATES = True,
)

if __name__ == '__main__':
    celery.start()