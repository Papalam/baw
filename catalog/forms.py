from django import forms
from .models import Dealership
from .widgets import YandexMapWidget


class CoordinatesField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            forms.DecimalField(max_digits=9, decimal_places=6, required=False),
            forms.DecimalField(max_digits=9, decimal_places=6, required=False),
        )
        super().__init__(
            fields=fields,
            widget=YandexMapWidget(),
            required=False,
            *args, **kwargs
        )

    def compress(self, data_list):
        if data_list:
            return {'latitude': data_list[0], 'longitude': data_list[1]}
        return None


class DealershipAdminForm(forms.ModelForm):
    coordinates = CoordinatesField(label='Координаты на карте')

    class Meta:
        model = Dealership
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['coordinates'].initial = {
                'latitude': self.instance.latitude,
                'longitude': self.instance.longitude,
            }

    def save(self, commit=True):
        instance = super().save(commit=False)
        coords = self.cleaned_data.get('coordinates')
        if coords:
            instance.latitude = coords.get('latitude')
            instance.longitude = coords.get('longitude')
        if commit:
            instance.save()
        return instance
