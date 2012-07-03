from copy import copy
from inspect import isclass

from djpcms import html
from djpcms.utils.httpurl import iteritems
from djpcms.utils.text import slugify, escape
from djpcms.utils.orms import mapper

from .globals import *
from .layout import FormTemplate, FormLayout


__all__ = ['HtmlForm']


def default_success_message(request, instance, modified_or_added):
    '''Very basic success message. Write your own for a better one.'''
    if instance:
        name = mapper(instance).pretty_repr(instance)
        return '%s successfully %s' % (name,modified_or_added)
    else:
        return '%s' % modified_or_added


class HtmlForm(FormTemplate):
    '''The :class:`Form` class is designed to be used for validation purposes.
To render an instance of :class:`Form` on a web page we use this class.
:class:`HtmlForm` is a specialized :class:`FormTemplate`.
    
:parameter form_class: A :class:`Form` class setting the :attr:`form_class`
    attribute.
:parameter layout: An optional :class:`Formlayout` instance which sets
    the :attr:`layout` attribute.    
:parameter ajax: Set the :attr:`ajax` attribute.
:parameter success_message: optional function which overrides the
    :attr:`success_message` attribute

 
                   
Simple usage::

    from djpcms import forms
    
    MyHtmlForm = forms.HtmlForm(MyFormClass,
                                method = 'get') 


.. attribute:: form_class

    A class derived from :class:`djpcms.forms.Form` which declares
    a set of :class:`djpcms.forms.Fields`.
    
.. attribute:: layout

    An instance of :class:`djpcms.forms.layout.FormLayout` used to render
    the :attr:`form_class`.

.. attribute:: ajax

    If ``True`` the interaction will be using ajax.
    
    Default: ``True``.
    
.. attribute:: inputs

    An iterable of form inputs.
    
    Default:: ``[]``
    
.. attribute:: success_message

    A callable which accept the request object, an instance of an object
    and a string indicating if the form has changed or created the instance.
'''
    tag = 'form'
    default_attrs = {'method':'post',
                     'enctype':'multipart/form-data',
                     'action': '.'}
    attributes = html.WidgetMaker.makeattr('method','enctype','action')
    
    def __init__(self, form_class,
                 layout=None,
                 model=None,
                 inputs=None,
                 ajax=True,
                 success_message=None,
                 internal=None,
                 **params):
        layout = layout if layout is not None else FormLayout()
        layout.key = 'layout'
        if inputs:
            new_inputs = []
            for input in inputs:
                if not hasattr(input, 'render'):
                    input = html.SubmitInput(value = input[0],
                                             name = input[1])
                new_inputs.append(input)
            inputs = new_inputs
        internal = {
            'success_message': success_message or default_success_message,
            'form_class': form_class,
            'model': model,
            'inputs': inputs}
        super(HtmlForm, self).__init__(internal=internal, **params)
        if ajax:
            self.addClass('ajax')
        self.addClass(layout.form_class)
        self.add(layout)
        layout.check_fields(list(form_class.base_fields))
        
    @property
    def model(self):
        return self.internal['model']
    
    @property
    def form_class(self):
        return self.internal['form_class']
    
    @property
    def inputs(self):
        return self.internal['inputs']
    
    def __call__(self, model = None, inputs = None,
                 action = '.', **kwargs):
        '''Create a :attr:`form_class` instance with
input paramaters ``kwargs``.'''
        f = self.form_class(model=model or self.model, **kwargs)
        return super(HtmlForm,self).__call__(form=f, inputs=inputs,
                                             action=action)
        
    def json_messages(self, f):
        return self.children['layout'].json_messages(f)
    