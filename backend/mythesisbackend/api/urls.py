from django.urls import path
from .views.views_field import add_field, my_fields, update_field, delete_field
from .views.views_auth import (
    change_password,
    user_registration,
    user_login,
    user_logout,
    user_view,
    user_update,
    user_delete
)
from .views.views_seasons import (
    create_season,
    list_fields_in_season,
    list_seasons,
    get_season,
    update_season,
    delete_season,
    add_fields_to_season,
    remove_field_from_season,
    add_image_to_field_season,
    add_processing_result_to_field_image,
)

from .views.views_flights import (
    create_uav_flight,
    delete_uav_flight,
    get_uav_flights_by_owner,
    link_uav_flight_to_field_season,
    get_uav_flights_for_field_season,
    get_images_for_uav_flight,
)

from .views.views_analysis import start_analysis, get_generated_images_for_uav_flight, uav_flights_with_completed_analysis

from .views.views_mock_server import mock_ml_server

urlpatterns = [
    # Authentication-related URLs
    path('signup/', user_registration, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('user/', user_view, name='user'),
    path('user/update/', user_update, name='user_update'),
    path('user/delete/', user_delete, name='user_delete'),
    path('change-password/', change_password, name='change-password'),

    # Field-related URLs
    path('add-field/', add_field, name='add_field'),
    path('my-fields/', my_fields, name='my_fields'),
    path('update-field/', update_field, name='update_field'),
    path('delete-field/', delete_field, name='delete_field'),

    # Season-related URLs
    path('create-season/', create_season, name='create_season'),
    path('list-seasons/', list_seasons, name='list_seasons'),
    path('get-season/', get_season, name='get_season'),
    path('update-season/', update_season, name='update_season'),
    path('delete-season/', delete_season, name='delete_season'),
    path('add-field-to-season/', add_fields_to_season, name='add_field_to_season'),
    path('remove-field-from-season/', remove_field_from_season, name='remove_field_from_season'),
    path('list-fields-in-season/', list_fields_in_season, name='list_fields_in_season'),
    path('add-image-to-field-season/', add_image_to_field_season, name='add_image_to_field_season'),
    path('add-processing-result-to-field-image/', add_processing_result_to_field_image, name='add_processing_result_to_field_image'),

    # UAV Flight-related URLs
    path('create-uav-flight/', create_uav_flight, name='create_uav_flight'),
    path('link-uav-flight-to-field-season/', link_uav_flight_to_field_season, name='link_uav_flight_to_field_season'),
    path('get-uav-flights-for-field-season/', get_uav_flights_for_field_season, name='get_uav_flights_for_field_season'),
    path('get-images-for-uav-flight/', get_images_for_uav_flight, name='get_images_for_uav_flight'),
    path('get-uav-flights-by-owner/', get_uav_flights_by_owner, name='get_uav_flights_by_owner'),
    path('delete-uav-flight/', delete_uav_flight, name='delete_uav_flight'),

    path('analysis-job/', start_analysis, name='analysis-job'),
    path('mock-ml-server/', mock_ml_server, name='mock-ml-server'),
    path('get-generated-images-for-uav-flight/', get_generated_images_for_uav_flight, name='get_generated_images_for_uav_flight'),
    path('uav-flights-with-completed-analysis/', uav_flights_with_completed_analysis, name='uav_flights_with_completed_analysis'),
]

