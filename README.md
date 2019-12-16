**btk2**

REST API backend for a [web application](http://mysite.com) used to track individuals health metrics.

Third party libraries include Django 2.1, PyJWT, Django Rest Framework 3.5 and Celery 4.3. 
Configured to use Postgres for the database and Redis as the message broker for Celery tasks.

Quick start
-----------

    $ apt-get update
    $ apt-get install python3-pip python3-dev python3-venv nginx redis-server -y

1. Clone the repository and install requirements using `pip`

2. Run `python manage.py migrate` to create the database schema

3. Create a user with administrative permissions by running `python manage.py createsuperuser`
 and then use the admin views to manage records
 
Tasks require Redis to be installed and a server running.

Data can be loaded using `python manage.py loaddata <file_name>.json`
