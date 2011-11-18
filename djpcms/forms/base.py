'''Lightweight form library

Several parts are originally from django
'''
from copy import deepcopy, copy
import json

from py2py3 import iteritems

import djpcms
from djpcms import nodata, UnicodeMixin
from djpcms.utils.structures import OrderedDict
from djpcms.core.orms import mapper
from djpcms.utils import force_str
from djpcms.utils.text import nicename
from djpcms.utils.const import NOTHING
from djpcms.html import List, SubmitInput

from .globals import *
from .formsets import FormSet
from .fields import Field


__all__ = ['FormType',
           'Form',
           'BoundField',
           'FieldList']


class FieldList(list):
    '''A list of :class:`Field` and :class:`FieldList`.
 It can be used to specify fields
 using a declarative list in a :class:`Form` class.
 For example::
 
     from djpcms import forms
     
     class MyForm(forms.Form):
         some_fields = forms.FieldList(('name',forms.CharField()),
                                       ('description',forms.CharField()))
'''
    def fields(self, prefix = None):
        for name,field in self:
            if isinstance(field,self.__class__):
                for name2,field2 in field.fields(name):
                    yield name2,field2
            else:
                if prefix:
                    name = '{0}{1}'.format(prefix,name)
                yield name,field
                

def get_form_meta_data(bases, attrs, with_base_fields=True):
    """Adapted form django
    """
    fields = []
    inlines = []
    for name,obj in list(attrs.items()):
        if isinstance(obj, Field):
            fields.append((name, attrs.pop(name)))
        elif isinstance(obj, FieldList):
            obj = attrs.pop(name)
            fields.extend(obj.fields())
        elif isinstance(obj, FormSet):
            obj.name = name
            inlines.append((name, attrs.pop(name)))
                        
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


