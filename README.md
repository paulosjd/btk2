=====
btk2
=====

Serves as backend for a [web application](http://mysite.com) used to track individuals health metrics.

API which uses JSON web token for authentication.
Third party libraries include Django 2.1, Django Rest Framework 3.5, Postgres Celery/Redis for running background tasks.

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'polls',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('polls/', include('polls.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/polls/ to participate in the poll.