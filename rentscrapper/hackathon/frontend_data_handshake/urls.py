# frontend_data_handshake/urls.py

from django.urls import path
from frontend_data_handshake.views.get_rental_listings_view import rental_data_list
from frontend_data_handshake.views.get_building_details_view import building_details_list
from frontend_data_handshake.views.get_upcoming_project_view import future_properties_list


urlpatterns = [
    path('get-rental-data/', rental_data_list, name='rental_data_list'),
    path('get-building-details/', building_details_list, name='building_details_list'),
    path('get-upcoming-projects/', future_properties_list, name='upcoming_project_list'),
]
