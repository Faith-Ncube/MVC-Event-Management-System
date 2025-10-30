from django.contrib import admin
from .models import Event, Attendee

class AttendeeInline(admin.TabularInline):
    model = Attendee
    extra = 1
    readonly_fields = ['registration_date']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'organizer', 'is_upcoming', 'attendee_count']
    list_filter = ['event_type', 'date', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    inlines = [AttendeeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'event_type', 'image')
        }),
        ('Event Details', {
            'fields': ('date', 'location', 'max_attendees')
        }),
        ('Organizer Information', {
            'fields': ('organizer',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer')

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registration_date', 'has_paid']
    list_filter = ['has_paid', 'registration_date']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['registration_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')