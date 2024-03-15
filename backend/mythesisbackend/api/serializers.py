from rest_framework import serializers
from .models import UAVFlight, UAVFlightFieldSeasonAssociation, User, Season, Field, FieldSeasonAssociation, FieldImage, ProcessingResult, AnalysisJob
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import serializers

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'farmer'),
        )
        return user

    def update(self, instance, validated_data):
        # Update the User instance
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User is not active.")
        return user

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is not correct")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "New passwords must match"})
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')


# Season Serializer
class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ('id', 'owner', 'name', 'start_date', 'end_date', 'description')


# Field Serializer
class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ('id', 'owner', 'name', 'location', 'description')


# FieldImage Serializer
class FieldImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldImage
        fields = ('id', 'uav_flight', 'image', 'resized_image', 'upload_date', 'description', 'gps_latitude', 'gps_longitude', 'gps_altitude')


class UAVFlightSerializer(serializers.ModelSerializer):
    images = FieldImageSerializer(many=True, read_only=True)

    class Meta:
        model = UAVFlight
        fields = ('id', 'owner', 'flight_date', 'description', 'images')

class UAVFlightFieldSeasonAssociationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UAVFlightFieldSeasonAssociation
        fields = ('id', 'uav_flight', 'field_season')

class FieldSeasonAssociationSerializer(serializers.ModelSerializer):
    uav_flights = UAVFlightSerializer(many=True, read_only=True)

    class Meta:
        model = FieldSeasonAssociation
        fields = ('id', 'field', 'season', 'date_associated', 'uav_flights')
        

class ProcessingResultSerializer(serializers.ModelSerializer):
    image_details = serializers.SerializerMethodField()

    class Meta:
        model = ProcessingResult
        fields = ('id', 'image', 'result_data', 'date_processed', 'generated_image', 'image_details')

    def get_image_details(self, obj):
        # obj.image is the FieldImage instance related to this processing result
        serializer = FieldImageSerializer(obj.image)
        return serializer.data



class AnalysisJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisJob
        fields = ['id', 'owner', 'created_at', 'status', 'uav_flight', 'field_image']

        # Ensure that 'field_image' is optional and can be null
        extra_kwargs = {
            'field_image': {'required': False, 'allow_null': True}
        }




#superuser: ensar
#password: 123456789