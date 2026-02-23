from django import forms
from .models import CarApplication, Configuration, Color


class CarApplicationForm(forms.ModelForm):
    class Meta:
        model = CarApplication
        fields = [
            'configuration',
            'outside_color',
            'inside_color',
            'dealer',
            'first_name',
            'last_name',
            'phone',
            'comment',
            'agreement'
        ]
