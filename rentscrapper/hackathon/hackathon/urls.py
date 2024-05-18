# myproject/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('datacollection/', include('rentscraper.urls')),
    path('data_manager/', include('data_manager.urls')),
    path('frontend/', include('frontend_data_handshake.urls')),
]