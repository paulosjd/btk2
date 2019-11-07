import logging

from django.db import models

log = logging.getLogger(__name__)


class ProfileShare(models.Model):

# Cannot resolve keyword 'name' into field. Choices are: enabled, id,
# message, receiver, receiver_id, requester, requester_id

    message = models.CharField(
        max_length=50,
        default='',
        blank=True,
    )
    enabled = models.BooleanField(
        default=False,
        blank=True,
    )
    requester = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='shares_requested',
    )
    receiver = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='shares_received',
    )

    class Meta:
        unique_together = ('requester', 'receiver')

    def __str__(self):
        return f'ProfileShare: {self.requester} - {self.receiver}'

    def save(self, **kwargs):
        if not self.requester.email_confirmed:
            return
        super(ProfileShare, self).save(**kwargs)

    def get_id_and_profile_name(self, fk_type='requester'):
        return {'id': self.id, fk_type: getattr(self, fk_type).user.username}

