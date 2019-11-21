from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Profile, User


class Command(BaseCommand):
    """
    Deletes User records (and children) which have 'is_temporary' flag True.
    Applies to those created gt 12 hrs beforehand, or a number specified by an
    optional argument

    Example usage:
        $ python manage.py cleanup_temp_users 6
    """
    def add_arguments(self, parser):
        parser.add_argument('hours', type=int, nargs='?', default=12)

    def handle(self, *args, **options):
        dt = timezone.now() - timedelta(hours=options["hours"])
        users_to_delete = User.objects.filter(
            is_temporary=True, date_joined__lt=dt).all()
        Profile.objects.filter(user__in=users_to_delete).delete()
        users_to_delete.delete()
