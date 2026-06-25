from django import forms
from .models import CarApplication, Configuration, Color, CallbackRequest, TestDriveRequest


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


class ContactForm(forms.ModelForm):
    """Форма заказа обратного звонка"""
    class Meta:
        model = CallbackRequest
        fields = [
            'name',
            'phone',
            'comment'
        ]


class TestDriveForm(forms.ModelForm):
    """Форма заявки на тест-драйв"""
    class Meta:
        model = TestDriveRequest
        fields = [
            'first_name',
            'last_name',
            'phone',
            'desired_date',
            'desired_time',
            'comment',
            'consent',
        ]