from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urljoin

from movie.models import Showtime


def send_starting_notification(showtime):
    subject = render_to_string(
        "movie/notifications/starting_subject.txt",
        {"showtime": showtime},
    )

    showtime_path = reverse("showtime_detail_ui", args=(showtime.pk,))

    body = render_to_string(
        "movie/notifications/starting_body.txt",
        {
            "showtime": showtime,
            "showtime_url": urljoin(settings.BASE_URL, showtime_path),
        },
    )

    to_emails = [
        invite.invited.email for invite in showtime.invites.filter(is_attending=True)
    ]
    to_emails.append(showtime.creator.email)

    send_mail(
        subject,
        body,
        None,
        to_emails,
    )
    showtime.start_notification_sent = True
    showtime.save()


def send_invitation(invitation):
    subject = render_to_string(
        "movie/notifications/invitation_subject.txt",
        {"showtime": invitation.showtime},
    )

    showtime_path = reverse(
        "showtime_detail_ui", args=(invitation.showtime.pk,)
    )

    body = render_to_string(
        "movie/notifications/invitation_body.txt",
        {
            "creator": invitation.showtime.creator,
            "showtime": invitation.showtime,
            "showtime_url": urljoin(settings.BASE_URL, showtime_path),
        },
    )

    send_mail(
        subject,
        body,
        None,
        [invitation.invited.email],
    )


def send_attendance_change(invitation, is_attending):
    subject = render_to_string(
        "movie/notifications/attendance_update_subject.txt",
        {
            "showtime": invitation.showtime,
            "invitation": invitation,
        },
    )

    showtime_path = reverse(
        "showtime_detail_ui", args=(invitation.showtime.pk,)
    )

    body = render_to_string(
        "movies/notifications/attendance_update_body.txt",
        {
            "is_attending": is_attending,
            "invitation": invitation,
            "showtime": invitation.showtime,
            "showtime_url": urljoin(settings.BASE_URL, showtime_path),
        },
    )

    send_mail(
        subject,
        body,
        None,
        [invitation.showtime.creator.email],
    )


def starting_soon_notification():
    start_before = timezone.now() + timedelta(minutes=30)
    showtimes = Showtime.objects.filter(
        start_time__lte=start_before, start_notification_sent=False
    )

    for showtime in showtimes:
        send_starting_notification(showtime)
