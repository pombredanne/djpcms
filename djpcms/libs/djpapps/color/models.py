from djpcms import html, forms
from djpcms.utils import media


COLOR_MEDIA = media.Media(js = ['color/js/colorpicker.js',
                                'color/color.js'])


class ColorInput(html.TextInput):
    default_style = 'color-picker'
    
    def set_value(self, value, widget):
        if value and value.startswith('#'):
            value = value[1:]
        widget.addAttr('value',value)
        
    def media(self,djp=None):
        return COLOR_MEDIA
    
    
    
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
    