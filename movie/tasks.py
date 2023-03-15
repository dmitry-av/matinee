from movie import notifications
from movie.models import Invitation
from celery import shared_task


@shared_task
def send_invitation(m_pk):
    notifications.send_invitation(Invitation.objects.get(pk=m_pk))


@shared_task
def send_attendance_change(m_pk, is_attending):
    notifications.send_attendance_change(
        Invitation.objects.get(pk=m_pk), is_attending
    )


@shared_task
def starting_soon_notification():
    notifications.starting_soon_notification()
