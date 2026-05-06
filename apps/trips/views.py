from django.shortcuts import render
from django.utils import timezone
from datetime import time, timedelta
from apps.survey.models import Survey
from apps.locations.models import Location
from .models import Trip, TripStop
from .generator import generate_locations, sort_by_distance

def trip_result(request, survey_id):
    survey = Survey.objects.get(id=survey_id)

    locations = generate_locations(survey)
    locations = sort_by_distance(locations)

    trip = Trip.objects.create(
        user=request.user,
        survey=survey
    )

    # Sayohat vaqtini hisoblash
    current_time = time(9, 0)  # 09:00 dan boshlash
    
    for i, loc in enumerate(locations):
        # Vaqt-ni hisoblash
        arrival_hour = current_time.hour + (i * 2)  # Har bir joy uchun 2 soat oraliq
        if arrival_hour > 23:
            arrival_hour = arrival_hour - 24
        
        arrival_time = time(arrival_hour, current_time.minute)
        
        # Ketish vaqti = Kelish vaqti + o'rtacha vaqt
        departure_hour = arrival_hour + (loc.avg_duration // 60)
        departure_minute = current_time.minute + (loc.avg_duration % 60)
        if departure_minute >= 60:
            departure_hour += 1
            departure_minute -= 60
        if departure_hour > 23:
            departure_hour = departure_hour - 24
        
        departure_time = time(departure_hour, departure_minute)
        
        TripStop.objects.create(
            trip=trip,
            location=loc,
            order=i+1,
            estimated_arrival=arrival_time,
            estimated_departure=departure_time
        )

    stops = TripStop.objects.filter(trip=trip).order_by('order')

    return render(request, 'trips/result.html', {
        'trip': trip,
        'stops': stops,
        'survey': survey
    })