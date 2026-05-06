from django import forms
from django.utils import timezone
from .models import TravelBuddyPost, BuddyRequest
from apps.locations.models import Location


class TravelBuddyPostForm(forms.ModelForm):
    """Hamroh post yaratish formasi"""
    
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Joyni tanlang'
        })
    )
    
    class Meta:
        model = TravelBuddyPost
        fields = [
            'location',
            'travel_date',
            'people_needed',
            'preferred_group',
            'budget_from',
            'budget_to',
            'transport_type',
            'note'
        ]
        widgets = {
            'travel_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().date().isoformat()
            }),
            'people_needed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'preferred_group': forms.Select(attrs={
                'class': 'form-control'
            }),
            'budget_from': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Min budjet',
                'min': '0',
                'step': '0.01'
            }),
            'budget_to': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Max budjet',
                'min': '0',
                'step': '0.01'
            }),
            'transport_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Qisqa izoh yozing...'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        budget_from = cleaned_data.get('budget_from')
        budget_to = cleaned_data.get('budget_to')
        
        # Sana tekshirish
        if travel_date and travel_date < timezone.now().date():
            raise forms.ValidationError("Sana o'tib ketgan bo'lmasin!")
        
        # Budget tekshirish
        if budget_from and budget_to and budget_from > budget_to:
            raise forms.ValidationError("Minimum budjet maksimumdan katta bo'lmasin!")
        
        return cleaned_data


class BuddyRequestForm(forms.ModelForm):
    """Hamroh request formasi"""
    
    class Meta:
        model = BuddyRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Salom! Men sizning hamrohingiz bo\'lishga qiziqaman...',
                'maxlength': '500'
            })
        }


class TravelBuddyFilterForm(forms.Form):
    """Filter formasi"""
    
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Joyni tanlang'
        })
    )
    
    travel_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    travel_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    preferred_group = forms.ChoiceField(
        required=False,
        choices=[('', 'Barchasi')] + TravelBuddyPost.PREFERRED_GROUP_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    transport_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Ixtiyoriy')] + TravelBuddyPost.TRANSPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    budget_from = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min budjet',
            'min': '0',
            'step': '0.01'
        })
    )
    
    budget_to = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max budjet',
            'min': '0',
            'step': '0.01'
        })
    )
