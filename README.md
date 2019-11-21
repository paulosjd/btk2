=====
btk2
=====

REST API which serves as a backend for a [web application](http://mysite.com) used to track individuals health metrics.

JSON web tokens are used for authentication. URLs are defined with `btk.urls` and `app.urls`.

Third party libraries include Django 2.1, Django Rest Framework 3.5, Postgres Celery/Redis for running background tasks.


Quick start
-----------

1. Run `python manage.py migrate` to create the database schema.

2. Create a user with admin access by running `python manage.py createsuperuser`
 and then visit http://127.0.0.1:8000/admin/ to manage records.
 
Any pre-existing data can be loaded by running `python manage.py loaddata <file_name>.json`
