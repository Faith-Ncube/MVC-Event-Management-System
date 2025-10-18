from django.shortcuts import render
from rest_framework import generics
from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer

class EventListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all events or create a new event.
    - GET: Returns a list of all events.
    - POST: Create a new event.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a single event by its ID.
    - GET: Retrieve details of a specific event.
    - PUT/PTACH: Update a specific event.
    - DELETE: Delete a specific  event.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventAttendeesAPIView(generics.ListAPIView):
    """
    This view returns a list of all attendees registered for a specific event.
    """
    serializer_calss = RegistrationSerializer

    def get_quesryset(self):
        # This method overrides the default queryset to filter registrations
        # based on the event's primary key ('event_pk') passed in the URL.
        event_id = self.kwargs['event_pk']
        return Registration.objects.filter(event_id=event_id)