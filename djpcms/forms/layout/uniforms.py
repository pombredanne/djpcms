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
from djpcms.utils import zip

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


class Fieldset(FormLayoutElement):
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
    default_style = "formRow"
    

class Columns(FormLayoutElement):
    '''A :class:`FormLayoutElement` which defines a set of columns using
yui3_ grid layout.

:parameter columns: tuple of columns
:parameter column_width: optional iterable over t2o-elements tuple for defining
    the with of the columns. For example::
    
        (1,3),(2,3)
        (1,4),(1,2),(1,4)
        
    By default, equally spaced columns are used.
.. _yui3: http://yuilibrary.com/yui/docs/cssgrids/
'''
    tag = 'div'
    default_style = "formColumns"
    
    def __init__(self, *columns, **kwargs):
        column_width = kwargs.pop('column_width',None) 
        super(Columns,self).__init__(**kwargs)        self.allchildren = columns
        ncols = len(columns)
        if not column_width:
            column_width = ((1,ncols),)*ncols
        if len(column_width) != ncols:
            raise ValueError('Number of column {0} does not match number of\
 yui elements {1}'.format(ncols,len(column_width)))
        self.column_width = column_width        

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
            
    def layout_stream(self, request, widget, context):
        children = (w.render(request, context) for w in\
                         self.children_widgets(widget))
        data = tuple(zip(children, self.column_width))
        yield html.yuigrid3(*data).render(request)

class Layout(FormLayout):
    '''Main class for defining the layout of a uniform.'''
    default_style  = 'inlineLabels'
    form_class = 'uniForm'
    default_element = Fieldset
    form_messages_container_class = '{0} ctrlHolder'.format(\
                                    FormLayout.form_messages_container_class)

