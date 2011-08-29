from copy import copy
from inspect import isclass

from py2py3 import iteritems

from djpcms import html
from djpcms.utils import slugify, escape

from .globals import *
from .layout import FormWidgetMaker, FormLayout


__all__ = ['HtmlForm']


class HtmlForm(FormWidgetMaker):
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
    default_attrs = {'method':'post',
                     'enctype':'multipart/form-data',
                     'action': '.'}
    attributes = html.WidgetMaker.makeattr('method','enctype','action')
    
    def __init__(self, form_class,
                 layout = None,
                 model = None,
                 inputs = None,
                 ajax = True,
                 **params):
        super(HtmlForm,self).__init__(**params)
        self.form_class = form_class
        self.layout = layout or DefaultLayout()
        self.model = model
        self.ajax = ajax
        self.inputs = None
        if inputs is not None:
            self.inputs = []
            for input in inputs:
                if not hasattr(input,'render'):
                    input = html.SubmitInput(value = input[0],
                                             name = input[1])
                #if not isinstance(input,html.WidgetMaker):
                #    raise TypeError('{0} is not a widgetmaker,
                # cannot addt to form inputs'.format(input))
                self.inputs.append(input)
        missings = list(form_class.base_fields)
        self.layout.check_fields(missings)
        self.add(self.layout)
        
    def __call__(self, model = None, inputs = None,
                 action = '.', **kwargs):
        '''Create a :attr:`form_class` instance with
input paramaters ``kwargs``.'''
        f = self.form_class(model=model or self.model,**kwargs)
        w =  self.widget(form = f,
                         inputs = inputs or [],
                         layout = self.layout,
                         method = self.attrs['method'],
                         action = action)\
                            .addClass(self.layout.form_class)
        if self.ajax:
            w.addClass('ajax')
        return w
    
