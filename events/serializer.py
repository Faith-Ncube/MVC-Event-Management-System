from rest_framework import serializers
from .models import model_for_events_to_be_created_by_West

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = model_for_events_to_be_created_by_West
        fields = [] # fields to be exposed in our API

