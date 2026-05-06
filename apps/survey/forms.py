from django import forms
from .models import Survey, Interest, Companion, HealthCondition

class Step1InterestsForm(forms.Form):
    """1-bosqich: Qiziqishlarni tanlash"""
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='🎯 Qiziqishlaringiz',
        help_text='Bir nechta variant tanlashingiz mumkin',
        error_messages={
            'required': 'Iltimos, kamita bitta qiziqishni tanlang!'
        }
    )

class Step2CompanionForm(forms.Form):
    """2-bosqich: Kim bilan sayohat qilish"""
    companion = forms.ModelChoiceField(
        queryset=Companion.objects.all(),
        widget=forms.RadioSelect(),
        label='👥 Kim bilan sayohat qilasiz?',
        error_messages={
            'required': 'Iltimos, variantni tanlang!'
        }
    )

class Step3HealthForm(forms.Form):
    """3-bosqich: Sog'liq holati"""
    health = forms.ModelMultipleChoiceField(
        queryset=HealthCondition.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='🏥 Sog\'liq holatingiz',
        help_text='Agar muammo bo\'lmasa, bo\'sh qoldiring',
        required=False
    )

class Step4DateForm(forms.Form):
    """4-bosqich: Sayohat sanasi"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='📅 Sayohat sanasi',
        help_text='Format: YYYY-MM-DD (masalan: 2026-12-31)',
        error_messages={
            'required': 'Iltimos, sayohat sanasini kiriting!',
            'invalid': 'Sanani to\'g\'ri formatda kiriting!'
        }
    )
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        from datetime import date as today_date
        if date and date < today_date.today():
            raise forms.ValidationError('Sayohat sanasi kelajakdagi sana bo\'lishi kerak!')
        return date

class SurveyForm(forms.ModelForm):
    """Yakuniy forma - barcha ma'lumotlarni saqlash"""
    class Meta:
        model = Survey
        fields = ['interests', 'companion', 'health', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'interests': forms.CheckboxSelectMultiple(),
            'health': forms.CheckboxSelectMultiple(),
            'companion': forms.Select(),
        }