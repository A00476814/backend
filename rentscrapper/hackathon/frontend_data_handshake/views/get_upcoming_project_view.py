from django.http import JsonResponse
from rentscraper.models import FutureProperties

def future_properties_list(request):
    properties = FutureProperties.objects.all().values(
        'title',
        'date_of_post',
        'blog_link',
        'image_url',
        'floors',
        'units',
        'cost',
        'property_type',
        'address',
        'builder',
        'latitude',
        'longitude',
        'zone'
    )
    return JsonResponse(list(properties), safe=False)