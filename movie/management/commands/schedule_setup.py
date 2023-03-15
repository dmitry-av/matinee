from django.core.management.base import BaseCommand

from movie.schedule_setup import schedule_setup


class Command(BaseCommand):
    help = "Run the schedule_setup function"

    def handle(self, *args, **options):
        schedule_setup()
