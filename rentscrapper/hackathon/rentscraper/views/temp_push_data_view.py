import pandas as pd
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from rentscraper.models import BuildingDetails
import os


def load_csv(request):
    # Path to the uploaded CSV file
    csv_file_path = "D:\\updated_buildingdetails____.csv"

    # Read the CSV file using pandas
    try:
        data = pd.read_csv(csv_file_path)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Clear existing data in the table
    BuildingDetails.objects.all().delete()

    # Iterate through the dataframe and create BuildingDetails instances
    for _, row in data.iterrows():
        building_details = BuildingDetails(
            name=row.get('name'),
            builder_name=row.get('builder_name'),
            status=row.get('status'),
            address=row.get('address'),
            latitude=row.get('latitude'),
            longitude=row.get('longitude'),
            zone=row.get('zone'),
            number_of_floors=row.get('number_of_floors'),
            property_type=row.get('property_type'),
            number_of_units=row.get('number_of_units'),
            year_built=row.get('year_built'),
            air_conditioning=row.get('air_conditioning'),
            balcony_patio=row.get('balcony_patio'),
            convenience_store=row.get('convenience_store'),
            elevator=row.get('elevator'),
            fitness_center=row.get('fitness_center'),
            free_outdoor_parking=row.get('free_outdoor_parking'),
            heat_included=row.get('heat_included'),
            laundry_facilities=row.get('laundry_facilities'),
            water_included=row.get('water_included'),
            parking_available=row.get('parking_available'),
            parking_cost=row.get('parking_cost'),
            parking_type=row.get('parking_type'),
            walk_score=row.get('walk_score'),
            transit_score=row.get('transit_score'),
            bike_score=row.get('bike_score'),
            nearest_police_station=row.get('nearest_police_station'),
            nearest_superstore=row.get('nearest_superstore'),
            nearest_pharmacy=row.get('nearest_pharmacy'),
            nearest_hospital=row.get('nearest_hospital'),
            time_to_nearest_hospital=row.get('time_to_nearest_hospital'),
            time_to_nearest_police_station=row.get('time_to_nearest_police_station'),
            time_to_nearest_superstore=row.get('time_to_nearest_superstore'),
            time_to_nearest_pharmacy=row.get('time_to_nearest_pharmacy')
        )
        building_details.save()

    return JsonResponse({'status': 'success', 'message': 'Data loaded successfully'}, status=200)
