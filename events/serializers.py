from rest_framework import serializers
from .models import Organizer, Venue, Event, Attendee, Registration
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model. Exposes basic, non-sensitive user information.
    """
    class Meta:
        model = User
        fields = ['id', 'username']


class OrganizerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Organizer model.Includes nested User details for better readability.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = Organizer
        fields = ['id', 'user', 'organization_name']

class VenueSerializer(serializers.ModelSerializer):
    """
    Serializer for the Venue model. Translates Venue data to JSON.
    """
    class Meta:
        model = Venue
        fields = ['id', 'name', 'address', 'capacity']

class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model. Includes nested serializers for Venue and Organizer to provide full details
    """
    organizer = OrganizerSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'venue', 'title', 'description', 'start_time', 'end_time', 'max_attendees'
            ] 

class AttendeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Attendee model. Shows the user's username for better readability instead of just the user ID.
    """
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Attendee
        fields = ['id', 'username']

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Registration model. Used to show which attendee has registered for an event.
    """
    attendee = AttendeeSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'attendee', 'registered_at']