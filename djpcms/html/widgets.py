from djpcms.utils import escape
from djpcms.utils.const import *

from .base import WidgetMaker, Widget
from .media import Media


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput',
           'CheckboxInput',
           'TextArea',
           'Select',
           'ListWidget',
           'List',
           'SelectWithAction',
           'TextSelect',
           'DefinitionList']


class FieldWidget(WidgetMaker):
    attributes = WidgetMaker.makeattr('value','name','disabled')
    
    def widget(self, bfield = None, **kwargs):
        w = super(FieldWidget,self).widget(bfield = bfield,**kwargs)
        if bfield:
            attrs = w.attrs
            attrs['id'] = bfield.id
            attrs['name'] = bfield.html_name
            if bfield.help_text:
                attrs['title'] = bfield.help_text
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
    attributes = WidgetMaker.makeattr('name','rows','cols',
                                      'disabled','readonly')
    area_media = Media(js = ['djpcms/taboverride.js'])

    def get_value(self, value, widget):
        widget.internal['value'] = escape(value)
        
    def inner(self, djp, widget, keys):
        return widget.internal['value']
    
    def media(self, *args):
        return self.area_media
    
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    attributes = WidgetMaker.makeattr('name','disabled','multiple','size')
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    select_media = Media(js = ['djpcms/jquery.bsmselect.js'])
    
    def __init__(self, choices = None, **kwargs):
        self.choices = choices
        super(Select,self).__init__(**kwargs)
        
    def get_value(self, val, widget):
        pass
    
    def inner(self, djp, widget, keys):
        return '\n'.join(self.render_options(djp, widget.internal['bfield']))

    def render_options(self, djp, bfield):
        selected_choices = []
        field = None
        if bfield:
            field = bfield.field
            choices,model = field.choices_and_model(bfield)
            values = bfield.value
            if values:
                if not field.multiple:
                    values = (values,)
                for value in values:
                    selected_choices.append(value)
        else:
            choices,model = self.choices,None
        option = self._option
        selected = self._selected
        if model:
            if field and not field.required:
                yield option.format('','',field.empty_label)
            for val in choices:
                sel = (val in selected_choices) and selected or EMPTY
                yield option.format(val.id,sel,val)
        else:
            for val,des in choices:
                sel = (val in selected_choices) and selected or EMPTY
                yield option.format(val,sel,des)

    def media(self, widget):
        if 'multiple' in widget.attrs:
            return self.select_media

for tag in ('div','p','h1','h2','h3','h4','h5','th','li','tr','span','button'):
    WidgetMaker(tag = tag)
    
    
WidgetMaker(tag = 'a', default = 'a', attributes = ('href','title'))
TextInput(default='input:text')
InputWidget(default='input:password')
SubmitInput(default='input:submit')
HiddenInput(default='input:hidden')
PasswordInput(default='input:password')
CheckboxInput(default='input:checkbox')


class ListWidget(WidgetMaker):
    tag='ul'
    def inner(self, djp, widget, keys):
        return '\n'.join(widget._list)


class List(Widget):
    maker = ListWidget()
    def __init__(self, data = None, li_class = None, **kwargs):
        self._list = []
        self.li_class = li_class
        super(List,self).__init__(tag='ul',**kwargs)
        if data:
            for d in data:
                self.append(d)
    
    def addanchor(self, href, text):
        if href:
            a = "<a href='{0}'>{1}</a>".format(href,text)
            self.append(a)
            
    def append(self, elem, cn = None):
        elem = Widget('li', cn = self.li_class).render(inner = elem)
        self._list.append(elem)
    
    
ListWidget(default = 'ul', widget = List)


#___________________________________________________ LIST DEFINITION
class DefinitionListMaker(WidgetMaker):
    tag = 'div'
    
    def data2html(self, data):
        return '<dl><dt>{0}</dt><dd>{1}</dd></dl>'.format(*data)
    

class DefinitionList(Widget):
    maker = DefinitionListMaker()


    
def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()


class TextSelect(WidgetMaker):
    tag = 'div'
    default_class = 'text-select'
    
    def __init__(self, data, empty_label = None, **kwargs):
        super(TextSelect,self).__init__(**kwargs)
        choices = []
        text = []
        initial = None
        if empty_label:
            initial = ''
            choices.append(('',empty_label))
        for name,value,body in data:
            if initial is None:
                initial = name
            choices.append((name,value))
            text.append((name,body))
        self.add(Select(choices=choices))
        self.initial = initial
        self.body = text
    
    def stream(self, djp, widget, context):
        for child in context['children']:
            yield child
        for name,body in self.body:
            yield Widget(maker='div',
                         cn = '{0} target'.format(name))\
                        .render(inner = body)
    
        