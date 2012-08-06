'''Lightweight form library

Several parts are originally from django
'''
import json
from collections import Mapping

from djpcms.utils import orms
from djpcms.utils.httpurl import iteritems
from djpcms.utils.structures import OrderedDict
from djpcms.utils.decorators import lazyproperty
from djpcms.utils.text import nicename, UnicodeMixin, to_string
from djpcms.html import SubmitInput

from .globals import *
from .formsets import FormSet
from .fields import Field


__all__ = ['FormType',
           'Form',
           'BoundField',
           'FieldList',
           'MakeForm']


NOTHING = ('', None)

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
    def __init__(self, data=None, withprefix=True):
        self.withprefix = withprefix
        super(FieldList, self).__init__(data or ())

    def fields(self, prefix=None):
        for nf in self:
            name, field = nf[0], nf[1]
            initial = nf[2] if len(nf) > 2 else None
            if isinstance(field, self.__class__):
                for name2, field2 in field.fields(name):
                    yield name2, field2
            else:
                if prefix and self.withprefix:
                    name = '{0}{1}'.format(prefix,name)
                if isinstance(field, type):
                    field = field(initial=initial)
                yield name, field


def get_form_meta_data(bases, attrs, with_base_fields=True):
    fields = []
    inlines = []
    for name,obj in list(attrs.items()):
        if isinstance(obj, Field):
            # field name priority is the name in the instance
            obj.name = obj.name or name
            fields.append((obj.name, attrs.pop(name)))
        elif isinstance(obj, FieldList):
            obj = attrs.pop(name)
            fields.extend(obj.fields(name+'__'))
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
        fields, inlines = get_form_meta_data(bases, attrs)
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

.. attribute:: is_bound

    If ``True`` the form has data which can be validated.

.. attribute:: initial

    Dictionary of initial values for fields. The values in :attr:`initial` are
    only used when :attr:`is_bound` is ``False``.

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

    A disctionary of :class:`FormSet` instances. If available,
    form-sets are used to create a given number of sub-forms which are
    included in the current form.

    Default: ``{}``.

.. attribute:: instance

    An optional instance of a model.

    Default: ``None``.
'''
    prefix_input = '_prefixed'
    request = None

    def __init__(self, data=None, files=None, initial=None, prefix=None,
                 model=None, instance=None, request=None, environ=None,
                 on_submit=None):
        '''Initialize a :class:`Form` with *data* or *initial* values.
If *data* is not ``None`` the form will bound itself to the data, otherwise
it remains unbounded.

:parameter data: dictionary type object containing data to validate.
:parameter files: dictionary type object containing files to upload.
:parameter initial: dictionary type object containing initial values for
    form fields (see  :class:`Field`).
:parameter prefix: Optional string to use as prefix for field keys.
:parameter model: An optional model class. The model must be registered with
    the library (see :func:`djpcms.RegisterORM`).
:parameter instance: An optional instance of a model class. The model must
    be registered with the library. It sets the :attr:`instance` attribute.
:parameter request: An optional Http Request object of any kind.
    Not used by the class itself but stored in the :attr:`request`
    attribute for convenience.
    '''
        self.is_bound = data is not None or files is not None
        self.rawdata = data
        self._files = files
        if initial:
            self.initial = dict(initial.items())
        else:
            self.initial = {}
        self.prefix = prefix or ''
        self.instance = instance
        self.messages = {}
        self.request = request
        self.environ = environ
        if environ is None:
            self.environ = getattr(request, 'environ', None)
        self.changed = False
        self.user = getattr(request,'user',None) if request else None
        if self.instance:
            model = self.instance.__class__
        if model:
            self.mapper = orms.mapper(model)
            if self.mapper is not None and not self.instance:
                self.instance = self.mapper()
        else:
            self.mapper = None
        self.form_sets = {}
        for name, fset in self.base_inlines.items():
            self.form_sets[name] = fset(self)
        self.forms = []
        if on_submit is not None:
            self.on_submit = lambda commit: on_submit(self, commit)
        if not self.is_bound:
            self._fill_initial()

    @property
    def model(self):
        return self.mapper.model if self.mapper is not None else None

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
        '''List of :class:`BoundField` instances after
validation, if the form is bound, otherwise a list of :class:`BoundField`
instances with initial values.'''
        self._unwind()
        return self._fields

    @property
    def dfields(self):
        '''Dictionary of :class:`BoundField` instances after
