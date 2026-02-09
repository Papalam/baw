from django import forms
from django.utils.safestring import mark_safe


class RichTextEditorWidget(forms.Textarea):
    """CKEditor 4 виджет для Django админки"""

    class Media:
        js = ('ckeditor/ckeditor.js',)
        css = {'all': ('ckeditor/contents.css',)}

    def __init__(self, attrs=None):
        super().__init__(attrs={
            'rows': 25,
            'cols': 80,
            'class': 'ckeditor'
        })

    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs)
        return mark_safe(output)
        # JS автоматически подключается через class='ckeditor'
