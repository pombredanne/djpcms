from djpcms import html, forms
from djpcms.utils import media


COLOR_MEDIA = media.Media(js = ['color/js/colorpicker.js',
                                'color/color.js'])


class ColorInput(html.TextInput):
    default_style = 'color-picker'
    
    def media(self,djp=None):
        return COLOR_MEDIA
    
    
    
class ColorField(forms.CharField):
    widget = ColorInput()