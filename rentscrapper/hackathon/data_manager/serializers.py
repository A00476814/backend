from rest_framework import serializers
from rentscraper.models import BuildingDetails

class BuildingDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingDetails
        fields = '__all__'