from djpcms import html, forms
from djpcms.media import Media, js


class ColorInput(html.TextInput):
    classes = 'color-picker'
    _media = Media(js=[js.RAPHAEL, 'color/color.js'])
    
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
    