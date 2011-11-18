'''\
This module complements the django forms library by adding ajax functionality,
inline forms, and custom layout based on uni-form_ style.

Using uniforms to render form is easy::

    from djpcms import forms
    from djcms.forms.layout.uniforms import Layout, Fieldset, blockLabels2
    
    class MyForm(forms.Form):
        name = forms.CharField()

    HtmlMyForm = forms.HtmlForm(
       MyForm,
       layout = Layout(Fieldset('name'))
    )


There are three types of layout:

* ``inlineLabels``
* ``blockLabels``
* ``blockLabels2`` (default)   

.. _uni-form: http://sprawsm.com/uni-form/
'''
from djpcms import html

from .base import FormLayout, FormLayoutElement, SubmitElement, check_fields,\
                    nolabel
from .tablefield import TableRelatedFieldset


inlineLabels   = 'inlineLabels'
inlineLabels2  = 'inlineLabels fullwidth'
inlineLabels3  = 'inlineLabels auto'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'


WIDGET_CLASSES = {'CharField': 'textInput',
                  'DateField': 'dateInput'}


class UniFormElement(FormLayoutElement):
    default_class = 'ctrlHolder'
    
    def add_widget_classes(self, field, widget):
        cls = field.field.__class__.__name__
        if cls in WIDGET_CLASSES:
            widget.addClass(WIDGET_CLASSES[cls])


class Fieldset(UniFormElement):
    '''A :class:`FormLayoutElement` which renders to a <fieldset>.'''
    tag = 'fieldset'
    def __init__(self, *children, **kwargs):
        super(Fieldset,self).__init__(**kwargs)
        self.allchildren = children
    
    def check_fields(self, missings, layout):
        self.allchildren = check_fields(self.allchildren,missings,layout)
      

class Row(Fieldset):
    '''A :class:`FormLayoutElement` which renders to a <div>.'''
    tag = 'div'
    elem_css = "formRow"
    

class Columns(UniFormElement):
    '''A :class:`FormLayoutElement` whiche defines a set of columns. Renders to a set of <div>.'''
    elem_css = "formColumn"
    template = None
    template_dict = {2: ('djpcms/yui/yui-simple.html',),
                     3: ('djpcms/yui/yui-simple3.html',)}
    
    def __init__(self, *columns, **kwargs):
        super(Columns,self).__init__(**kwargs)        self.allchildren = columns
        ncols = len(columns)
        if not self.template or self.template_name:
            self.template_name = self.template_dict.get(ncols,None)
        if not (self.template or self.template_name):
            raise ValueError('Template not available in uniform Column.')

    def check_fields(self, missings, layout):
        newcolumns = []
        for column in self.allchildren:
            if isinstance(column,(list,tuple)):
                kwargs = {'default_style':self.default_style}
                column = layout.default_element(*column, **kwargs)
            elif not isinstance(column,html.WidgetMaker):
                column = layout.default_element(column,
                                        default_style = self.default_style)
            column.check_fields(missings,layout)
            newcolumns.append(column)
        self.allchildren = newcolumns
            
    def get_context(self, djp, widget, keys):
        ctx = super(Columns,self).get_context(djp, widget, keys)
        for i,c in enumerate(ctx.pop('children')):
            ctx['content%s' % i] = c
        ctx['grid'] = html.get_grid960(djp)
        return ctx

class Layout(FormLayout):
    '''Main class for defining the layout of a uniform.'''
    default_style  = 'inlineLabels'
    form_class = 'uniForm'
    default_element = Fieldset
    form_messages_container_class = '{0} ctrlHolder'.format(\
                                    FormLayout.form_messages_container_class)

