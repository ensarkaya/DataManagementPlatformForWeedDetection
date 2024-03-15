from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import FieldSeasonAssociationSerializer, UAVFlightFieldSeasonAssociationSerializer, UAVFlightSerializer
from ..models import FieldSeasonAssociation, UAVFlight, FieldImage, UAVFlightFieldSeasonAssociation
from ..utils import get_image_metadata, convert_gps_to_decimal, resize_image

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_uav_flight(request):
    flight_data = request.data
    user = request.user
    uav_flight_serializer = UAVFlightSerializer(data=flight_data)
    if uav_flight_serializer.is_valid():
        uav_flight = uav_flight_serializer.save(owner=user)

        # Handle Image Uploads
        images = request.FILES.getlist('images')
        for image in images:

            metadata = get_image_metadata(image)
            # Convert GPS coordinates to decimal
            gps_latitude_decimal = convert_gps_to_decimal(metadata['gps_latitude'], metadata['gps_latitude_ref'])
            gps_longitude_decimal = convert_gps_to_decimal(metadata['gps_longitude'], metadata['gps_longitude_ref'])

            # Re-open the stream for PIL processing
            resized_image = resize_image(image)
            field_image_instance = FieldImage.objects.create(uav_flight=uav_flight, image=image,  gps_latitude=gps_latitude_decimal, gps_longitude=gps_longitude_decimal, gps_altitude=metadata['gps_altitude'])
            field_image_instance.resized_image.save(image.name, resized_image, save=True)

        return Response(uav_flight_serializer.data, status=status.HTTP_201_CREATED)
    uav_flight.delete()
    return Response(uav_flight_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_uav_flight(request):
    uav_flight_id = request.data.get('uav_flight_id')
    uav_flight = get_object_or_404(UAVFlight, id=uav_flight_id)
    uav_flight.delete()
    return Response({'message': 'UAV Flight deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_uav_flight_to_field_season(request):
    user = request.user
    field_id = request.data.get('field_id')
    season_id = request.data.get('season_id')
    uav_flight_ids = request.data.get('uav_flight_ids', []) 

    # Check if FieldSeasonAssociation exists for given field and season
    field_season_association = get_object_or_404(FieldSeasonAssociation, field_id=field_id, season_id=season_id, field__owner=user)

    # Link each UAV Flight to the FieldSeasonAssociation
    for uav_flight_id in uav_flight_ids:
        uav_flight = get_object_or_404(UAVFlight, id=uav_flight_id)
        UAVFlightFieldSeasonAssociation.objects.create(uav_flight=uav_flight, field_season=field_season_association)

    return Response({'message': f'{len(uav_flight_ids)} UAV Flights linked successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_uav_flights_for_field_season(request):
    season_id = request.query_params.get('season_id')
    field_id = request.query_params.get('field_id')
    try:
        field_season_association = FieldSeasonAssociation.objects.get(field=field_id, season=season_id)
    except FieldSeasonAssociation.DoesNotExist:
        return Response({'error': 'FieldSeasonAssociation not found {}, {}'.format(season_id, field_id)}, status=status.HTTP_404_NOT_FOUND)

    serializer = FieldSeasonAssociationSerializer(field_season_association)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_images_for_uav_flight(request):
    uav_flight_id = request.data.get('uav_flight_id')
    try:
        uav_flight = UAVFlight.objects.get(id=uav_flight_id)
    except UAVFlight.DoesNotExist:
        return Response({'error': 'UAVFlight not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UAVFlightSerializer(uav_flight)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_uav_flights_by_owner(request):
    user = request.user
    uav_flights = UAVFlight.objects.filter(owner=user)
    serializer = UAVFlightSerializer(uav_flights, many=True)
    return Response(serializer.data)
