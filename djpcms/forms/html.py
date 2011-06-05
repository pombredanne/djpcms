from inspect import isclass

from py2py3 import iteritems

from djpcms.utils import slugify, merge_dict, escape
from djpcms.template import loader
from djpcms.html import HtmlWidget
from djpcms.html.widgets import *


class FormWidget(HtmlWidget):
    '''A :class:`djpcms.html.HtmlWidget` used to display
forms using the :mod:`djpcms.forms.layout` API.'''
    tag = 'form'
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'method':'post',
                                                    'enctype':'multipart/form-data',
                                                    'action': '.'
                                                    })
    def __init__(self, form, layout, inputs = None, **kwargs):
        super(FormWidget,self).__init__(**kwargs)
        self.form = form
        self.layout = layout
        self.inputs = inputs if inputs is not None else []
        self.addClass(self.layout.form_class)
        
    def inner(self, djp = None, **kwargs):
        return self.layout.render(djp,
                                  self.form,
                                  self.inputs,
                                  **kwargs)
        
    def is_valid(self):
        '''Proxy for :attr:`forms` ``is_valid`` method.
See :meth:`djpcms.forms.Form.is_valid` method for more details.'''
        return self.form.is_valid()


    