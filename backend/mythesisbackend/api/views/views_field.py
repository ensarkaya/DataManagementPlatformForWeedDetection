from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import GEOSGeometry, Polygon
from ..models import Field, User
from ..serializers import FieldSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_field(request):
    field_data = request.data.get('field')
    user_id = request.user.id 

    # Convert location data to Polygon
    location_data = field_data.get('location', [])
    if location_data:
        # Convert list of coordinate dicts to tuple of tuples
        coords = tuple((point['lng'], point['lat']) for point in location_data)

        # Ensure the polygon is closed (first and last points are the same)
        if coords and coords[0] != coords[-1]:
            coords = coords + (coords[0],)

        # Create a Polygon from the coordinates
        polygon = Polygon(coords)
        field_data['location'] = GEOSGeometry(polygon.wkt)

    serializer = FieldSerializer(data=field_data)
    if serializer.is_valid():
        serializer.save(owner_id=user_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_fields(request):
    # Get the user ID from the request
    user_id = request.user.id
    # Retrieve the user object from the database
    user = get_object_or_404(User, id=user_id)

    # Get fields for the user
    fields = Field.objects.filter(owner=user)
    serializer = FieldSerializer(fields, many=True)
    
    return Response(serializer.data)


# Update a Field
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_field(request):
    field_data = request.data.get('field')
    field_id = field_data['id']
    field = get_object_or_404(Field, id=field_id)
    if request.user != field.owner and request.user.role != 'admin':
        return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
    # Convert location data to Polygon
    location_data = field_data.get('location', [])
    if location_data:
        # Convert list of coordinate dicts to tuple of tuples
        coords = tuple((point['lng'], point['lat']) for point in location_data)

        # Ensure the polygon is closed (first and last points are the same)
        if coords and coords[0] != coords[-1]:
            coords = coords + (coords[0],)

        # Create a Polygon from the coordinates
        polygon = Polygon(coords)
        field_data['location'] = GEOSGeometry(polygon.wkt)

    serializer = FieldSerializer(data=field_data)
    serializer = FieldSerializer(field, data=field_data, partial=True)  # partial=True allows for partial updates
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a Field
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_field(request):
    field_id = request.data.get('field_id')
    field = get_object_or_404(Field, id=field_id)
    if request.user != field.owner and request.user.role != 'admin':
        return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

    field.delete()
    return Response({'detail': 'Field deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
