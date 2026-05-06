from django.shortcuts import render, get_object_or_404
from .models import Location

def location_list(request):
    locations = Location.objects.all().order_by('category', 'name')
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        locations = locations.filter(category__id=category)
    
    # Get all categories for filter
    from apps.survey.models import Interest
    categories = Interest.objects.all()
    
    context = {
        'locations': locations,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'locations/list.html', context)

def location_detail(request, id):
    location = get_object_or_404(Location, id=id)
    
    # Get similar locations (same category)
    similar_locations = Location.objects.filter(
        category=location.category
    ).exclude(id=location.id)[:4]
    
    context = {
        'location': location,
        'similar_locations': similar_locations,
    }
    return render(request, 'locations/detail.html', context)