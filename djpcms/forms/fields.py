from inspect import isclass
from datetime import datetime, date
from copy import copy, deepcopy

from djpcms import html, sites, nodata, to_string
from djpcms.utils import escape, slugify
from djpcms.utils.const import NOTHING
from djpcms.utils.dates import parse as dateparser
from djpcms.core.orms import mapper

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


standard_validation_error = '{0} is required'
    

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
    validation_error = standard_validation_error
    
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
        widget = widget or self.widget
        if isclass(widget):
            widget = widget()
        self.widget = widget
        if not isinstance(self.widget,html.WidgetMaker):
            raise ValueError("Form field widget of wrong type")
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
            if self.required and value in NOTHING:
                raise ValidationError(self.validation_error.format(bfield.name,value))
            elif not self.required:
                return value
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

    def model(self):
        return None
    
    @property
    def is_hidden(self):
        return self.widget.is_hidden
    
    def get_widget(self, djp, bfield):
        return self.widget.widget(bfield = bfield)
    

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
    widget = html.TextInput()
    
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
            raise ValidationError(self.validation_error.format(bfield.name,value))
        return value


class IntegerField(Field):
    default = 0
    widget = html.TextInput(default_class = 'numeric')
    convert_error = 'Could not convert {0} to a valid number'
    
    def _handle_params(self, validator = None, **kwargs):
        self.validator = validator
        self._raise_error(kwargs)
        
    def clean(self, value, bfield):
        try:
            value = value.replace(',','')
        except AttributeError:
            pass
        return super(IntegerField,self).clean(value,bfield)
    
    def _clean(self, value, bfield):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError(self.convert_error.format(value))
        

class FloatField(IntegerField):
    '''A field which normalises to a Python float value'''
    def _clean(self, value, bfield):
        try:
            value = float(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError(self.validation_error.format(bfield,value))
    
        
class DateField(Field):
    widget = html.TextInput(default_class = 'dateinput')
    validation_error = 'Could not recognized date {1}.'
    
    def _clean(self, value, bfield):
        if not isinstance(value, date):
            try:
                value = dateparser(value)
            except:
                raise ValidationError(self.validation_error.format(bfield,value))
        return self.todate(value)
    
    def todate(self, value):
        if hasattr(value,'date'):
            value = value.date()
        return value
    

class DateTimeField(DateField):
    
    def todate(self, value):
        if not hasattr(value, 'date'):
            value = datetime(value.year, value.month, value.day)
        return value

    
class BooleanField(Field):
    default = False
    required = False
    widget = html.CheckboxInput()
    
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
It has several additional attributes which can be used to customize its
behaviour in validation as well as when rendering in html::

.. attribuite:: choices

    A callable or any iterable over two-dimensional tuples.
    If a callable, it must accept a one parameter given by
    the bounded field instance.
    
.. attribute:: model

    An optional model class if the Choice field is based on a database model.
    
    Default ``None``.
    
.. attribute:: multiple

    ``True`` if multiple choices are possible.
    
    Default:: ``False``
    
.. attribute:: separator

    An optional character to separate elements when the field is used in conjunction with
    javascript autocomplete. This attribute is used only if :attr:`multiple` is set to ``True``.
    
    Default ``", "``
    
.. attribute:: autocomplete

    an optional boolean indicating if the field is rendered as an autocomplete widget.
    
    Default ``False``.
    
.. attribute:: empty_label

    If provided it represents an empty choice
    
This field works in conjunction with the ``autocomplete`` decorator in
``djpcms.js``.
'''
    widget = html.Select()
    
    def _handle_params(self, choices = None, model = None,
                       separator = ', ', autocomplete = False,
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
        if self.autocomplete:
            self.widget = html.TextInput(default_class = 'autocomplete')
        
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
                if self.multiple:
                    values = value.split(self.separator)
                else:
                    values = (value,)
                for val in values:
                    if not val in ch:
                        raise ValidationError('{0} is not a valid choice'.format(value))
                if self.multiple and model:
                    value = values
        return value
    
    def get_widget(self, djp, bfield):
        widget = super(ChoiceField,self).get_widget(djp, bfield)
        if self.autocomplete:
            ch,model = self.choices_and_model(bfield)
            value = bfield.value
            widget.addData('multiple',self.multiple)\
                  .addData('minlength',self.minLength)\
                  .addData('maxrows',self.maxRows)
            # If the choice field is on a model we need to have a url for searching
            if model:
                se = sites.search_engine
                if se:
                    url = se.search_url(model)
                    widget.addData('url',url)
                if value:
                    if self.multiple:
                        raise NotImplemented
                    else:
                        obj = mapper(model).get(id = value)
                        initial_value = ((obj.id,str(obj)),)
                    widget.addData('initial_value',initial_value)
            else:
                widget.addData('choices',ch)
                if value:
                    chd = dict(ch)
                    values = []
                    for val in value.split(self.separator):
                        if val in chd:
                            values.append((val,chd[val]))
                    if values:
                        widget.addData('initial_value',values)
        return widget
        

class EmailField(CharField):
    pass


class FileField(CharField):
    pass


def HiddenField(**kwargs):
    return CharField(widget=html.HiddenInput(), **kwargs)

