'''Lightweight form library

Several parts are originally from django
'''
from copy import deepcopy

from py2py3 import iteritems

from djpcms import nodata
from djpcms.utils.collections import OrderedDict
from djpcms.core.orms import mapper
from djpcms.utils import force_str
from djpcms.utils.text import nicename

from .globals import *
from .fields import Field
from .html import media_property, FormWidget, List


__all__ = ['Form',
           'HtmlForm',
           'BoundField',
           'FormSet']


class FormSet(object):
    """A collection of instances of the same Form."""
    creation_counter = 0
    def __init__(self, form_class, prefix = ''):
        self.form_class = form_class
        self.prefix = ''
        self.creation_counter = Field.creation_counter
        FormSet.creation_counter += 1


def get_form_meta_data(bases, attrs, with_base_fields=True):
    """Adapted form django
    """
    fields = []
    inlines = []
    for name,obj in list(attrs.items()):
        if isinstance(obj, Field):
            fields.append((name, attrs.pop(name)))
        elif isinstance(obj, FormSet):
            fields.append((name, attrs.pop(name)))
                        
    fields = sorted(fields, key=lambda x: x[1].creation_counter)
    inlines = sorted(inlines, key=lambda x: x[1].creation_counter)
    
    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = list(base.base_fields.items()) + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = list(base.declared_fields.items()) + fields

    return OrderedDict(fields),OrderedDict(inlines)


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        fields,inlines = get_form_meta_data(bases, attrs)
        attrs['base_fields'] = fields
        attrs['base_inlines'] = inlines
        new_class = super(DeclarativeFieldsMetaclass,cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class
    

BaseForm = DeclarativeFieldsMetaclass('BaseForm',(object,),{})    


class Form(BaseForm):
    '''Base class for forms with JSON messages.'''
    prefix_input = '_prefixed'
    auto_id='id_{0[html_name]}'
    
    def __init__(self, data = None, files = None,
                 initial = None, prefix = None,
                 factory = None, model = None,
                 instance = None, request = None):
        self.is_bound = data is not None or files is not None
        self.factory = factory
        self.rawdata = data
        self._files = files
        self.initial = initial
        self.prefix = prefix or ''
        self.model = model
        self.instance = instance
        self.messages = {}
        self.request = request
        if self.instance:
            model = self.instance.__class__
        self.model = model
        if model:
            self.mapper = mapper(model)            
    
    @property
    def data(self):
        self._unwind()
        return self._data
    
    @property
    def cleaned_data(self):
        self._unwind()
        return self._cleaned_data
        
    @property
    def errors(self):
        self._unwind()
        return self._errors
    
    @property
    def fields(self):
        self._unwind()
        return self._fields
    
    @property
    def dfields(self):
        self._unwind()
        return self._fields_dict
    
    def get_prefix(self, prefix, data):
        if data and self.prefix_input in data:
            return data[self.prefix_input]
        elif prefix:
            if hasattr(prefix,'__call__'):
                prefix = prefix()
            return prefix
        else:
            return ''
    
    def additional_data(self):
        return None
        
    def _unwind(self):
        '''unwind the form by building bound fields and validating if it is bound.'''
        if hasattr(self,'_data'):
            return
        self._data = data = {}
        cleaned = {}
        self._errors = errors = {}
        rawdata = self.additional_data()
        if rawdata:
            rawdata.update(self.rawdata)
        else:
            rawdata = self.rawdata
        self._fields = fields = []
        self._fields_dict = dfields = {}
        
        prefix = self.prefix
        self.initial = initial = self.initial or {}
        is_bound = self.is_bound
        form_message = self.form_message
        
        # Loop over form fields
        for name,field in iteritems(self.base_fields):
            key = self.prefix+name         
            bfield = BoundField(self,field,name,key)
            fields.append(bfield)
            dfields[name] = bfield
            field_value = None
            
            if is_bound:
                if key in rawdata:
                    value = field_value = rawdata[key]
                else:
                    value = nodata
                try:
                    value = bfield.clean(value)
                    func_name = 'clean_' + name
                    if hasattr(self,func_name):
                        value = getattr(self,func_name)(value)
                    cleaned[name] = value
                except ValidationError as e:
                    form_message(errors, name, force_str(e))
                data[name] = value
            
            elif name in initial:
                data[name] = field_value = initial[name]
            
            bfield.value = field_value
                
        if is_bound and not errors:
            self._cleaned_data = cleaned
        
            # Invoke the form clean method. Usefull for last minute
            # checking or cross field checking
            try:
                self.clean()
            except ValidationError as e:
                form_message(errors, '__all__', force_str(e))
                del self._cleaned_data
                
    def form_message(self, container, key, msg):
        '''Add a message to a message container in the form.
Messages can be errors or not.

:parameter container: a dictionary type container.
:parameter key: the dictionary key where the message goes.
:parameteer msg: the actual message, unicode please.'''
        if key in container:
            container[key].append(msg)
        else:
            container[key] = [msg]
            
    def is_valid(self):
        return self.is_bound and not self.errors
    
    def clean(self):
        pass
    
    def render(self):
        layout = self.factory.layout
        if not layout:
            layout = DefaultLayout()
            self.factory.layout = layout
        return layout.render(self)
    
    def add_message(self, msg):
        self.form_message(self.messages, '__all__', msg)
        
    def add_error(self, msg):
        self.form_message(self.errors, '__all__', msg)
    
    def save(self, commit = True):
        '''Save the form. This method works if an instance or a model is available'''
        self.mapper.save(self.cleaned_data, self.instance, commit)
        

class HtmlForm(object):
    '''An HTML class Factory Form used for grouping a :class:`Form` class, a
    form :class:`Layout` instance and a model class.'''
    def __init__(self, form_class, layout = None, model = None, submits = None):
        self.form_class = form_class
        self._layout = layout
        self.model = model
        self.submits = submits
        
    def __get_layout(self):
        layout = self._layout
        if not layout:
            self._layout = layout = DefaultLayout()
        return layout
    def __set_layout(self, lay):
        self._layout = lay
    layout = property(__get_layout,__set_layout)
        
    def __call__(self, model = None, **kwargs):
        return self.form_class(model=model or self.model,**kwargs)
    
    def widget(self, form, **kwargs):
        '''Create a rendable form widget'''
        return FormWidget(form, layout = self.layout, **kwargs)
    
        
class BoundField(object):
    "A Wrapper containg a form, field and data"
    def __init__(self, form, field, name, html_name = None):
        self.form = form
        self.field = field.copy(self)
        self.name = name
        self.html_name = html_name or name
        self.value = None
        if field.label is None:
            self.label = nicename(name)
        else:
            self.label = field.label
        self.help_text = field.help_text
        self.id = form.auto_id.format(self.__dict__)
        self.errors_id = self.id + '-errors'
        
    def clean(self, value):
        self.value = self.field.clean(value, self)
        return self.value

    def _data(self):
        """
        Returns the data for this BoundField, or None if it wasn't given.
        """
        return self.field.widget.value_from_datadict(self.form.data, self.form.files, self.html_name)
    data = property(_data)

