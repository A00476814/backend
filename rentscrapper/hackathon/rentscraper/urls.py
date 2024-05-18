# rentscraper/urls.py

from django.urls import path
from rentscraper.views.views import scrape_killamreit_view
from .views.templeton_view import scrape_and_save_listings
from .views.building_details_view import scrape_building_details
from .views.westwood_group_view import scrape_listings
from .views.new_properties_view import scrape_new_properties
from .views.killam_dynamic_scraper_view import scrape_rental_listings_view
from .views.push_to_master_db_view import update_master_data
from .views.push_to_master_rental_db_view import update_master_rental_data
from .views.temp_push_data_view import load_csv


urlpatterns = [
    path('scrape/killamreit/', scrape_killamreit_view, name='scrape_killamreit'),
    path('scrape/killamreit/dynamic', scrape_rental_listings_view, name='scrape_killamreit_dynamic'),
    path('scrape/templeton/', scrape_and_save_listings, name='scrape_templeton'),
    path('scrape/buildingdetails/', scrape_building_details, name='scrape_buildingdetails'),
    path('scrape/westwoodgroup/', scrape_listings, name='scrape_westwoodgroup'),
    path('scrape/newproperties/', scrape_new_properties, name='scrape_newproperties'),
    path('merge/update-master-data/', update_master_data, name='update_master_data'),
    path('merge/update-master-rental-data/', update_master_rental_data, name='update_master_rental_data'),
    path('temp/pushdata/', load_csv, name='push_data'),

]
