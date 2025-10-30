from django.shortcuts import render
from rest_framework import generics
from .models import Event, Registration, Attendee
from .serializers import EventSerializer, RegistrationSerializer
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = Event.objects.filter(is_active=True).select_related('organizer')
        
        # Filter by event type if provided
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
            
        # Filter by search query if provided
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(location__icontains=search_query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_types'] = Event.EVENT_TYPES
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.select_related('organizer').prefetch_related('attendees__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        # Check if current user is attending
        if self.request.user.is_authenticated:
            context['is_attending'] = Attendee.objects.filter(
                event=event, 
                user=self.request.user
            ).exists()
        else:
            context['is_attending'] = False
            
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['title', 'description', 'event_type', 'date', 'location', 'max_attendees', 'image']

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    template_name = 'events/event_form.html'
    fields = ['title', 'description', 'event_type', 'date', 'location', 'max_attendees', 'image', 'is_active']

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def attend_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Check if user is already attending
    if Attendee.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
    else:
        # Check if event has attendee limit
        if event.max_attendees > 0 and event.attendee_count >= event.max_attendees:
            messages.error(request, 'This event is full.')
        else:
            Attendee.objects.create(event=event, user=request.user)
            messages.success(request, 'Successfully registered for the event!')
    
    return redirect('event-detail', pk=pk)

@login_required
def unattend_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    attendee = Attendee.objects.filter(event=event, user=request.user).first()
    
    if attendee:
        attendee.delete()
        messages.success(request, 'Successfully unregistered from the event.')
    else:
        messages.warning(request, 'You are not registered for this event.')
    
    return redirect('event-detail', pk=pk)


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
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        # This method overrides the default queryset to filter registrations
        # based on the event's primary key ('event_pk') passed in the URL.
        event_id = self.kwargs['event_pk']
        return Registration.objects.filter(event_id=event_id)