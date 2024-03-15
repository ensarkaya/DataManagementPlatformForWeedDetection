from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Field, FieldImage, FieldSeasonAssociation, ProcessingResult, Season, User
from ..serializers import FieldSerializer, SeasonSerializer 
from rest_framework import status
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_season(request):
    season_data = request.data
    user_id = request.user.id  

    serializer = SeasonSerializer(data=season_data)
    if serializer.is_valid():
        serializer.save(owner_id=user_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_seasons(request):
    user_id = request.user.id
    seasons = Season.objects.filter(owner_id=user_id)
    serializer = SeasonSerializer(seasons, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_season(request):
    season_id = request.data.get('season_id')
    season = get_object_or_404(Season, id=season_id, owner=request.user)
    serializer = SeasonSerializer(season)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_season(request):
    season_id = request.data.get('season_id')
    try:
        season = Season.objects.get(id=season_id, owner=request.user)
    except Season.DoesNotExist:
        return Response({'detail': 'Season not found or you are not the owner.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SeasonSerializer(season, data=request.data, partial=True)  # partial=True allows for partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_season(request):
    season_id = request.data.get('season_id')
    season = get_object_or_404(Season, id=season_id, owner=request.user)
    season.delete()
    return Response({'detail': 'Season deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_fields_to_season(request):
    user = request.user
    season_id = request.data.get('season_id')
    field_ids = request.data.get('field_ids')  

    if not isinstance(field_ids, list):
        return Response({'detail': 'field_ids should be a list.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if season exists and belongs to the user
    season = get_object_or_404(Season, id=season_id, owner=user)

    for field_id in field_ids:
        # Check if each field exists and belongs to the user
        field = get_object_or_404(Field, id=field_id, owner=user)

        # Create association for each field
        FieldSeasonAssociation.objects.create(field=field, season=season)

    return Response({'detail': 'Fields added to season successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_fields_in_season(request):
    user = request.user
    season_id = request.query_params.get('season_id')

    # Check if season exists and belongs to the user
    season = get_object_or_404(Season, id=season_id, owner=user)

     # Get FieldSeasonAssociation objects related to the season
    field_season_associations = FieldSeasonAssociation.objects.filter(season=season)

    # Get fields from the associations
    fields = [association.field for association in field_season_associations]

    # Serialize fields
    serializer = FieldSerializer(fields, many=True)

    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_field_from_season(request):
    user = request.user
    season_id = request.data.get('season_id')
    field_id = request.data.get('field_id')

    # Check if season exists and belongs to the user
    season = get_object_or_404(Season, id=season_id, owner=user)

    # Check if field exists and belongs to the user
    field = get_object_or_404(Field, id=field_id, owner=user)

    # Check if association exists
    association = get_object_or_404(FieldSeasonAssociation, field=field, season=season)

    # Delete association
    association.delete()

    return Response({'detail': 'Field removed from season successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_image_to_field_season(request):
    season_id = request.data.get('season_id')
    field_id = request.data.get('field_id')

    # Retrieve the Season and Field instances
    season = get_object_or_404(Season, id=season_id)
    field = get_object_or_404(Field, id=field_id, owner=request.user)

    # Get or create the FieldSeasonAssociation instance
    field_season, created = FieldSeasonAssociation.objects.get_or_create(
        season=season,
        field=field
    )

    images = request.FILES.getlist('image')
    
    for image in images:
        # Create FieldImage for each image
        FieldImage.objects.create(
            field_season=field_season,
            image=image,
            upload_date=timezone.now(),
            # Handle other fields like description, uav_flight_date, etc., as needed
        )

    return Response({'detail': f'{len(images)} images added successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_processing_result_to_field_image(request):

    field_image_id = request.data.get('field_image_id')
    result_data = request.data.get('result_data')  # JSON data with processing results

    # Check if FieldImage exists and belongs to the user
    field_image = get_object_or_404(FieldImage, id=field_image_id, field_season__field__owner=request.user)

    # Create ProcessingResult
    processing_result = ProcessingResult.objects.create(image=field_image, result_data=result_data)

    # Handle other fields like date_processed as needed

    return Response({'detail': 'Processing result added successfully.'}, status=status.HTTP_201_CREATED)
