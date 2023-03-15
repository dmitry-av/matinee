from django_celery_beat.models import IntervalSchedule, PeriodicTask


def schedule_setup():
    interval_schedule = IntervalSchedule.objects.create(
        every=1, period=IntervalSchedule.MINUTES
    )

    PeriodicTask.objects.create(
        task="movie.tasks.starting_soon_notification", interval=interval_schedule
    )
