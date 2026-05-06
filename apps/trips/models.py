from django.db import models
from django.contrib.auth.models import User
from apps.locations.models import Location
from apps.survey.models import Survey

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class TripStop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    order = models.IntegerField()
    estimated_arrival = models.TimeField(null=True, blank=True)
    estimated_departure = models.TimeField(null=True, blank=True)