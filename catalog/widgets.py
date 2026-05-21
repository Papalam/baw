from django import forms
from django.utils.html import format_html


class YandexMapWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [forms.HiddenInput(), forms.HiddenInput()]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.get('latitude'), value.get('longitude')]
        return [None, None]

    def render(self, name, value, attrs=None, renderer=None):
        print(f"YandexMapWidget.render() called: name={name}, value={value}")
        if not isinstance(value, list):
            value = self.decompress(value)
        lat_val = value[0] or ''
        lon_val = value[1] or ''
        id_prefix = (attrs.get('id', name) if attrs else name)

        coords_text = (
            f'Широта: {lat_val}, Долгота: {lon_val}'
            if lat_val and lon_val
            else 'Координаты не заданы'
        )

        return format_html('''
            <div class="yandex-map-container">
                <div class="ymap-search-row">
                    <input type="text" class="ymap-search" placeholder="Введите адрес для поиска...">
                    <button type="button" class="ymap-search-btn">Найти</button>
                    <button type="button" class="ymap-clear-btn">Очистить</button>
                </div>
                <div class="ymap-canvas"></div>
                <div class="ymap-coords-display">{coords_text}</div>
                <input type="hidden" name="{name}_0" value="{lat}" class="ymap-lat" id="{id}_0">
                <input type="hidden" name="{name}_1" value="{lon}" class="ymap-lon" id="{id}_1">
            </div>
        ''',
            name=name, lat=lat_val, lon=lon_val,
            id=id_prefix, coords_text=coords_text
        )

    class Media:
        css = {'all': ('admin/css/yandex_map_widget.css',)}
        js = ('admin/js/yandex_map_widget.js',)
