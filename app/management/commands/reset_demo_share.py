from django.core.management.base import BaseCommand

from app.models import ProfileShare


class Command(BaseCommand):
    """
    Example usage:
        $ python manage.py reset_demo_share Darrell
    """
    def add_arguments(self, parser):
        parser.add_argument('requester_name', type=str, nargs='?',
                            default='Samuel')

    def handle(self, *args, **options):
        req_name = options["requester_name"]
        instance = ProfileShare.objects.filter(
            requester__user__username=req_name,
            receiver__user__username='demo'
        ).first()
        if instance:
            instance.enabled = False
            instance.save()
