from djpcms.utils import merge_dict, escape
from djpcms.utils.const import *
from .base import HtmlWidget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput',
           'CheckboxInput',
           'TextArea',
           'Select',
           'List',
           'SelectWithAction']


class FieldWidget(HtmlWidget):
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'value': None,
                                                    'name': None
                                                    })
    
    def render(self, djp = None, bfield = None):
        if bfield:
            attrs = self.attrs
            attrs['id'] = bfield.id
            attrs['name'] = bfield.html_name
            if bfield.title:
                attrs['title'] = bfield.title
            value = self.get_value(bfield.value)
            attrs['value'] = value
        return super(FieldWidget,self).render(djp,bfield)
    
    def get_value(self, value):
        return value
    

class TextInput(FieldWidget):
    tag = 'input'
    inline = True
    attributes = merge_dict(FieldWidget.attributes, {'type':'text'})
    
    
class SubmitInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'submit'})
    
    
class HiddenInput(TextInput):
    is_hidden = True
    attributes = merge_dict(TextInput.attributes, {'type':'hidden'})
    
    
class PasswordInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'password'})
    

class CheckboxInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'checkbox'})
    
    def get_value(self, val):
        if val:
            self.attrs['checked'] = 'checked'
        
    def ischeckbox(self):
        return True
    
    
class TextArea(TextInput):
    tag = 'textarea'
    inline = False
    _value = ''
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'name': None,
                                                    'rows': 10,
                                                    'cols': 40
                                                    })

    def get_value(self, value):
        self._value = escape(value)
        
    def inner(self, *args, **kwargs):
        return self._value
    
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    
    def __init__(self, choices = None, **kwargs):
        self.choices = choices
        super(Select,self).__init__(**kwargs)
        
    def get_value(self, val):
        pass
    
    def inner(self, djp, bfield = None):
        return '\n'.join(self.render_options(djp, bfield))

    def render_options(self, djp, bfield):
        selected_choices = []
        if bfield:
            field = bfield.field
            choices,model = field.choices_and_model(bfield)
            if bfield.value:
                selected_choices.append(bfield.value)
        else:
            choices,model = self.choices,None
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
    
    
def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()