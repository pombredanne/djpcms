from djpcms.utils import merge_dict
from djpcms.utils.const import *

from .base import HtmlWidget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput',
           'CheckboxInput',
           'TextArea',
           'Select',
           'List']

class TextInput(HtmlWidget):
    tag = 'input'
    inline = True
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'type':'text',
                                                    'value': None,
                                                    'name': None
                                                    })
    
class SubmitInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'submit'})
    
    
class HiddenInput(TextInput):
    is_hidden = True
    attributes = merge_dict(TextInput.attributes, {'type':'hidden'})
    
    
class PasswordInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'password'})
    

class CheckboxInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'checkbox'})
    
    def ischeckbox(self):
        return True
    
class TextArea(HtmlWidget):
    tag = 'textarea'
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'name': None,
                                                    'rows': 10,
                                                    'cols': 40
                                                    })
    
    
class Select(HtmlWidget):
    tag = 'select'
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    
    def __init__(self, **kwargs):
        super(Select,self).__init__(**kwargs)
        
    def inner(self, djp, field):
        return '\n'.join(self.render_options(djp, field))

    def render_options(self, djp, bfield):
        field = bfield.field
        choices,model = field.choices_and_model()
        selected_choices = []
        if bfield.value:
            selected_choices.append(bfield.value)
        option = self._option
        selected = self._selected
        if model:
            for val in choices:
                sel = (val in selected_choices) and selected or EMPTY
                yield option.format(val.id,sel,val)
        else:
            for val,des in choices:
                sel = (val in selected_choices) and selected or EMPTY
                yield option.format(val,sel,des)


class List(HtmlWidget,list):
    tag = 'ul'
    inline = False
    def __init__(self, data = None, **kwargs):
        HtmlWidget.__init__(self,**kwargs)
        if data:
            list.__init__(self, data)
        else:
            list.__init__(self)
    
    def inner(self):
        return '\n'.join((LI + elem + LIEND for elem in self))
    
    
