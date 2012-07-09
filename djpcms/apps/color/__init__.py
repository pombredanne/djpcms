'''Color picker application from

https://github.com/vanderlee/colorpicker

MIT License
'''
from djpcms import html, forms, media


class ColorInput(html.TextInput):
    classes = 'color-picker span2'
    _media = media.Media(
                js=['color/colorpicker/jquery.colorpicker.js',
                    'color/colorpicker/i18n/jquery.ui.colorpicker-en.js',
                    'color/color.js'])
    
    def set_value(self, value, widget):
        if value and value.startswith('#'):
            value = value[1:]
        widget.addAttr('value',value)    
    
    
class ColorField(forms.CharField):
    widget = ColorInput()
    
    def _clean(self, value, bfield):
        if value and not value.startswith('#'):
            try:
                int(value,16)
                value = '#{0}'.format(value)
            except ValueError:
                pass
        return value
    