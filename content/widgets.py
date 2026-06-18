from django import forms
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy


class RichTextEditorWidget(forms.Textarea):
    """CKEditor 4 виджет для Django админки"""

    class Media:
        js = ('ckeditor/ckeditor.js',)
        css = {'all': ('ckeditor/contents.css',)}

    def __init__(self, attrs=None):
        super().__init__(attrs={'rows': 25, 'cols': 80})

    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs)
        upload_url = reverse_lazy('ckeditor_upload')
        script = f"""
<script>
(function() {{
    function getCsrfToken() {{
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }}

    if (!CKEDITOR.plugins.registered['djangoImageUpload']) {{
        CKEDITOR.plugins.add('djangoImageUpload', {{
            init: function(editor) {{
                editor.addCommand('djangoImageUpload', {{
                    exec: function(editor) {{
                        var input = document.createElement('input');
                        input.type = 'file';
                        input.accept = 'image/jpeg,image/png';
                        input.onchange = function() {{
                            var file = input.files[0];
                            if (!file) return;
                            var formData = new FormData();
                            formData.append('upload', file);
                            fetch('{upload_url}', {{
                                method: 'POST',
                                headers: {{'X-CSRFToken': getCsrfToken()}},
                                body: formData,
                                credentials: 'same-origin'
                            }})
                            .then(function(r) {{
                                if (!r.ok) {{
                                    return r.text().then(function(t) {{ throw new Error('HTTP ' + r.status + ': ' + t.substring(0, 200)); }});
                                }}
                                return r.json();
                            }})
                            .then(function(data) {{
                                if (data.url) {{
                                    editor.focus();
                                    setTimeout(function() {{
                                        var img = editor.document.createElement('img');
                                        img.setAttribute('src', data.url);
                                        editor.insertElement(img);
                                    }}, 50);
                                }} else {{
                                    alert('Ошибка загрузки: ' + (data.error || 'неизвестная ошибка'));
                                }}
                            }})
                            .catch(function(err) {{
                                alert('Ошибка: ' + err.message);
                            }});
                        }};
                        input.click();
                    }}
                }});
                editor.ui.addButton('DjangoImageUpload', {{
                    label: 'Загрузить изображение',
                    command: 'djangoImageUpload',
                    icon: 'data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="1" y="2" width="14" height="11" rx="1.5" fill="none" stroke="%23555" stroke-width="1.2"/><circle cx="5.5" cy="6" r="1.5" fill="%23555"/><polyline points="1,13 5,9 8,11.5 11,8 15,13" fill="none" stroke="%23555" stroke-width="1.2"/><line x1="10" y1="1" x2="10" y2="5" stroke="%23555" stroke-width="1.2"/><polyline points="8,3 10,1 12,3" fill="none" stroke="%23555" stroke-width="1.2"/></svg>',
                    toolbar: 'insert,10'
                }});
            }}
        }});
    }}

    var el = document.querySelector('[name="{name}"]');
    if (!el) return;
    CKEDITOR.replace(el, {{
        extraPlugins: 'djangoImageUpload',
        allowedContent: true,
        toolbar: [
            {{ name: 'document', items: ['Source'] }},
            {{ name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'] }},
            {{ name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll'] }},
            '/',
            {{ name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] }},
            {{ name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] }},
            {{ name: 'links', items: ['Link', 'Unlink'] }},
            {{ name: 'insert', items: ['DjangoImageUpload', 'Table', 'HorizontalRule', 'SpecialChar'] }},
            '/',
            {{ name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] }},
            {{ name: 'colors', items: ['TextColor', 'BGColor'] }},
        ],
    }});
}})();
</script>"""
        return mark_safe(output + script)
