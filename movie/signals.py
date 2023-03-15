from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from movie.models import Invitation
from movie.tasks import send_invitation, send_attendance_change

USE_CELERY = True


@receiver(post_save, sender=Invitation, dispatch_uid="invitation_create")
def invitation_create(sender, created, instance, **kwargs):
    if created:
        if USE_CELERY:
            send_invitation.delay(instance.pk)
        else:
            send_invitation(instance.pk)


@receiver(pre_save, sender=Invitation, dispatch_uid="invitation_update")
def invitation_update(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous_invitation = Invitation.objects.get(pk=instance.pk)
    instance.attendance_confirmed = True

    # notify if there is attendance change
    if previous_invitation.is_attending != instance.is_attending:
        if USE_CELERY:
            send_attendance_change.delay(instance.pk, instance.is_attending)
        else:
            send_attendance_change(instance.pk, instance.is_attending)
