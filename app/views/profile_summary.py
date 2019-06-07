from django.http import JsonResponse
from django.views.generic import View

import logging
log = logging.getLogger(__name__)

class ProfileSummary(View):

    # authprotect decorator
    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id']
        # user = ...  user look up and authenticate (or user auth decorator)
        # serialize user_summary(user)
        # default jsonresponse(error) or 404 or 403
        log.info('PJD sdf')
        print(args)
        print(kwargs)


        return JsonResponse([
            {'name': 'body_weight', 'value': '65.5 kg', 'date': '19th Jan 2019'},
            {'name': 'blood_pressure', 'value': '65.5 kg', 'date': '19th Jan 2019'}], safe=False)



