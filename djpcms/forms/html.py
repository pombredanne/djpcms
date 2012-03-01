from copy import copy
from inspect import isclass

from djpcms import html
from djpcms.utils.py2py3 import iteritems
from djpcms.utils import slugify, escape

from .globals import *
from .layout import FormWidgetMaker, FormLayout


__all__ = ['HtmlForm']


def default_success_message(request, instance, mch):
    from djpcms.core.orms import mapper
    '''Very basic success message. Write your own for a better one.'''
    c = {'mch': mch}
    if instance:
        c['name'] = mapper(instance).pretty_repr(instance)
        return '{0[name]} successfully {0[mch]}'.format(c)
    else:
        return '0[mch]'.format(c)


class HtmlForm(FormWidgetMaker):
    '''The :class:`Form` class is designed to be used for validation purposes.
To render an instance of :class:`Form` on a web page we use this class.
:class:`HtmlForm` is a specialized :class:`FormWidgetMaker`.
    
:parameter form_class: A form class setting the :attr:`form_class` attribute.
:parameter layout: An optional layout instance which sets the :attr:`layout`
    attribute.    
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
                 layout = None,
                 model = None,
                 inputs = None,
                 ajax = True,
                 success_message = None,
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
        self.success_message = success_message or default_success_message
        
    def __call__(self, model = None, inputs = None,
                 action = '.', **kwargs):
        '''Create a :attr:`form_class` instance with
input paramaters ``kwargs``.'''
        f = self.form_class(model=model or self.model,**kwargs)
        w = super(HtmlForm,self).__call__(
                form = f,
                inputs = inputs or [],
                layout = self.layout,
                method = self.attrs['method'],
                action = action,
                success_message = self.success_message)\
                    .addClass(self.layout.form_class)
        if self.ajax:
            w.addClass('ajax')
        return w
    
