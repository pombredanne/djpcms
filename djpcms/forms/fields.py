from copy import copy, deepcopy

from djpcms import sites, nodata, to_string
from djpcms.utils import escape
from djpcms.core.orms import mapper
from djpcms.html import TextInput, CheckboxInput, Select,\
                        HiddenInput

from .globals import *


__all__ = ['Field',
           'CharField',
           'BooleanField',
           'DateField',
           'DateTimeField',
           'ChoiceField',
           'IntegerField',
           'FloatField',
           'EmailField',
           'FileField',
           'HiddenField']


def standard_validation_error(field,value):
    return '{0} is required'.format(field.label)
    

class Field(object):
    '''Base class for all :class:`djpcms.forms.Form` fields.
Field are specified as attribute of a form, for example::

    from djpcms import forms
    
    class MyForm(forms.Form):
        name = forms.CharField()
        age = forms.IntegerField()
    
very similar to django forms API.
    
.. attribute:: required

    boolean specifying if the field is required or not. If a field is required and
    it is not available or empty it will fail validation.
    
    Default: ``None``.
    
.. attribute:: initial

    Initial value for field. If Provided, the field will display the value when rendering
    the form without bound data.
    
    Default: ``None``.
    
    .. seealso::
        
        Inital is used by :class:`djpcms.forms.Form` and
        by :class:`djpcms.forms.HtmlForm` instances to render
        an unbounded form. The :func:`djpcms.forms.Form.initials`
        method return a dictionary of initial values for fields
        providing one. 
    
.. attribute:: widget_attrs

    dictionary of widget attributes. Used for modifying widget html attributes.
    
    Default: ``None``.

    instance of :class:`View` or None.
    '''
    default = None
    widget = None
    required = True
    creation_counter = 0
    
    def __init__(self,
                 required = None,
                 default = None,
                 initial = None,
                 validation_error = None,
                 help_text = None,
                 label = None,
                 widget = None,
                 widget_attrs = None,
                 **kwargs):
        self.name = None
        self.default = default if default is not None else self.default
        self.initial = initial
        self.required = required if required is not None else self.required
        self.validation_error = validation_error or standard_validation_error
        self.help_text = escape(help_text)
        self.label = label
        self.widget = widget or self.widget
        self.widget_attrs = widget_attrs
        self._handle_params(**kwargs)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1
        
    def set_name(self, name):
        self.name = name
        if not self.label:
            self.label = name
        
    def _handle_params(self, **kwargs):
        self._raise_error(kwargs)
        
    def _raise_error(self, kwargs):
        keys = list(kwargs)
        if keys:
            raise ValueError('Parameter {0} not recognized'.format(keys[0]))
    
    def clean(self, value, bfield):
        '''Clean the field value'''
        if value == nodata or value is None:
            value = self.get_default(bfield)
            if self.required and value is None:
                raise ValidationError(self.validation_error(bfield,value))
        return self._clean(value, bfield)
    
    def _clean(self, value, bfield):
        return value
    
    def get_default(self, bfield):
        default = self.default
        if hasattr(default,'__call__'):
            default = default(bfield)
        return default
    
    def copy(self, bfield):
        result = copy(self)
        result.widget = deepcopy(self.widget)
        return result

    def model(self):
        return None
    

class CharField(Field):
    default = ''
    widget = TextInput
    
    def _handle_params(self, max_length = 30, **kwargs):
        if not max_length:
            raise ValueError('max_length must be provided for {0}'.format(self.__class__.__name__))
        self.max_length = int(max_length)
        if self.max_length <= 0:
            raise ValueError('max_length must be positive')
        self._raise_error(kwargs)
        
    def _clean(self, value, bfield):
        try:
            return str(value)
        except:
            raise ValidationError


class IntegerField(Field):
    widget = TextInput
    
    def _handle_params(self, validator = None, **kwargs):
        self.validator = validator
        self._raise_error(kwargs)
        
    def _clean(self, value, bfield):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError('Could not convert {0} to an integer'.format(value))
        

class FloatField(IntegerField):
    '''A field which normalises to a Python float value'''
    def _clean(self, value, bfield):
        try:
            value = float(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError('Could not convert {0} to an float value'.format(value))
    
        
class DateField(Field):
    widget = TextInput
    
    def _clean(self, value, bfield):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError
    

class DateTimeField(DateField):
    
    def _clean(self, value, bfield):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError

    
class BooleanField(Field):
    default = False
    required = False
    widget = CheckboxInput
    
    def clean(self, value, bfield):
        '''Clean the field value'''
        if value == nodata:
            return self.default
        else:
            if value in ('False', '0'):
                return False
            else:
                return bool(value)
    
    
class ChoiceField(Field):
    '''A :class:`Field` which validates against a set of ``choices``.
Additiona attributes::

.. attribuite:: choices

    A callable or an iterable over two-dimensional tuples.
    If a callable, it must accept a one parameter given by
    the bounded field instance and return an iterable over two dimensional tuples.
'''
    widget = Select
    
    def _handle_params(self, choices = None, model = None,
                       separator = ' ', inline = True,
                       empty_label = None, **kwargs):
        '''Choices is an iterable or a callable which takes the form as only argument'''
        self.choices = choices
        self._model = model
        self.empty_label = empty_label
        self.separator = separator
        self.inline = inline
        self._raise_error(kwargs)
        
    def choices_and_model(self, bfield):
        '''Return an tuple containing an
iterable over choices and a model class (if applicable).'''
        ch = self.choices
        if hasattr(ch,'__call__'):
            ch = ch(bfield)
        model = self._model
        if not model and hasattr(ch,'model'):
            model = ch.model
        return ch,model
                
    def _clean(self, value, bfield):
        if value is not None:
            ch,model = self.choices_and_model(bfield)
            if model:
                try:
                    mp = mapper(model)
                    if not isinstance(value,mp.model):
                        value = mp.get(id = value)
                except:
                    raise ValidationError('{0} is not a valid choice'.format(value))
            if value:
                if not model:
                    ch = set((to_string(x[0]) for x in ch))
                if not value in ch:
                    raise ValidationError('{0} is not a valid choice'.format(value))
        return value


class EmailField(CharField):
    pass


class FileField(CharField):
    pass


def HiddenField(**kwargs):
    return CharField(widget=HiddenInput, **kwargs)
