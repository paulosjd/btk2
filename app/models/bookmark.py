from django.db import models, DataError


class Bookmark(models.Model):

    url = models.URLField(
        max_length=200,
    )
    title = models.CharField(
        max_length=50,
        default='',
        blank=True,
    )
    param_name = models.CharField(
        max_length=50,
        default='',
        blank=True,
    )
    profile = models.ForeignKey(
        'app.Profile',
        on_delete=models.CASCADE,
        related_name='user_bookmarks',
    )

    def __str__(self):
        return f'{self.profile} - {self.title}'
