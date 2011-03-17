from inspect import isclass

from py2py3 import iteritems

from djpcms.utils import slugify, merge_dict, escape
from djpcms.template import loader
from djpcms.html import BaseMedia, HtmlWidget
from djpcms.html.widgets import *



class FormWidget(HtmlWidget):
    '''Form HTML widget'''
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
        
    def inner(self, djp = None):
        return self.layout.render(djp,
                                  self.form,
                                  self.inputs)
        
    def is_valid(self):
        '''Proxy for self.forms.is_valid'''
        return self.form.is_valid()
    
    def add(self, elem):
        '''Add extra element to the form widget'''
        pass
    