validation.'''
        self._unwind()
        return self._fields_dict

    @property
    def view(self):
        if self.request:
            return self.request.view

    def _fill_initial(self):
        # Fill the initial dictionary with data from fields and from
        # the instance if available
        old_initial = self.initial
        self.initial = initial = {}
        instance = self.instance
        instance_id = instance.id if instance else None
        for name, field in iteritems(self.base_fields):
            if name in old_initial:
                value = old_initial[name]
            else:
                value = field.get_initial(self)
            # Instance with id can override the initial value
            if instance_id:
                try:
                    # First try the field method
                    value = field.value_from_instance(instance)
                except ValueError:
                    # otherwise try the form method
                    value = self.value_from_instance(instance, name)
            if value is not None:
                initial[name] = value

    def value_from_instance(self, instance, name):
        '''Utility function for extracting an attribute value from an
*instance*. This function is called when :class:`Form` is not bounded to data
and an :attr:`instance` of a model is available.

By default it returns the attribute value for the instance or ``None``.
Override if you need to.'''
        value = getattr(instance, name, None)
        if hasattr(value, '__call__'):
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
        self._cleaned_data = cleaned = {}
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
        self.initial = initial = self.initial
        is_bound = self.is_bound
        form_message = self.form_message

        # Loop over form fields
        for name, field in iteritems(self.base_fields):
            bfield = BoundField(self, field, name, self.prefix)
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
                    if hasattr(self, func_name):
                        value = getattr(self, func_name)(value)
                    cleaned[name] = value
                except ValidationError as e:
                    form_message(errors, name, to_string(e))

            elif name in initial:
                data[name] = field_value = initial[name]

            bfield.value = field_value

        if is_bound and not errors:
            # Invoke the form clean method. Usefull for last minute
            # checking or cross field checking
            try:
                self.clean()
            except ValidationError as e:
                form_message(errors, '__all__', to_string(e))
                del self._cleaned_data
        else:
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

    def submit(self, commit=True):
        '''Save the form and return a model instance.
This method works if an instance or a model is available.

:parameter commit: if ``True`` changes are committed to the model backend.
:parameter as_new: if ``True`` the instance is saved as a new instance.
'''
        response = self.on_submit(commit)
        if response is None:
            response = self.mapper.save(self.cleaned_data, self.instance,
                                        commit)
            if commit:
                for fset in self.form_sets.values():
                    fset.submit()
        return response

    def on_submit(self, commit):
        '''Hook to modify/manipulate data before submitting the form.
        It is advised to override this function rather than the save method.'''
        pass

    def tojson(self):
        if self.is_valid():
            return json.dumps(self.cleaned_data)
        else:
            return ''

    def get_widget_data(self, bound_field):
        pass

    @classmethod
    def initials(cls):
        '''Iterator over initial field values.
Check the :attr:`Field.initial` attribute for more information.
This class method can be useful when using forms outside web applications.'''
        for name, field in iteritems(cls.base_fields):
            initial = field.get_initial(cls)
            if initial is not None:
                yield name, initial


class BoundField(object):
    '''A Wrapper containing a :class:`Form` instance,
a :class:`Field` instance which belongs to the form,
and field bound data.
Instances of BoundField are created during form validation
and shouldn't be used otherwise.

.. attribute:: form

    An instance of :class:`Form`

.. attribute::    field

    An instance of :class:`Field`

.. attribute::    request

    An instance of :class:`djpcms.core.Request`

.. attribute::    name

    The :attr:`field` name (the key in the forms's fields dictionary).

.. attribute::    html_name

    The :attr:`field` name to be used in HTML.
'''
    auto_id='id_{0[for_name]}'

    def __init__(self, form, field, name, prefix):
        self.form = form
        self.field = field
        self.request = form.request
        self.name = name
        self.for_name = '%s%s' % (prefix, name)
        self.html_name = field.html_name(self.for_name)
        self.value = None
        if field.label is None:
            self.label = nicename(name)
        else:
            self.label = field.label
        self.required = field.required
        self.help_text = field.help_text
        self.id = self.auto_id.format(self.__dict__)
        self.errors_id = self.id + '-errors'

    def __repr__(self):
        return '{0}: {1}'.format(self.name,self.value)

    @property
    def error(self):
        return self.form.errors.get(self.name,'')

    def clean(self, value):
        '''Return a cleaned value for ``value`` by running the validation
algorithm on :attr:`field`.'''
        self.value = self.field.clean(value, self)
        return self.value

    @lazyproperty
    def widget(self):
        '''The :class:`djpcms.html.Widget` instance for the field
with bound data and attributes. This is obtained from the :class:`Field.widget`
factory.'''
        field = self.field
        data = field.get_widget_data(self)
        fdata = self.form.get_widget_data(self)
        attr = field.widget_attrs
        if hasattr(attr, '__call__'):
            attr = attr(self)
        widget = field.widget(data=data, **attr).addData(fdata)
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


def MakeForm(name, fields, **params):
    '''Create a form class from a list of fields'''
    if not isinstance(fields, Mapping):
        fields = ((f.name, f) for f in fields)
    params.update(fields)
    return FormType(name, (Form,), params)

