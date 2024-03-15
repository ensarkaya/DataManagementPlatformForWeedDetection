from os import path
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import User, Field, FieldImage, ProcessingResult, Season, FieldSeasonAssociation
from .views.views_field import add_field

# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = "Weed Detection Admin"
    site_title = "Weed Detection Admin Portal"
    index_title = "Welcome to the Weed Detection Admin Portal"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('api/field/add/', self.admin_view(add_field), name="add_field"),
        ]
        return custom_urls + urls

admin_site = CustomAdminSite(name='custom_admin')
"""
# Registering the Field model with the custom admin site using OSMGeoAdmin
@admin.register(Field)
class FieldAdmin(OSMGeoAdmin):
    list_display = ('name', 'owner', 'description')
    list_filter = ('owner',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'start_date', 'end_date', 'description')
    list_filter = ('owner', 'start_date', 'end_date')
    search_fields = ('name', 'description', 'owner__username')
    ordering = ('start_date',)


@admin.register(FieldSeasonAssociation)
class FieldSeasonAssociationAdmin(admin.ModelAdmin):
    list_display = ('field', 'season', 'date_associated')
    list_filter = ('field', 'season')
    search_fields = ('field__name', 'season__name')
    ordering = ('date_associated',)


@admin.register(FieldImage)
class FieldImageAdmin(admin.ModelAdmin):
    list_display = ('field_season', 'upload_date', 'description')
    list_filter = ('field_season__field', 'field_season__season')
    search_fields = ('description', 'field_season__field__name', 'field_season__season__name')
    ordering = ('upload_date',)


@admin.register(ProcessingResult)
class ProcessingResultAdmin(admin.ModelAdmin):
    list_display = ('image', 'date_processed')
    list_filter = ('date_processed',)
    search_fields = ('image__description', 'image__field_season__field__name', 'image__field_season__season__name')
    ordering = ('date_processed',)
"""