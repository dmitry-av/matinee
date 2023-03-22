# Matinee

Web app for organizations of private film showtimes

Project called Matinee which aims to make it easier to organize times to watch films with friends.

Development in progress

Prior running Docker images, enviroment variables must be set in /doc_env/docker.env. Example file is there.

Finally, run in terminal:

_docker-compose up --build_

To run in local machine without Docker:
install requirements from requirements.txt or using pipenv.
run local postgres database;  
set all enviroment variables (see example file);  
run local redis server;

first terminal:  
_python manage.py runserver_

second terminal:  
_celery -A matinee worker -l INFO_

third terminal:  
_celery -A matinee beat -l INFO --scheduler django_celery_beat. schedulers:DatabaseScheduler_
