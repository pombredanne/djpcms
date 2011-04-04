from inspect import isclass
from copy import copy, deepcopy

from djpcms import sites, nodata, to_string
from djpcms.utils import escape, slugify
from djpcms.utils.const import NOTHING
from djpcms.utils.dates import parse as dateparser
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

    Initial value for field. If Provided, the field will display
    the value when rendering the form without bound data.
    It can be a callable which receive a :class:`djpcms.forms.Form`
    instance as argument.
    
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
        if value == nodata or value in NOTHING:
            value = self.get_default(bfield)
            if self.required and value is None:
                raise ValidationError(self.validation_error(bfield,value))
        return self._clean(value, bfield)
    
    def _clean(self, value, bfield):
        return value
    
    def get_initial(self, form):
        '''\
Get the initial value of field if available.

:parameter form: an instance of the :class:`djpcms.forms.Form` class
                 where the ``self`` is declared.
        '''
        initial = self.initial
        if hasattr(initial,'__call__'):
            initial = initial(form)
        return initial
        
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
    
    def get_widget(self, djp, bfield):
        widget = self.widget
        if isclass(widget):
            widget = widget()
        return widget
    

class CharField(Field):
    '''\
A text :class:`djpcms.forms.Field` which introduces three
optional parameter (attribute):

.. attribute:: max_length

    If provided, the text length will be validated accordingly.
    
    Default ``None``.
    
.. attribute:: char_transform

    One of ``None``, ``u`` for upper and ``l`` for lower. If provided
    converts text to upper or lower.
    
    Default ``None``.
    
.. attribute:: toslug

    If provided it will be used to create a slug text which can be used
    as URI without the need to escape.
    For example, if ``toslug`` is set to "_", than::
    
        bla foo; bee

    becomes::
    
        bla_foo_bee
    
    Default ``None``
'''
    default = ''
    widget = TextInput
    
    def _handle_params(self, max_length = 30, char_transform = None,
                       toslug = None, **kwargs):
        if not max_length:
            raise ValueError('max_length must be provided for {0}'.format(self.__class__.__name__))
        self.max_length = int(max_length)
        if self.max_length <= 0:
            raise ValueError('max_length must be positive')
        self.char_transform = char_transform
        if toslug:
            if toslug == True:
                toslug = '-'
            toslug = slugify(toslug)
        self.toslug = toslug
        self._raise_error(kwargs)
        
    def _clean(self, value, bfield):
        try:
            value = to_string(value)
        except:
            raise ValidationError
        if self.toslug:
            value = slugify(value, self.toslug)
        if self.char_transform:
            if self.char_transform == 'u':
                value = value.upper()
            else:
                value = value.lower()
        if self.required and not value:
            raise ValidationError(self.validation_error(bfield,value))
        return value


class IntegerField(Field):
    default = 0
    widget = TextInput(cn = 'numeric')
    
    def _handle_params(self, validator = None, **kwargs):
        self.validator = validator
        self._raise_error(kwargs)
        
    def clean(self, value, bfield):
        value = value.replace(',','')
        return super(IntegerField,self).clean(value,bfield)
    
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
    widget = TextInput(cn = 'dateinput')
    
    def _clean(self, value, bfield):
        try:
            return dateparser(value)
        except:
            raise ValidationError('Could not recognized date {0}'.format(value))
    

class DateTimeField(DateField):
    widget = TextInput(cn = 'dateinput')
    
    def _clean(self, value, bfield):
        try:
            return dateparser(value)
        except:
            raise ValidationError('Could not recognized date {0}'.format(value))

    
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
Additional attributes:

.. attribuite:: choices

    A callable or an iterable over two-dimensional tuples.
    If a callable, it must accept a one parameter given by
    the bounded field instance and return an iterable over
    two dimensional tuples.
    
.. attribute:: model

    An optional model class if the Choice field is based on a database model.
    
    Default ``None``.
    
.. attribute:: separator

    A character to separate element when the field is used in a html
    autocomplete widget.
    
    Default ``" "``
    
.. attribute:: empty_label

    If provided it represents an empty choice
    
'''
    widget = Select
    
    def _handle_params(self, choices = None, model = None,
                       separator = ' ', autocomplete = False,
                       empty_label = None, multiple = False,
                       minLength = 2, maxRows = 20,
                       **kwargs):
        '''Choices is an iterable or a callable which takes the form as only argument'''
        self.choices = choices
        self._model = model
        self.empty_label = empty_label
        self.separator = separator
        self.autocomplete = autocomplete
        self.multiple = multiple
        self.minLength = minLength
        self.maxRows = maxRows
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
                    value = to_string(value)
                if not value in ch:
                    raise ValidationError('{0} is not a valid choice'.format(value))
        return value
    
    def get_widget(self, djp, bfield):
        if self.autocomplete:
            ch,model = self.choices_and_model(bfield)
            if model:                    
                url = djp.site.get_url(model,'search')    
                widget = TextInput(cn = 'autocomplete')
                widget.addData('url',url)\
                      .addData('multiple',self.multiple)\
                      .addData('minlength',self.minLength)\
                      .addData('maxrows',self.maxRows)
                value = bfield.value
                if value:
                    if self.multiple:
                        raise NotImplemented
                    else:
                        obj = mapper(model).get(id = value)
                        initial_value = ((obj.id,str(obj)),)
                    widget.addData('initial_value',initial_value)
                return widget
        return super(ChoiceField,self).get_widget(djp, bfield)
        


class EmailField(CharField):
    pass


class FileField(CharField):
    pass


def HiddenField(**kwargs):
    return CharField(widget=HiddenInput, **kwargs)

