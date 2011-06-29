from copy import copy
from inspect import isclass

from py2py3 import iteritems

from djpcms import html
from djpcms.utils import slugify, escape

from .globals import *


__all__ = ['HtmlForm','FormWidget']


class FormWidget(html.Widget):
    '''A :class:`djpcms.html.HtmlWidget` used to display
forms using the :mod:`djpcms.forms.layout` API.'''
    def __init__(self, maker, form, inputs = None, **kwargs):
        super(FormWidget,self).__init__(maker,
                                        form=form,
                                        layout=maker.layout,
                                        inputs = inputs if inputs is not None else [],
                                        **kwargs)
        self.addClass(maker.layout.form_class)
    
    @property 
    def form(self):
        return self.internal['form']
    
    @property 
    def layout(self):
        return self.internal['layout']
    
    def is_valid(self):
        '''Proxy for :attr:`forms` ``is_valid`` method.
See :meth:`djpcms.forms.Form.is_valid` method for more details.'''
        return self.internal['form'].is_valid()


class HtmlForm(html.WidgetMaker):
    '''The :class:`Form` class is designed to be used for validation purposes and therefore it needs this
wrapper class for web rendering on web pages.
    
:parameter form_class: A form class setting the :attr:`form_class` attribute.
:parameter layout: An optional layout instance which sets the :attr:`layout` attribute.
                   Default ``None``.
                   
Simple usage::

    MyHtmlForm = HtmlForm(MyFormClass) 


.. attribute:: form_class

    A class derived from :class:`djpcms.forms.Form` which declares
    a set of :class:`djpcms.forms.Fields`.
    
.. attribute:: layout

    An instance of :class:`djpcms.forms.layout.FormLayout` used to render the :attr:`form_class`.
    
.. attribute:: inputs

    An iterable of form inputs.
    
    Default:: ``[]``
'''
    tag = 'form'
    _widget = FormWidget
    default_attrs = {'method':'post',
                     'enctype':'multipart/form-data',
                     'action': '.'}
    attributes = html.WidgetMaker.makeattr('method','enctype','action')
    
    def __init__(self, form_class,
                 layout = None,
                 model = None,
                 inputs = None, **params):
        super(HtmlForm,self).__init__(**params)
        self.form_class = form_class
        self.layout = layout or DefaultLayout()
        self.model = model
        self.inputs = []
        if inputs:
            for input in inputs:
                if not hasattr(input,'render'):
                    input = html.SubmitInput(value = input[0],
                                             name = input[1])
                #if not isinstance(input,html.WidgetMaker):
                #    raise TypeError('{0} is not a widgetmaker, cannot addt to form inputs'.format(input))
                self.inputs.append(input)
        missings = list(form_class.base_fields)
        self.layout.check_fields(missings)
        
    def __call__(self, model = None, inputs = None, **kwargs):
        '''Create a :attr:`form_class` instance with
input paramaters ``kwargs``.'''
        f = self.form_class(model=model or self.model,**kwargs)
        return self.widget(form = f, inputs = inputs or self.inputs)
    
    def inner(self, djp, widget, keys):
        '''Delegate the inner part of rendering to the layout instance'''
        return self.layout.inner(djp,widget,keys)


