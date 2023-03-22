# Matinee

Web app for organizations of private film showtimes

Project called Matinee which aims to make it easier to organize times to watch films with friends.

Development in progress

Prior running Docker images, enviroment variables must be set in /doc_env/docker.env. Example file is there.

Finally, run in terminal:

    docker-compose up --build

To run in local machine without Docker:
run local postgres database;
set all enviroment variables (see example file);
run local redis server;
first terminal:
python manage.py runserver
second terminal:
celery -A matinee worker -l INFO
third terminal:
celery -A matinee beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
