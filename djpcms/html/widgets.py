from djpcms.utils import escape, js, media, ispy3k, to_string

from .base import WidgetMaker, Widget

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
           'DefinitionList']


class FieldWidget(WidgetMaker):
    wrapper_class = None
    attributes = WidgetMaker.makeattr('value','name','disabled','readonly')
    
    def set_value(self, value, widget):
        widget.addAttr('value',value)
    

class InputWidget(FieldWidget):
    tag = 'input'
    inline = True
    wrapper_class = 'field-widget input ui-widget-content'
    attributes = FieldWidget.makeattr('type','placeholder')
    

class TextInput(InputWidget):
    default_attrs = {'type': 'text'}


class PasswordInput(InputWidget):
    default_attrs = {'type': 'password'}
    
    def set_value(self, value, widget):
        pass
    
    
class SubmitInput(InputWidget):
    classes = 'button'
    default_attrs = {'type': 'submit'}
    
    
class HiddenInput(InputWidget):
    is_hidden = True
    default_attrs = {'type': 'hidden'}
    
    
class CheckboxInput(InputWidget):
    wrapper_class = None
    default_attrs = {'type':'checkbox'}
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
    _media = media.Media(js = ['djpcms/taboverride.js'])

    def set_value(self, value, widget):
        widget.add(escape(value))
        
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    wrapper_class = 'field-widget select ui-widget-content'
    attributes = WidgetMaker.makeattr('name','disabled','multiple','size')
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    _media = media.Media(js = ['djpcms/jquery.bsmselect.js'])
    
    def set_value(self, val, widget):
        if val:
            selected = tuple((to_string(val) for v in\
                               (val if widget.attr('multiple') else (val,))))
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
        
        
for tag in ('div','p','h1','h2','h3','h4','h5','th','td',
            'li','tr','span','button','i','dt', 'dd'):
    WidgetMaker(tag = tag)
    
    
WidgetMaker(tag = 'a', default = 'a', attributes = ('href','title'))
WidgetMaker(tag = 'table', default = 'table')
TextInput(default='input:text')
InputWidget(default='input:password')
SubmitInput(default='input:submit')
HiddenInput(default='input:hidden')
PasswordInput(default='input:password')
CheckboxInput(default='input:checkbox')
Select(default='select')


class List(WidgetMaker):
    tag='ul'
    def add_to_widget(self, widget, elem, cn = None):
        if elem is not None:
            if not isinstance(elem, Widget) or elem.tag != 'li':
                elem = Widget('li', elem, cn = cn)
            widget._data_stream.append(elem)
    

List(default = 'ul')


#___________________________________________________ LIST DEFINITION
class DefinitionList(WidgetMaker):
    tag = 'dl'
    
    def add_to_widget(self, widget, elem, cn = None):
        if hasattr(elem,'__iter__'):
            tags = ('dt', 'dd')
            for n,data in enumerate(zip_longest(tags, elem, fillvalue='')):
                if n > 1:
                    break
                widget._data_stream.append(Widget(*data))
    

    
def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()

