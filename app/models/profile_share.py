from django.db import models


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
        related_name='param_bookmarks',
    )
    receiver = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='user_bookmarks',
    )

    def __str__(self):
        return f'ProfileShare: {self.requester} - {self.receiver}'
