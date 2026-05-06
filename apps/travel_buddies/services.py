from datetime import timedelta
from django.db.models import Q
from .models import TravelBuddyPost, BuddyRequest


def calculate_match_score(post1, post2):
    """
    Ikki post orasidagi moslik balini hisoblash.
    Yuqori ball = yuqori moslik
    """
    if not post1 or not post2:
        return 0
    
    if post1.id == post2.id:
        return 0
    
    score = 0
    
    # 1. Location mosliklik (+50)
    if post1.location_id == post2.location_id:
        score += 50
    
    # 2. Sana mosliklik
    date_diff = abs((post1.travel_date - post2.travel_date).days)
    
    if date_diff == 0:
        score += 30  # Bir xil sana
    elif date_diff == 1:
        score += 20  # 1 kun farq
    elif date_diff <= 3:
        score += 10  # 2-3 kun farq
    
    # 3. Transport mosliklik (+10)
    if post1.transport_type == post2.transport_type:
        score += 10
    elif post1.transport_type == 'any' or post2.transport_type == 'any':
        score += 5
    
    # 4. Budget oralig'i kesishish (+10)
    if post1.budget_from and post1.budget_to and post2.budget_from and post2.budget_to:
        # Budgetlar kesishadimi?
        if not (post1.budget_to < post2.budget_from or post2.budget_to < post1.budget_from):
            score += 10
    
    # 5. Preferred group mosliklik (+10)
    if post1.preferred_group == post2.preferred_group:
        score += 10
    elif post1.preferred_group == 'everyone' or post2.preferred_group == 'everyone':
        score += 5
    
    return score


def get_matching_posts(post, limit=6, min_score=20):
    """
    Berilgan postga mos boshqa postlarni topish.
    
    Args:
        post: TravelBuddyPost model instance
        limit: maksimal qaytaradigan postlar soni
        min_score: minimal moslik balli
    
    Returns:
        List of (matched_post, score) tuples
    """
    
    # Faqat active postlarni ol, o'z postni istisna qil
    all_posts = TravelBuddyPost.objects.filter(
        is_active=True,
        status='active'
    ).exclude(
        id=post.id,
        user=post.user  # O'z postlarini istisna qil
    )
    
    matches = []
    
    for other_post in all_posts:
        score = calculate_match_score(post, other_post)
        
        if score >= min_score:
            matches.append((other_post, score))
    
    # Ballga qarab teskari tartiblash
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:limit]


def find_potential_buddies(post):
    """
    Post uchun potensial hamrohlarni topish.
    Faqat shu post egasiga hali request yubormagan userlarni qaytaradi.
    """
    matches = get_matching_posts(post)
    
    # Hali request yuborilmagan postlarni filtr qil
    existing_requests = BuddyRequest.objects.filter(
        post=post,
        status__in=['pending', 'accepted']
    ).values_list('from_user_id', flat=True)
    
    potential_buddies = [
        (matched_post, score)
        for matched_post, score in matches
        if matched_post.user_id not in existing_requests
    ]
    
    return potential_buddies


def auto_deactivate_expired_posts():
    """O'tib ketgan vaqt postlarini avtomatik inactive qilish"""
    expired_posts = TravelBuddyPost.objects.filter(
        is_active=True,
        status='active'
    )
    
    count = 0
    for post in expired_posts:
        if post.is_expired():
            post.is_active = False
            post.status = 'completed'
            post.save()
            count += 1
    
    return count
