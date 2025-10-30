from django.contrib import admin
from .models import Event, Attendee

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'location', 'max_attendees', 'registered_attendees_count', 'is_active', 'registration_open']
    list_filter = ['is_active', 'registration_open', 'start_date']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at']

    def registered_attendees_count(self, obj):
        return obj.registered_attendees_count()
    registered_attendees_count.short_description = 'Registered'

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'event', 'category', 'attendance_status', 'registration_date', 'is_approved']
    list_filter = ['category', 'attendance_status', 'is_approved', 'event', 'registration_date']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'confirmation_code']
    readonly_fields = ['registration_date', 'confirmation_code']
    list_editable = ['attendance_status', 'is_approved']
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'