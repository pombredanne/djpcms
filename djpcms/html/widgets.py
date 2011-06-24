from djpcms.utils import escape
from djpcms.utils.const import *
from .base import WidgetMaker, Widget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput',
           'CheckboxInput',
           'TextArea',
           'Select',
           'List',
           'SelectWithAction']

class FieldWidget(WidgetMaker):
    attributes = WidgetMaker.makeattr('value','name','title')
    
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
    

class InputWidget(WidgetMaker):
    tag = 'input'
    inline = True
    attributes = FieldWidget.makeattr('type')
    
    def get_value(self, value):
        if 'initial_value' in self.data:
            initial_value = self.data['initial_value']
            if isinstance(initial_value,list):
                return ', '.join(initial[1] for initial in initial_value)
            else:
                return initial_value
        else:
            return value
    
class TextInput(InputWidget):
    default_attrs = {'type': 'text'}


class PasswordInput(InputWidget):
    default_attrs = {'type': 'password'}
    
    
class SubmitInput(InputWidget):
    default_attrs = {'type': 'submit'}
    
    
class HiddenInput(InputWidget):
    is_hidden = True
    default_attrs = {'type': 'hidden'}
    
    
class CheckboxInput(InputWidget):
    default_attrs = {'type':'checkbox'}
    attributes = InputWidget.makeattr('type','checked')
    
    def get_value(self, val):
        if val:
            self.attrs['checked'] = 'checked'
        
    def ischeckbox(self):
        return True
    
    
class TextArea(InputWidget):
    tag = 'textarea'
    inline = False
    _value = ''
    default_attrs  = {'rows': 10, 'cols': 40}
    attributes = WidgetMaker.makeattr('name','rows','cols')

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



WidgetMaker('div', default = 'div')
WidgetMaker('th', default = 'th')
WidgetMaker('tr', default = 'tr')
WidgetMaker('ul', default = 'ul')
WidgetMaker('a', default = 'a', attributes = ('href','title'))
TextInput(default='input:text')
InputWidget(default='input:password')
SubmitInput(default='input:submit')
HiddenInput(default='input:hidden')
PasswordInput(default='input:password')


class List(Widget, list):
    def __init__(self, data = None, **kwargs):
        super(List,self).__init__('ul',**kwargs)
        list.__init__(self,data) if data else list.__init__(self)
        
    def inner(self, djp):
        return '\n'.join((LI + elem + LIEND for elem in self))
    
    
def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()
