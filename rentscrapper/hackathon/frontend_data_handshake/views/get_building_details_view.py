# frontend_data_handshake/views.py

from django.http import JsonResponse
from rentscraper.models import BuildingDetails


def building_details_list(request):
    buildings = BuildingDetails.objects.all().values(
        'name',
        'builder_name',
        'status',
        'address',
        'latitude',
        'longitude',
        'zone',
        'number_of_floors',
        'property_type',
        'number_of_units',
        'year_built',
        'air_conditioning',
        'balcony_patio',
        'convenience_store',
        'elevator',
        'fitness_center',
        'free_outdoor_parking',
        'heat_included',
        'laundry_facilities',
        'water_included',
        'parking_available',
        'parking_cost',
        'parking_type',
        'walk_score',
        'transit_score',
        'bike_score',
        'nearest_police_station',
        'nearest_superstore',
        'nearest_pharmacy',
        'nearest_hospital',
        'time_to_nearest_hospital',
        'time_to_nearest_police_station',
        'time_to_nearest_superstore',
        'time_to_nearest_pharmacy'
    )
    return JsonResponse(list(buildings), safe=False)