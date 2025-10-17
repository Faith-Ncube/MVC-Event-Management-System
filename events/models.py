from django.db import models
from django.contrib.auth.models import User


# Organizer model (extends User)
class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="organizer_profile")
    organization_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"


# Venue model (physical event space)
class Venue(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"


# Event model (created by organizer, hosted at venue)
class Event(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name="events")
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_attendees = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} @ {self.venue.name}"


# Attendee model (extends User)
class Attendee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="attendee_profile")

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Registration model (links attendees to events)
class Registration(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, related_name="registrations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("attendee", "event")  # prevent double sign-ups

    def __str__(self):
        return f"{self.attendee.user.username} -> {self.event.title}"
