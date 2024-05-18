# frontend_data_handshake/views.py

from django.http import JsonResponse
from rentscraper.models import MasterRentalData

def rental_data_list(request):
    rentals = MasterRentalData.objects.all().values(
        'latitude',
        'longitude',
        'address',
        'name',  # Building name
        'full_url',
        'price_per_month',
        'bedrooms',
        'baths',
        'zone',
        'walk_score',
        'bike_score',
        'transit_score',
        'nearest_superstore',
        'nearest_hospital',
        'time_to_nearest_hospital',
        'time_to_nearest_superstore'
    )
    return JsonResponse(list(rentals), safe=False)