class FormType(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        fields,inlines = get_form_meta_data(bases, attrs)
        attrs['base_fields'] = fields
        attrs['base_inlines'] = inlines
        new_class = super(FormType,cls).__new__(cls, name, bases, attrs)
        return new_class
    

# Base class for forms. Hack taht works for python 2 and python 3
BaseForm = FormType('BaseForm',(UnicodeMixin,),{})    


class Form(BaseForm):
    '''Base class for validation forms with JSON messages.
This class can be used for browser based application as well as remote
procedure calls validation.

:parameter data: dictionary type object containing data to validate.
:parameter files: dictionary type object containing files to upload.
:parameter initial: dictionary type object containing initial values for
    form fields (see  :class:`djpcms.forms.Field`).
:parameter prefix: Optional string to use as prefix for field keys.
:parameter model: An optional model class. The model must be registered with
    the library (see :func:`djpcms.RegisterORM`).
:parameter instance: An optional instance of a model class. The model must
    be registered with the library (see :func:`djpcms.RegisterORM`).
:parameter request: An optional Http Request object of any kind.
    Not used by the class itself but stored in the :attr:`request`
    attribute for convenience.
:parameter site: An optional site instance when used in a web site.

.. attribute:: is_bound

    If ``True`` the form has data which can be validated.
    
.. attribute:: initial

    Dictionary of initial values for fields.
    
.. attribute:: request

    An instance of a Http request class stored for convenience.
    The Form itself does not use it, however user's implementations
    may want to access it.
    In custom validation functions for example. Default ``None``.
    
.. attribute:: widget_attrs

    dictionary of widget attributes. Used for midifying widget html attributes.
    
    Default: ``None``.
    
.. attribute:: forms

    A list of :class:`Form` classes. If available, the forms are used to
    create sub-forms which are included in the current form.
    
    Default: ``[]``.
    
.. attribute:: form_sets

    A list of :class:`djpcms.forms.FormSet` instances. If available,
    formsets are used to create a given number of sub-forms which are
    included in the current form.
    
    Default: ``[]``.
    
'''
    prefix_input = '_prefixed'
    
    def __init__(self, data = None, files = None,
                 initial = None, prefix = None,
                 model = None, instance = None,
                 request = None, site = None):
        self.is_bound = data is not None or files is not None
        self.rawdata = data
        self._files = files
        if initial:
            self.initial = dict(initial.items())
        else:
            self.initial = {}
        self.prefix = prefix or ''
        self.model = model
        self.instance = instance
        self.messages = {}
        self.hidden_fields = set()
        self.request = request
        self._site = site
        self.changed = False
        if request:
            self.user = getattr(request,'user',None)
        else:
            self.user = None 
        if self.instance:
            model = self.instance.__class__
        self.model = model
        if model:
            self.mapper = mapper(model)
            if not self.instance:
                self.instance = model()
        else:
            self.mapper = None
        self.form_sets = {}
        for name,fset in self.base_inlines.items():
            self.form_sets[name] = fset(self)
        self.forms = []
        if not self.is_bound:
            self._fill_initial()

    @property
    def data(self):
        self._unwind()
        return self._data
    
    @property
    def cleaned_data(self):
        '''Form cleaned data, the data after the validation
algorithm has been run. If the form was
not yet validated, this property will kick off the process and return
cleaned.'''
        self._unwind()
        return self._cleaned_data
        
    @property
    def errors(self):
        '''Dictionary of errors, if any, after validation. If the form was
not yet validated, this property will kick off the process and returns errors
if they occur.'''
        self._unwind()
        return self._errors
    
    @property
    def fields(self):
        '''List of :class:`djpcms.forms.BoundField` instances after
validation.'''
        self._unwind()
        return self._fields
    
    @property
    def dfields(self):
        '''Dictionary of :class:`djpcms.forms.BoundField` instances after
validation.'''
        self._unwind()
        return self._fields_dict
    
    @property
    def site(self):
        if self._site:
            return self._site
        elif self.request:
            return self.request.DJPCMS.site
        
    @property
    def root(self):
        site = self.site
        if site:
            return site.root
    
    def _fill_initial(self):
        # Fill the initial dictionary with data from fields and from
        # the instance if available
        initials = self.initial
        instance = self.instance
        instanceid = instance.id if instance else None
        for name,field in iteritems(self.base_fields):
            if name in initials:
                continue
            # The instance is a new one (no id). precedence to the
            # initial of the form field
            if not instanceid:
                initial = field.get_initial(self)
                if initial is not None:
                    initials[name] = initial
                    continue
            if instance:
                value = self.value_from_instance(instance,name)
                if value is not None:
                    initials[name] = value
    
    def value_from_instance(self, instance, name):
        value = getattr(instance,name,None)
        if hasattr(value,'__call__'):
            value = value()
        return value
        
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
        '''unwind the form by building bound fields and validating
if it is bound.'''
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
        files = self._files
        self._fields = fields = []
        self._fields_dict = dfields = {}
        
        prefix = self.prefix
        self.initial = initial = self.initial or {}
        is_bound = self.is_bound
        form_message = self.form_message
        
        # Loop over form fields
        for name,field in iteritems(self.base_fields):         
            bfield = BoundField(self,field,name,self.prefix)
            key = bfield.html_name
            fields.append(bfield)
            dfields[name] = bfield
            field_value = None
            
            if is_bound:
                rawvalue = field_value = field.value_from_datadict(
                                    rawdata, files, key)
                if rawvalue not in NOTHING:
                    self.changed = True
                    data[name] = rawvalue
                try:
                    value = bfield.clean(rawvalue)
                    func_name = 'clean_' + name
                    if hasattr(self,func_name):
                        value = getattr(self,func_name)(value)
                    cleaned[name] = value
                except ValidationError as e:
                    form_message(errors, name, force_str(e))
            
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
Messages can be errors or not. If the message is empty, it does nothing.

:parameter container: a dictionary type container.
:parameter key: the dictionary key where the message goes.
:parameteer msg: the actual message string.'''
        if msg:
            if key in container:
                container[key].append(msg)
            else:
                container[key] = [msg]
            
    def is_valid(self):
        '''Check if Form is valid, including any subforms'''
        if self.is_bound:
            if not self.errors:
                for fset in self.form_sets.values():
                    if fset.errors or self.errors:
                        del self._cleaned_data
                        return False
                return True
            return False
        return False
    
    def clean(self):
        '''The form clean method. Called last in the validation algorithm.
By default it does nothing but it can be overritten to cross checking
fields for example. It doesn't need to return anything, just throw a
:class:`djpcms.ValidationError` in case the cleaning is not successful.
 '''
        pass
    
    def add_message(self, msg):
        self.form_message(self.messages, '__all__', msg)
        
    def add_error(self, msg):
        self.form_message(self.errors, '__all__', msg)
    
    def save_as_new(self, commit = True):
        if self.instance is not None:            
            self.instance.id = None
            for fset in self.form_sets.values():
                fset.set_save_as_new()
        return self.save(commit = commit)
    
    def save(self, commit = True):
        '''Save the form and return a model instance.
This method works if an instance or a model is available.

:parameter commit: if ``True`` changes are committed to the model backend.
:parameter as_new: if ``True`` the instance is saved as a new instance.
'''
        obj = self.before_save(commit)
        if not obj:
            obj = self.mapper.save(self.cleaned_data, self.instance, commit)
            if commit:
                for fset in self.form_sets.values():
                    fset.save()
        return obj
    
    def before_save(self, commit=True):
        '''Hook to modify/manipulate data before saving.
        It is advised to override this function rather than the save method.'''
        pass
    
    def tojson(self):
        if self.is_valid():
            return json.dumps(self.cleaned_data)
        else:
            return ''
        
        
    @classmethod
    def initials(cls):
        '''Iterator over initial field values.
Check the :attr:`djpcms.forms.Field.initial` attribute for more information.
This class method can be useful when using forms outside web applications.'''
        for name,field in iteritems(cls.base_fields):
            initial = field.get_initial(cls)
            if initial is not None: 
                yield name,initial
        
        
class BoundField(object):
    '''A Wrapper containing a :class:`djpcms.forms.Form` instance,
a :class:`djpcms.forms.Field` instance which belongs to the form,
and field bound data.
Instances of BoundField are created during form validation
and shouldn't be used otherwise. It is an utility class.

.. attribute:: form

    An instance of :class:`djpcms.forms.Form`
    
.. attribute::    field

    An instance of :class:`djpcms.forms.Field`
    
.. attribute::    name

    The :attr:`field` name (the key in the forms's fields dictionary).
    
.. attribute::    html_name

    The :attr:`field` name to be used in HTML.
'''
    _widget = None
    auto_id='id_{0[for_name]}'
    
    def __init__(self, form, field, name, prefix):
        self.form = form
        self.field = field
        self.name = name
        self.for_name = '{0}{1}'.format(prefix,name)
        self.html_name = field.html_name(self.for_name)
        self.value = None
        if field.label is None:
            self.label = nicename(name)
        else:
            self.label = field.label
        self.help_text = field.help_text
        self.id = self.auto_id.format(self.__dict__)
        self.errors_id = self.id + '-errors'
    
    def __repr__(self):
        return '{0}: {1}'.format(self.name,self.value)
    
    @property
    def is_hidden(self):
        return self.field.is_hidden
    
    def clean(self, value):
        '''return a cleaned value for ``value`` by running the validation
algorithm on :attr:`field`.'''
        self.value = self.field.clean(value, self)
        return self.value
    
    def widget(self, djp = None):
        widget = self._widget
        field = self.field
        if not widget:
            data = field.get_widget_data(djp,self)
            widget = field.widget.widget()\
                         .addAttrs(field.widget_attrs)\
                         .addData(data)
        widget.internal['bfield'] = self
        widget.addAttrs({'id': self.id,
                         'name':self.html_name,
                         'title':self.help_text})
        widget.maker.set_value(self.value, widget)
        return widget

    def _data(self):
        """Returns the data for this BoundField,
or None if it wasn't given.
        """
        return self.field.widget.value_from_datadict(
                        self.form.data, self.form.files, self.html_name)
    data = property(_data)

