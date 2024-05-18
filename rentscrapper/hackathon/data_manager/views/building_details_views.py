from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rentscraper.models import BuildingDetails
from data_manager.serializers import BuildingDetailsSerializer

@api_view(['POST'])
def add_building(request):
    try:
        building = BuildingDetails.objects.get(name=request.data.get('name'))
        serializer = BuildingDetailsSerializer(building, data=request.data, partial=True)
    except BuildingDetails.DoesNotExist:
        serializer = BuildingDetailsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_building(request, name):
    try:
        building = BuildingDetails.objects.get(name=name)
        building.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except BuildingDetails.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
def update_building(request, name):
    try:
        building = BuildingDetails.objects.get(name=name)
        serializer = BuildingDetailsSerializer(building, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except BuildingDetails.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_all_buildings(request):
    buildings = BuildingDetails.objects.all()
    serializer = BuildingDetailsSerializer(buildings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_building_by_name(request, name):
    try:
        building = BuildingDetails.objects.get(name=name)
        serializer = BuildingDetailsSerializer(building)
        return Response(serializer.data)
    except BuildingDetails.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)