from apps.locations.models import Location

def generate_locations(survey):
    locations = Location.objects.all()

    # 🔥 TO‘G‘RI FILTER
    locations = Location.objects.filter(
    category__in=survey.interests.all()
)
    # Sog‘liq
    if survey.health.exists():
        locations = locations.filter(difficulty__lte=2)

    # Hamroh
    if survey.companion:
        if "oila" in survey.companion.name.lower():
            locations = locations.filter(is_family_friendly=True)

    # ❗ AGAR BO‘SH BO‘LSA fallback
    if not locations.exists():
        locations = Location.objects.all()

    return locations[:5]

def sort_by_distance(locations):
    locations = list(locations)

    if not locations:
        return []

    sorted_list = [locations[0]]
    locations.remove(locations[0])

    while locations:
        last = sorted_list[-1]

        next_loc = min(
            locations,
            key=lambda x: distance(
                last.latitude, last.longitude,
                x.latitude, x.longitude
            )
        )

        sorted_list.append(next_loc)
        locations.remove(next_loc)

    return sorted_list