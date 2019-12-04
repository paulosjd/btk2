from django.core.management.base import BaseCommand

from app.models import ProfileShare


class Command(BaseCommand):
    """
    Example usage:
        $ python manage.py reset_demo_share Darrell
    """
    def add_arguments(self, parser):
        parser.add_argument('requester_name', type=str, nargs='?', default='')

    def handle(self, *args, **options):
        req_name = options["requester_name"]
        req_name_list = ['Samuel', 'Joseph']
        if req_name:
            req_name_list.append(req_name)
        instances = ProfileShare.objects.filter(
            requester__user__username__in=req_name_list,
            receiver__user__username='demo'
        ).all()
        for instance in instances:
            instance.enabled = False
            instance.save()
