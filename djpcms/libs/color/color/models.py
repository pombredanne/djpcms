from djpcms import html, forms


COLOR_MEDIA = html.Media(js = ['color/js/colorpicker.js'])


class ColorInput(html.TextInput):
    default_style = 'color-picker'
    
    def media(self,*args):
        return COLOR_MEDIA
    
    
    
class ColorField(forms.CharField):
    widget = ColorInput()