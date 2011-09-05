from djpcms import sites
from djpcms.utils import escape, js, media, gen_unique_id
from djpcms.utils.const import *

from .base import WidgetMaker, Widget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput',
           'CheckboxInput',
           'TextArea',
           'Select',
           'FileInput',
           'ListWidget',
           'List',
           'SelectWithAction',
           'TextSelect',
           'DefinitionList']


class FieldWidget(WidgetMaker):
    attributes = WidgetMaker.makeattr('value','name','disabled')
    
    def set_value(self, value, widget):
        widget.addAttr('value',value)
    

class InputWidget(FieldWidget):
    tag = 'input'
    inline = True
    attributes = FieldWidget.makeattr('type')
    
        
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
        
    def inner(self, djp, widget, keys):
        return widget.internal['value']
    
    def media(self, djp = None):
        return self.area_media
    
    
class Select(FieldWidget):
    tag = 'select'
    inline = False
    attributes = WidgetMaker.makeattr('name','disabled','multiple','size')
    _option = '<option value="{0}"{1}>{2}</option>'
    _selected = ' selected="selected"'
    select_media = media.Media(js = ['djpcms/jquery.bsmselect.js'])
    
    def __init__(self, choices = None, **kwargs):
        self.choices = choices
        super(Select,self).__init__(**kwargs)
    
    def set_value(self, val, widget):
        bfield =  widget.internal.get('bfield',None)
        if bfield:
            field = bfield.field
            choices, model = field.choices_and_model(bfield)
            widget.internal['model'] = model
            widget.internal['choices'] = choices
        if val:
            selected_choices = val if widget.attr('multiple') else (val,)
        else:
            selected_choices = ()
        widget.internal['selected_choices'] = selected_choices

    def inner(self, djp, widget, keys):
        return '\n'.join(self.render_options(djp, widget))
    
    def render_options(self, djp, widget):
        selected_choices = widget.internal.get('selected_choices',())
        model = widget.internal.get('model',None)
        choices = widget.internal.get('choices',self.choices) or ()
        option = self._option
        selected = self._selected
        if model:
            field = widget.internal['bfield'].field
            if field and not field.required:
                yield option.format('','',field.empty_label)
            for val in choices:
                sel = (val in selected_choices) and selected or EMPTY
                yield option.format(val.id,sel,val)
        elif choices:
            for val,des in choices:
                sel = (val in selected_choices) and selected or EMPTY
                yield option.format(val,sel,des)
        else:
            raise StopIteration

    def media(self, djp = None):
        return self.select_media
        
        
class FileInput(InputWidget):
    default_attrs = {'type': 'file'}
    attributes = InputWidget.makeattr('multiple')
        
        
for tag in ('div','p','h1','h2','h3','h4','h5','th','li','tr','span','button'):
    WidgetMaker(tag = tag)
    
    
WidgetMaker(tag = 'a', default = 'a', attributes = ('href','title'))
TextInput(default='input:text')
InputWidget(default='input:password')
SubmitInput(default='input:submit')
HiddenInput(default='input:hidden')
PasswordInput(default='input:password')
CheckboxInput(default='input:checkbox')
Select()


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


class TextSelect(object):

    def __init__(self, choices, html, **kwargs):
        '''If no htmlid is provided, a new widget containing the target html
    is created and data is an iterable over three elements tuples.'''
        htmlid = gen_unique_id()[:8]
        self.select = Widget('select', choices = choices, cn = 'text-select')\
                    .addData('target','#{0}'.format(htmlid))
        self.html = '\n'.join((Widget('div', cn = '{0} target'.format(name))\
                          .render(inner=body) for name,body in html))
        self.target = Widget('div',id=htmlid).render(inner=html)
        
    def render(self, djp = None):
        return '\n'.join((self.select.render(),self.target))
    