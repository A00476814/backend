from django.urls import path
from data_manager.views.building_details_views import add_building, delete_building, update_building, get_all_buildings, get_building_by_name
from data_manager.views.building_details_export_view import export_data

urlpatterns = [
    path('buildings/', add_building, name='add_building'),
    path('buildings/<str:name>/', delete_building, name='delete_building'),
    path('buildings/update/<str:name>/', update_building, name='update_building'),
    path('buildings/all/', get_all_buildings, name='get_all_buildings'),
    path('buildings/<str:name>/', get_building_by_name, name='get_building_by_name'),
    path('export/', export_data, name='export_data'),
]