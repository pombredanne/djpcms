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
           'ListWidget',
           'List',
           'SelectWithAction']


class FieldWidget(WidgetMaker):
    attributes = WidgetMaker.makeattr('value','name','title')
    
    def widget(self, bfield = None, **kwargs):
        w = super(FieldWidget,self).widget(bfield = bfield,**kwargs)
        if bfield:
            attrs = w.attrs
            attrs['id'] = bfield.id
            attrs['name'] = bfield.html_name
            if bfield.title:
                attrs['title'] = bfield.title
            self.get_value(bfield.value, w)
        return w
    
    def get_value(self, value, widget):
        widget.addAttr('value',value)
    

class InputWidget(FieldWidget):
    tag = 'input'
    inline = True
    attributes = FieldWidget.makeattr('type')
    
    def get_value(self, value, widget):
        if 'initial_value' in widget.data:
            initial_value = widget.data['initial_value']
            if isinstance(initial_value,list):
                value = ', '.join(initial[1] for initial in initial_value)
            else:
                value = initial_value
        widget.addAttr('value',value)
        
    
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
    
    def get_value(self, value, widget):
        if value:
            widget.attrs['checked'] = 'checked'
        
    def ischeckbox(self):
        return True
    
    
class TextArea(InputWidget):
    tag = 'textarea'
    inline = False
    _value = ''
    default_attrs  = {'rows': 10, 'cols': 40}
    attributes = WidgetMaker.makeattr('name','rows','cols')

    def get_value(self, value, widget):
        widget.internal['value'] = escape(value)
        
    def inner(self, djp, widget, keys):
        return widget.internal['value']
    
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    
    def __init__(self, choices = None, **kwargs):
        self.choices = choices
        super(Select,self).__init__(**kwargs)
        
    def get_value(self, val, widget):
        pass
    
    def inner(self, djp, widget, keys):
        return '\n'.join(self.render_options(djp, widget.internal['bfield']))

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



WidgetMaker(tag = 'div', default = 'div')
WidgetMaker(tag = 'th', default = 'th')
WidgetMaker(tag = 'tr', default = 'tr')
WidgetMaker(tag = 'span', default = 'span')
WidgetMaker(tag = 'a', default = 'a', attributes = ('href','title'))
WidgetMaker(tag = 'button', default = 'button')
TextInput(default='input:text')
InputWidget(default='input:password')
SubmitInput(default='input:submit')
HiddenInput(default='input:hidden')
PasswordInput(default='input:password')

class ListWidget(WidgetMaker):
    tag='ul'
    def inner(self, djp, widget, keys):
        return '\n'.join((LI + elem + LIEND for elem in widget))

class List(Widget, list):
    maker = ListWidget()
    def __init__(self, data = None, **kwargs):
        super(List,self).__init__(tag='ul',**kwargs)
        list.__init__(self,data) if data else list.__init__(self)
    
    def addanchor(self, href, text):
        if href:
            a = "<a href='{0}'>{1}</a>".format(href,text)
            self.append(a)
    
    
ListWidget(default = 'ul', widget = List)
    
def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()
