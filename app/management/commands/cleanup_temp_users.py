from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Profile, User


class Command(BaseCommand):
    """
    Deletes User instances which have 'is_temporary' flag and true, and which
    were created gt 12 hours ago, along with associated Profiles.
    """
    def add_arguments(self, parser):
        parser.add_argument('hours', type=int, nargs='?', default=12)

    def handle(self, *args, **options):
        dt = timezone.now() - timedelta(hours=options["hours"])
        users_to_delete = User.objects.filter(
            is_temporary=True, date_joined__lt=dt).all()
        Profile.objects.filter(user__in=users_to_delete).delete()
        users_to_delete.delete()
