
from django.http import JsonResponse
from django.views.generic import View


class CsvUpload(View):

    def post(self, request, *args, **kwargs):
        # First step to specific format?
        # THis method should authenticate based on credentials in headers ...
        # depending on args - if file ... call generate_preview which returns json to use in react to nmake preview
        # with hidden field a la postcode.. then when this method called again, takes post data, calls another
        # method (or method on profile)
        print(request.POST)
        print(dir(request))
        print(request)
        print(request.body)
        print(request.POST)

        return JsonResponse({'foo': 'bar'}, safe=False)


    def generate_preview(self):
        pass


    