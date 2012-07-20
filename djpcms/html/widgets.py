from djpcms.media import js, Media
from djpcms.utils.text import escape, ispy3k, to_string

from .base import WidgetMaker, Widget
from .icons import with_icon
from . import classes

if ispy3k:
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest

__all__ = ['TextInput',
           'SubmitInput',
           'PasswordInput',
           'CheckboxInput',
           'TextArea',
           'Select',
           'FileInput',
           'List',
           'HiddenInput',
           'SelectWithAction',
           'DefinitionList',
           'anchor_or_button']


class FieldWidget(WidgetMaker):
    attributes = WidgetMaker.makeattr('value', 'name', 'disabled', 'readonly')
    
    def set_value(self, value, widget):
        widget.addAttr('value',value)
    

class InputWidget(FieldWidget):
    tag = 'input'
    inline = True
    attributes = FieldWidget.makeattr('type', 'placeholder')
    

class TextInput(InputWidget):
    default_attrs = {'type': 'text'}
    
    def media(self, request, widget):
        if widget.hasClass(classes.autocomplete):
            m = Media(js=['djpcms/autocomplete.js'])
            m += super(TextInput, self).media(request, widget)
        else:
            m = super(TextInput, self).media(request, widget)
        return m


class PasswordInput(InputWidget):
    default_attrs = {'type': 'password'}
    
    def set_value(self, value, widget):
        pass
    
    
class SubmitInput(InputWidget):
    classes = (classes.clickable, classes.button)
    default_attrs = {'type': 'submit'}
    
    
class HiddenInput(InputWidget):
    is_hidden = True
    default_attrs = {'type': 'hidden'}
    
    
class CheckboxInput(InputWidget):
    default_attrs = {'type': 'checkbox'}
    attributes = InputWidget.makeattr('type','checked')
    
    def set_value(self, value, widget):
        if value:
            widget.attrs['checked'] = 'checked'
    
    
class TextArea(InputWidget):
    tag = 'textarea'
    inline = False
    _value = ''
    default_attrs  = {'rows': 10, 'cols': 40}
    attributes = WidgetMaker.makeattr('name','rows','cols',
                                      'disabled','readonly')
    _media = Media(js=['djpcms/taboverride.js'])

    def set_value(self, value, widget):
        widget.add(escape(value))
        
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    attributes = WidgetMaker.makeattr('name', 'disabled', 'multiple', 'size')
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    _media = Media(js=['djpcms/jquery.bsmselect.js'])
    
    def set_value(self, val, widget):
        if val:
            if not widget.attr('multiple'):
                val = (val,)
            selected = tuple((to_string(v) for v in val))
        else:
            selected = ()
        widget.add(self._all_choices(widget, selected))
        
    def _all_choices(self, widget, selected):
        bfield =  widget.internal.get('bfield',None)
        if not bfield:
            return
        choices = bfield.field.choices
        option = self._option
        if not bfield.field.required:
            yield option.format('','',choices.empty_label)
        for id,val in choices.all(bfield):
            id = to_string(id)
            if id in selected:
                yield option.format(id,self._selected,val)
            else:
                yield option.format(id,'',val)
    
        
class FileInput(InputWidget):
    default_attrs = {'type': 'file'}
    attributes = InputWidget.makeattr('multiple')
    

class List(WidgetMaker):
    tag='ul'
    def add_to_widget(self, widget, elem, cn=None):
        if elem is not None:
            if not isinstance(elem, Widget) or elem.tag != 'li':
                elem = Widget('li', elem, cn=cn)
            widget._data_stream.append(elem)

#___________________________________________________ LIST DEFINITION
class DefinitionList(WidgetMaker):
    tag = 'dl'
    
    def add_to_widget(self, widget, elem):
        n = len(widget)
        tag = 'dt' if (n // 2)*2 == n else 'dd'
        return super(DefinitionList, self).add_to_widget(widget,
                                                         Widget(tag,elem))
        
        
for tag in ('div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5',
            'tr', 'th', 'td', 'table', 'thead', 'tbody', 'tfoot',
            'li', 'span', 'button', 'i', 'dt', 'dd'):
    WidgetMaker(tag=tag)
    

TextInput(default='input:text')
InputWidget(default='input:password')
SubmitInput(default='input:submit')
HiddenInput(default='input:hidden')
PasswordInput(default='input:password')
CheckboxInput(default='input:checkbox')
Select(default='select')
List(default='ul')
DefinitionList(default='dl')

def anchor_or_button(text, href=None, icon=None, asbutton=False, size=None,
                     **kwargs):
    w = Widget('a', text, href=href, **kwargs)
    if asbutton:
        w.addClass(classes.button)
    return with_icon(name=icon, size=size, widget=w)

def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()

