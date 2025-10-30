from django.urls import path
from . import views

urlpatterns = [
    path('api/events/', views.EventListCreateAPIView.as_view(), name='api-event-list-create'),
    path('api/events/<int:pk>/', views.EventRetrieveUpdateDestroyAPIView.as_view(), name='api-event-retrieve-update-delete'),

    # Event CRUD URLs
    path('api/events/<int:event_pk>/attendees', views.EventAttendeesAPIView.as_view(), name='api-event-attendees')
    path('', views.EventListView.as_view(), name='event-list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('event/new/', views.EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/update/', views.EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
    
    # Attendance URLs
    path('event/<int:pk>/attend/', views.attend_event, name='event-attend'),
    path('event/<int:pk>/unattend/', views.unattend_event, name='event-unattend'),
]