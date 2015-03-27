from fd_celery_tasks import *

res = mul.delay(3,3)
res.get(timeout=1)

print mul.apply_async((3, 3))
