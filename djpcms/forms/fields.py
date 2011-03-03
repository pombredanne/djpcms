from copy import copy, deepcopy

from djpcms import sites, nodata

from .globals import *
from .html import TextInput, CheckboxInput, Select

__all__ = ['Field',
           'CharField',
           'BooleanField',
           'DateField',
           'ChoiceField',
           'IntegerField',
           'FloatField',
           'ModelChoiceField']


def standard_validation_error(field,value):
    return '{0} is required'.format(field.label)
    

class Field(object):
    '''Base class for all :class:`stdnet.forms.Form` fields.'''
    default = None
    widget = None
    required = True
    creation_counter = 0
    
    def __init__(self,
                 required = None,
                 default = None,
                 validation_error = None,
                 help_text = None,
                 label = None,
                 widget = None,
                 widget_classes = None,
                 **kwargs):
        self.name = None
        self.default = default or self.default
        self.required = required if required is not None else self.required
        self.validation_error = validation_error or standard_validation_error
        self.help_text = help_text
        self.label = label
        self.widget = widget or self.widget
        self.widget_classes = widget_classes
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
        if value == nodata or not value:
            if not self.required:
                value = self.get_default(bfield)
            else:
                value = self.get_default(bfield)
                if not value:
                    raise ValidationError(self.validation_error(bfield,value))
        return self._clean(value)
    
    def _clean(self, value):
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
        
    def _clean(self, value):
        try:
            return str(value)
        except:
            raise ValidationError


class IntegerField(Field):
    widget = TextInput
    
    def _handle_params(self, validator = None, **kwargs):
        self.validator = validator
        self._raise_error(kwargs)
        
    def _clean(self, value):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError('Could not convert {0} to an integer'.format(value))
        

class FloatField(IntegerField):
    '''A field which normalises to a Python float value'''
    def _clean(self, value):
        try:
            value = float(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError('Could not convert {0} to an float value'.format(value))
    
        
class DateField(Field):
    widget = TextInput
    
    def _clean(self, value):
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
    widget = Select
    
    def _handle_params(self, choices = None, separator = ' ', inline = True,
                       empty_label = None, initial = None, **kwargs):
        '''Choices is an iterable or a callable which takes the form as only argument'''
        self.choices = choices
        self.empty_label = empty_label
        self.separator = separator
        self.inline = inline
        self.initial = initial
        self._raise_error(kwargs)
        
    def get_choices(self):
        ch = self.choices
        if hasattr(ch,'__call__'):
            ch = ch()
        if ch:
            return dict(ch)
        else:
            return {}
                
    def _clean(self, value):
        '''Clean the field value'''
        if value:
            ch = self.get_choices()
            if value not in ch:
                raise ValidationError('{0} is not a valid choice'.format(value))
        return value

    
class ModelChoiceField(ChoiceField):
    #auto_class = AutocompleteForeignKeyInput
    
    def get_choices(self):
        ch = self.choices
        if hasattr(ch,'__call__'):
            ch = ch()
        return ch
    
    def _clean(self, value):
        '''Clean the field value'''
        if value:
            ch = self.get_choices()
            model = ch.model
            if isinstance(value,model):
                value = value.id
            if value in ch:
                return model.objects.get(id = value)
            raise ValidationError('{0} is not a valid choice'.format(value))
        return value
            
    def __deepcopy__(self, memo):
        result = super(ModelChoiceField,self).__deepcopy__(memo)
        qs = result.queryset
        if hasattr(qs,'__call__'):
            result.queryset = qs()
        return set_autocomplete(result)

