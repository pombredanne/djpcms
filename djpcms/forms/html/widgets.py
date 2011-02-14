from djpcms.utils import merge_dict

from .base import HtmlWidget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput',
           'CheckboxInput',
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
    
    
class Select(HtmlWidget):
    tag = 'select'
    
    def __init__(self, **kwargs):
        super(Select,self).__init__(**kwargs)
        
    def inner(self, djp, field):
        return '\n'.join(self.render_options(djp, field))

    def render_options(self, djp, field):
        choices = field.field.choices
        selected_choices = []
        if hasattr(choices,'__call__'):
            choices = choices()
        for val,des in choices:
            sel = (val in selected_choices) and ' selected="selected"' or ''
            yield '<option value="{0}"{1}>{2}</option>'.format(val,sel,des)


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
        return '\n'.join(('<li>' + elem + '</li>' for elem in self))
    
    
