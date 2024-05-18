import os
import pandas as pd
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rentscraper.models import BuildingDetails
from datetime import datetime

EXPORT_DIR = 'D:\\exports\\'


@api_view(['GET'])
def export_data(request):
    format = request.GET.get('format', 'csv').lower()
    if format not in ['csv', 'excel']:
        return JsonResponse({'error': 'Invalid format. Use "csv" or "excel".'}, status=400)

    buildings = BuildingDetails.objects.all().values()
    df = pd.DataFrame(buildings)

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if format == 'csv':
        file_name = f'buildings_details_{timestamp}.csv'
        file_path = os.path.join(EXPORT_DIR, file_name)
        df.to_csv(file_path, index=False)
    else:
        file_name = f'buildings_details_{timestamp}.xlsx'
        file_path = os.path.join(EXPORT_DIR, file_name)
        df.to_excel(file_path, index=False)

    return JsonResponse({'file_path': file_path}, status=200)
