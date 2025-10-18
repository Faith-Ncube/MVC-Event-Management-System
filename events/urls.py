from django.urls import path
from . import views

urlpatterns = [
    path('api/events/', views.EventListCreateAPIView.as_view(), name='api-event-list-create'),
    path('api/events/<int:pk>/', views.EventRetrieveUpdateDestroyAPIView.as_view(), name='api-event-retrieve-update-delete'),

    path('api/events/<int:event_pk>/attendees', views.EventAttendeesAPIView.as_view(), name='api-event-attendees')
]