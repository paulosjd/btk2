
Django Rest Framework based API which uses JSON web token for authentication
and Celery/Redis for running background tasks.

**Getting started**

pip install requirements, install and configure Celery/redis,
create Postgres database, run migrations and then run the server.


running celery on windows:
celery worker -A btk2 --pool=solo -l info



# TODO

send_mail functionality:  use_ssl=True etc.