from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import Step1InterestsForm, Step2CompanionForm, Step3HealthForm, Step4DateForm, SurveyForm
from .models import Survey
from apps.locations.models import Location
from apps.survey.models import Interest, Companion, HealthCondition

def survey_detail(request, id):
    survey = get_object_or_404(Survey, id=id)
    return render(request, 'survey/detail.html', {'survey': survey})

@login_required
def survey_results(request, survey_id):
    """So'rovnoma natijalarini ko'rsatish - mos joylar va takliflar"""
    survey = get_object_or_404(Survey, id=survey_id)

    # So'rovnomaga mos joylarni topish
    matching_locations = Location.objects.filter(
        category__in=survey.interests.all()
    )

    # Sog'liq holatiga qarab filtrlash
    if survey.health.exists():
        # Agar sog'liq muammolari bo'lsa, oson joylarni afzal qilish
        health_issues = survey.health.all()
        # Masalan, yurish qiyin bo'lsa, past difficulty joylar
        if any('yurish' in health.name.lower() or 'oyoq' in health.name.lower() for health in health_issues):
            matching_locations = matching_locations.filter(difficulty__lte=2)

    # Kim bilan sayohat qilishga qarab filtrlash
    if survey.companion.name.lower() in ['oila', 'bolalar bilan']:
        matching_locations = matching_locations.filter(is_family_friendly=True)

    # Eng mos 6-8 ta joyni tanlash
    recommended_locations = matching_locations[:8]

    # Qo'shimcha takliflar (boshqa kategoriyalar)
    additional_suggestions = []
    for interest in survey.interests.all():
        other_locations = Location.objects.filter(
            category=interest
        ).exclude(id__in=[loc.id for loc in recommended_locations])[:3]
        additional_suggestions.extend(other_locations)

    # Agar kam joy topilsa, barcha joylardan qo'shimcha takliflar
    if len(recommended_locations) < 6:
        all_other_locations = Location.objects.exclude(
            id__in=[loc.id for loc in recommended_locations] + [loc.id for loc in additional_suggestions]
        )[:6-len(recommended_locations)]
        additional_suggestions.extend(all_other_locations)

    context = {
        'survey': survey,
        'recommended_locations': recommended_locations,
        'additional_suggestions': additional_suggestions[:6],  # Maksimum 6 ta qo'shimcha taklif
        'total_matches': len(recommended_locations),
    }

    return render(request, 'survey/results.html', context)

@login_required
def survey_create(request):
    """Ketma-ket so'rovnoma shakli"""
    step = int(request.GET.get('step', 1))
    
    # Sessiyada ma'lumotlarni saqlash
    if 'survey_data' not in request.session:
        request.session['survey_data'] = {}
    
    survey_data = request.session['survey_data']
    
    # Bosqichlarni aniqlash
    steps = [
        {'num': 1, 'title': 'Qiziqishlar', 'form_class': Step1InterestsForm},
        {'num': 2, 'title': 'Kim bilan', 'form_class': Step2CompanionForm},
        {'num': 3, 'title': 'Sog\'liq holati', 'form_class': Step3HealthForm},
        {'num': 4, 'title': 'Sayohat sanasi', 'form_class': Step4DateForm},
    ]
    
    # Bosqichni tekshirish
    if step < 1 or step > 4:
        step = 1
    
    current_step = steps[step - 1]
    
    if request.method == 'POST':
        action = request.POST.get('action', 'next')
        
        if action == 'next':
            form = current_step['form_class'](request.POST)
            if form.is_valid():
                # Ma'lumotlarni sessiyaga saqlash
                if step == 1:
                    survey_data['interests'] = [int(id) for id in form.cleaned_data['interests'].values_list('id', flat=True)]
                elif step == 2:
                    survey_data['companion'] = form.cleaned_data['companion'].id
                elif step == 3:
                    survey_data['health'] = [int(id) for id in form.cleaned_data['health'].values_list('id', flat=True)]
                elif step == 4:
                    survey_data['date'] = str(form.cleaned_data['date'])
                    # Barcha ma'lumotlar to'plandi, so'rovnomani saqlash
                    survey = Survey.objects.create(
                        user=request.user,
                        date=form.cleaned_data['date']
                    )
                    survey.interests.set(survey_data['interests'])
                    survey.companion_id = survey_data['companion']
                    if survey_data.get('health'):
                        survey.health.set(survey_data['health'])
                    survey.save()
                    
                    # Sessiyani tozalash
                    del request.session['survey_data']
                    messages.success(request, "So'rovnoma muvaffaqiyatli yakunlandi! 🎉")
                    return redirect('survey:results', survey_id=survey.id)
                
                request.session.modified = True
                # Keyingi bosqichga o'tish
                if step < 4:
                    return redirect(f"{reverse('survey:create')}?step={step + 1}")
            else:
                # Xato bor, formani qayta ko'rsatish
                pass
        
        elif action == 'prev' and step > 1:
            return redirect(f"{reverse('survey:create')}?step={step - 1}")
    
    # Oldingi bosqichlardan ma'lumotlarni yuklash
    initial_data = {}
    if step == 1 and 'interests' in survey_data:
        from .models import Interest
        initial_data['interests'] = Interest.objects.filter(id__in=survey_data['interests'])
    elif step == 2 and 'companion' in survey_data:
        from .models import Companion
        initial_data['companion'] = Companion.objects.get(id=survey_data['companion'])
    elif step == 3 and 'health' in survey_data:
        from .models import HealthCondition
        initial_data['health'] = HealthCondition.objects.filter(id__in=survey_data['health'])
    elif step == 4 and 'date' in survey_data:
        from datetime import datetime
        initial_data['date'] = datetime.fromisoformat(survey_data['date']).date()
    
    form = current_step['form_class'](initial=initial_data if initial_data else None)
    
    context = {
        'form': form,
        'step': step,
        'total_steps': 4,
        'current_step': current_step,
        'steps': steps,
        'survey_data': survey_data,
    }
    
    return render(request, 'survey/create.html', context)