import logging

from django.db import models

log = logging.getLogger(__name__)


class ProfileShare(models.Model):

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

    def get_id_and_profile(self, fk_type: str = 'requester') -> dict:
        return {'id': self.id,
                'profile_id': getattr(self, fk_type).id,
                fk_type: getattr(self, fk_type).user.username}
