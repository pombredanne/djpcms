from djpcms.utils import escape, js, media

from .base import WidgetMaker, Widget


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
        
    def ischeckbox(self):
        return True
    
    
class TextArea(InputWidget):
    tag = 'textarea'
    inline = False
    _value = ''
    default_attrs  = {'rows': 10, 'cols': 40}
    attributes = WidgetMaker.makeattr('name','rows','cols',
                                      'disabled','readonly')
    area_media = media.Media(js = ['djpcms/taboverride.js'])

    def set_value(self, value, widget):
        widget.internal['value'] = escape(value)
        
    def inner(self, request, widget, keys):
        return widget.internal['value']
    
    def media(self, request = None):
        return self.area_media
    
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    wrapper_class = 'field-widget select ui-widget-content'
    attributes = WidgetMaker.makeattr('name','disabled','multiple','size')
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    select_media = media.Media(js = ['djpcms/jquery.bsmselect.js'])
    
    def set_value(self, val, widget):
        bfield =  widget.internal.get('bfield',None)
        if bfield:
            choices = bfield.field.choices
            for c in choices.all(bfield):
                 widget.add(c)
            val = choices.widget_value(val)
        if val:
            selected_choices = val if widget.attr('multiple') else (val,)
        else:
            selected_choices = ()
        widget.internal['selected_choices'] = selected_choices

    def stream(self, request, widget, context):
        selected_choices = widget.internal.get('selected_choices',())
        option = self._option
        selected = self._selected
        if 'bfield' in widget.internal:
            bfield = widget.internal['bfield']
            field = bfield.field
            choices =  field.choices
            selected = self._selected
            if not field.required:
                yield option.format('','',choices.empty_label)
        for id,val in widget.data_stream:
            sel = (id in selected_choices) and selected or ''
            yield option.format(id,sel,val)

    def media(self, request = None):
        return self.select_media
        
        
class FileInput(InputWidget):
    default_attrs = {'type': 'file'}
    attributes = InputWidget.makeattr('multiple')
        
        
for tag in ('div','p','h1','h2','h3','h4','h5','th','td',
            'li','tr','span','button'):
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
        if not isinstance(elem,Widget) or elem.tag != 'li':
            elem = Widget('li', elem, cn = cn)
        widget.data_stream.append(elem)
    

List(default = 'ul')


#___________________________________________________ LIST DEFINITION
class DefinitionListMaker(WidgetMaker):
    tag = 'div'
    
    def data2html(self, request, data):
        return '<dl><dt>{0}</dt><dd>{1}</dd></dl>'.format(*data)
    

class DefinitionList(Widget):
    maker = DefinitionListMaker()


    
def SelectWithAction(choices, action_url, **kwargs):
    a = HtmlWidget('a', cn = 'djph select-action').addAttr('href',action_url)
    s = Select(choices = choices, **kwargs).addClass('ajax actions')
    return a.render()+s.render()

