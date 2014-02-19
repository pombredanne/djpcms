from inspect import isclass
from datetime import datetime, date
from copy import copy, deepcopy

from djpcms import html
from djpcms.html import Widget
from djpcms.utils.text import escape, slugify, to_string
from djpcms.utils.dates import parse as dateparser
from djpcms.utils.files import File
from djpcms.utils import orms

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
           'HiddenField',
           'ChoiceFieldOptions']


NOTHING = ('', None)
standard_validation_error = '{0} is required'


class Field(object):
    '''Base class for all :class:`Form` fields.
Field are specified as attribute of a form, for example::

    from djpcms import forms

    class MyForm(forms.Form):
        name = forms.CharField()
        age = forms.IntegerField()

very similar to django forms API.

:parameter required: set the :attr:`required` attribute.
:parameter default: set the :attr:`default` attribute.
:parameter initial: set the :attr:`initial` attribute.
:parameter widget: set the :attr:`widget` attribute.

.. attribute:: required

    boolean specifying if the field is required or not.
    If a field is required and
    it is not available or empty it will fail validation.

    Default: ``True``.

.. attribute:: default

    Default value for this field. It can be a callable accepting
    a :class:`BoundField` instance for the field as only parameter.

    Default: ``None``.

.. attribute:: initial

    Initial value for field. If Provided, the field will display
    the value when rendering the form without bound data.
    It can be a callable which receive a :class:`Form`
    instance as argument.

    Default: ``None``.

    .. seealso::

        Inital is used by :class:`Form` and
        by :class:`HtmlForm` instances to render
        an unbounded form. The :func:`Form.initials`
        method return a dictionary of initial values for fields
        providing one.

.. attribute:: widget

    The :class:`djpcms.html.WidgetMaker` for this field.

    Default: ``None``.

.. attribute:: widget_attrs

    dictionary of widget attributes used for setting the widget
    html attributes. For example::

        widget_attrs = {'title':'my title'}

    It can also be a callable which accept a :class:`BoundField` as the
    only parameter.

    Default: ``None``.
'''
    default = None
    widget = None
    required = True
    creation_counter = 0
    validation_error = standard_validation_error

    def __init__(self,
                 required=None,
                 default=None,
                 initial=None,
                 validation_error=None,
                 help_text=None,
                 label=None,
                 widget=None,
                 widget_attrs=None,
                 disabled=None,
                 attrname=None,
                 **kwargs):
        self.name = attrname
        self.default = default if default is not None else self.default
        self.initial = initial
        self.required = required if required is not None else self.required
        self.validation_error = validation_error or self.validation_error or\
                                    standard_validation_error
        self.help_text = escape(help_text)
        self.label = label
        self.disabled = disabled
        widget = widget or self.widget
        if isclass(widget):
            widget = widget()
        else:
            widget = copy(widget)
        self.widget = widget
        if not isinstance(self.widget,html.WidgetMaker):
            raise ValueError("Form field widget of wrong type")
        widget_attrs = widget_attrs or {}
        if not hasattr(widget_attrs,'__call__'):
            widget_attrs = widget_attrs or {}
            self.widget_attrs = widget_attrs.copy()
        else:
            self.widget_attrs = widget_attrs
        if self.disabled:
            self.widget_attrs['disabled'] = 'disabled'
        self.handle_params(**kwargs)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __repr__(self):
        return self.name
    __str__ = __repr__

    def set_name(self, name):
        self.name = name
        if not self.label:
            self.label = name

    def handle_params(self, **kwargs):
        '''Called during initialization for handling extra key-valued
parameters. By default it will raise an error if extra parameters
are available. Override for customized behaviour.'''
        self._raise_error(kwargs)

    def value_from_datadict(self, data, files, key):
        """Given a dictionary of data this field name, returns the value
of this field. Returns None if it's not provided.

:parameter data: multi dictionary of data.
:parameter files: multi dictionary of files.
:parameter files: key for this field.
:return: the value for this field
"""
        if key in data:
            return data[key]

    def value_from_instance(self, instance):
        '''Extract a value from an *instance*. By default it raises a ValueError
so that the :meth:`Form.value_from_instance` is used.'''
        raise ValueError

    def _raise_error(self, kwargs):
        keys = list(kwargs)
        if keys:
            raise ValueError('Parameter {0} not recognized'.format(keys[0]))

    def clean(self, value, bfield):
        '''Clean the field value'''
        if value in NOTHING:
            value = self.get_default(bfield)
            if self.required and value in NOTHING:
                raise ValidationError(
                            self.validation_error.format(bfield.label,value))
            elif not self.required:
                return value
        return self._clean(value, bfield)

    def _clean(self, value, bfield):
        return value

    def get_initial(self, form):
        '''\
Get the initial value of field if available.

:parameter form: an instance of the :class:`Form` class
                 where the ``self`` is declared.
        '''
        initial = self.initial
        if hasattr(initial, '__call__'):
            initial = initial(form)
        return initial

    def get_default(self, bfield):
        default = self.default
        if hasattr(default,'__call__'):
            default = default(bfield)
        return default

    def model(self):
        return None

    def html_name(self, name):
        return name

    def get_widget_data(self, bfield):
        '''Returns a dictionary of data to be added to the widget data
attribute. By default return ``None``. Override for custom behaviour.

:parameter bfield: instance of :class:`BoundField` of this field.
:rtype: an instance of ``dict`` or ``None``.'''
        return None


class CharField(Field):
    '''\
A text :class:`Field` which introduces three
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

    def handle_params(self, max_length = 30, char_transform = None,
                      toslug = None, **kwargs):
        if not max_length:
            raise ValueError('max_length must be provided for {0}'\
                             .format(self.__class__.__name__))
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
            raise ValidationError()
        if self.toslug:
            value = slugify(value, self.toslug)
        if self.char_transform:
            if self.char_transform == 'u':
                value = value.upper()
            else:
                value = value.lower()
        if self.required and not value:
            raise ValidationError(
                    self.validation_error.format(bfield.name,value))
        return value


class IntegerField(Field):
    default = None
    widget = html.TextInput(cn='numeric')
    convert_error = '"{0}" is not a valid integer.'

    def handle_params(self, validator = None, **kwargs):
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
    convert_error = 'Could not convert {0} to a valid number'
    def _clean(self, value, bfield):
        try:
            value = float(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError(self.validation_error.format(bfield,value))


class DateField(Field):
    widget = html.TextInput(cn='dateinput')
    validation_error = '{1} is not a valid date.'

    def _clean(self, value, bfield):
        if not isinstance(value, date):
            try:
                value = dateparser(value)
            except:
                raise ValidationError(
                        self.validation_error.format(bfield, value))
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
        if value in ('False', '0'):
            return False
        else:
            return bool(value)


class MultipleMixin(Field):

    def handle_params(self, multiple = None, **kwargs):
        self.multiple = multiple or False
        if self.multiple:
            self.widget_attrs['multiple'] = 'multiple'
        self._raise_error(kwargs)

    def html_name(self, name):
        return name if not self.multiple else '%s[]' % name

    def value_from_datadict(self, data, files, key):
        return self._value_from_datadict(data, key)

    def _value_from_datadict(self, data, key):
        if key in data:
            if self.multiple and hasattr(data, 'getlist'):
                return data.getlist(key)
            else:
                return data[key]


class ChoiceFieldOptions(object):
    '''A class for handling :class:`ChoiceField` options. Each
parameters can be overridden at during initialisation. It can handle both
queries on models as well as list of two-elements tuples ``(value, label)``.

.. attribute:: query

    In most cases, this is the only attribute required. It can be
     * an iterable over two elements tuples (but not a generator).
     * a query on a model
     * ``None``
     * a callable returning one of the above. The callable must accept
       a :class:`BoundField` instance as only parameter.
       It can be a *generator function*.

.. attribute:: autocomplete

    An optional boolean indicating if the field is rendered as
    an autocomplete widget.

    Default: ``False``.

.. attribute:: multiple

    ``True`` if multiple choices are possible.

    Default: ``False``.

.. attribute:: search

    A flag indicating if the field can be used as a search input in the case
    no choices where made.

    Default: ``False``.

.. attribute:: empty_label

    If provided it represents an empty choice
'''
    multiple = False
    model = None
    query = None
    field = 'id'
    autocomplete = False
    search = False
    autocomplete = None
    empty_label = '-----------'
    with_empty_label = None
    minLength = 2
    maxRows = 30

    def __init__(self, **kwargs):
        cls = self.__class__
        for attname in kwargs:
            if not attname.startswith('__') and hasattr(cls, attname):
                setattr(self, attname, kwargs[attname])
        self.mapper = orms.mapper(self.model) if self.model is not None\
                         else None
        self._setmodel(self.query)

    def all(self, bfield, html=False):
        '''Generator of all choices. If *html* is ``True`` it adds the
:attr:`empty_label`` if required.'''
        if html and not self.multiple and\
             (self.with_empty_label or not bfield.field.required):
            yield ('', self.empty_label)
        query = self.query
        if hasattr(query, '__call__'):
            query = query(bfield)
            self._setmodel(query)
        # The choice field is based on a model and therefore a query
        if self.mapper:
            if not self.autocomplete:
                query = query if query is not None else self.mapper.query()
                for v in query:
                    #TODO: allow for diferent attribute name for id
                    yield v.id, v
        elif query:
            for v in query:
                yield v

    def values(self, bfield):
        '''Generator of values in select'''
        for o in self.all(bfield):
            if isinstance(o, Widget):
                v = o.attr('value')
            else:
                v = to_string(o[0])
            yield v

    def html_value(self, val):
        '''Convert *val* into a suitable value to be included in the
widget HTML.'''
        if val:
            single_value = self.html_single_value
            if self.multiple:
                val = (single_value(el) for el in val)
            else:
                val = single_value(val)
        return val

    def html_single_value(self, value):
        '''Convert the single *value* into a suitable html value'''
        if self.mapper and hasattr(value, 'id'):
            value = value.id
        return value

    def get_initial(self, field, form):
        initial = field.initial
        if hasattr(initial, '__call__'):
            initial = initial(form)
        return initial

    def value_from_instance(self, field, instance):
        raise ValueError

    def url(self, request):
        '''Retrieve a url for search.'''
        return None

    def clean(self, value, bfield):
        '''Perform the cleaning of *value* for the :class:`BoundField`
instance *bfield*. The :meth:`ChoiceField.clean` uses this method to
clean its values.'''
        if self.mapper:
            if self.multiple:
                return self._clean_multiple_model_value(value, bfield)
            else:
                return self._clean_model_value(value, bfield)
        else:
            return self._clean_simple(value, bfield)

    #    INTERNALS

    def _clean_simple(self, value, bfield):
        '''Invoked by :meth:`clean` if :attr:`model` is not defined.'''
        ch = set(self.values(bfield))
        values = value if self.multiple else (value,)
        if not isinstance(values, (list, tuple)):
            raise ValidationError('Critical error. {0} is not a list'\
                                  .format(values))
        for v in values:
            v = to_string(v)
            if v not in ch:
                raise ValidationError('%s is not a valid choice' % v)
        return value

    def _clean_model_value(self, value, bfield):
        '''Invoked by :meth:`clean` if :attr:`model` is defined
and :attr:`multiple` is ``False``. It return an instance of :attr:`model`
otherwise it raises a validation exception unless :attr:`search`
is ``True``, in which case the value is returned.'''
        if isinstance(value, self.model):
            return value
        mapper = self.mapper
        try:
            return self.mapper.get(**{self.field: value})
        except (mapper.DoesNotExist, mapper.FieldValueError):
            if self.search:
                # if search is allowed, return the value
                return value
            else:
                raise ValidationError(
                    '{0} is not a valid {1}'.format(value,self.mapper))

    def _clean_multiple_model_value(self, value, bfield):
        field = '{0}__in'.format(self.field)
        return self.mapper.filter(**{field: value})

    def widget_value(self, value):
        model = self.model
        if not value or not model:
            return value
        if self.multiple:
            return [v.id if isinstance(v,model) else v for v in value]
        else:
            return value.id if isinstance(value, model) else value

    def get_widget_data(self, bfield):
        '''Called by the :meth:`Field.get_widget_data` method of
:class:`ChoiceField`.'''
        if not self.autocomplete:
            return
        value = bfield.value
        ch = self.all(bfield)
        if not hasattr(ch, '__len__'):
            ch = tuple(ch)
        data = {'multiple':self.multiple,
                'minlength':self.minLength,
                'maxrows':self.maxRows,
                'search_string':bfield.name,
                'url': self.url(bfield.request),
                'choices': ch}
        if self.model:
            if value:
                initial = None
                if not self.multiple:
                    if not isinstance(value,self.model):
                        if self.search:
                            initial = [(value,value)]
                    else:
                        initial = [(value.id,str(value))]
                else:
                    initial = [(v.id,str(v)) for v in value]
                data['initial_value'] = initial
        else:
            if value:
                chd = dict(ch)
                values = []
                for val in value.split(self.separator):
                    if val in chd:
                        values.append((val,chd[val]))
                if values:
                    data['initial_value'] = values
        return {'options': data}

    def _setmodel(self, query):
        # Set the model based on a query
        if not self.model and query is not None:
            self.model = getattr(query, 'model', None)
            if self.model:
                self.mapper = orms.mapper(self.model)


class ChoiceField(MultipleMixin, Field):
    '''A :class:`Field` which validates against a set of ``choices``.
It has several additional attributes which can be specified
via the :class:`ChoiceFieldOptions` class.

.. attribute:: choices

    An instance of :class:`ChoiceFieldOptions` or any of the
    possible values for the :attr:`ChoiceFieldOptions.query`
    attribute.
'''
    widget = html.Select()

    def get_initial(self, form):
        # Delegate to choices
        return self.choices.get_initial(self, form)

    def value_from_instance(self, instance):
        # Delegate to choices
        return self.choices.value_from_instance(self, instance)

    def handle_params(self, choices=None, **kwargs):
        '''Choices is an iterable or a callable which takes the
form as only argument'''
        if not isinstance(choices, ChoiceFieldOptions):
            if not hasattr(choices,'__call__') and\
               not hasattr(choices,'__iter__'):
                raise TypeError('choices must be an instance of\
 ChoiceFieldOptions, iterable or a callable. Got "{0}" instead'.format(choices))
            choices = ChoiceFieldOptions(query = choices)
        self.choices = choices
        if choices.autocomplete:
            if not self.widget.attrs.get('type') == 'text':
                self.widget = html.TextInput()
            self.widget.addClass('autocomplete')
        elif choices.multiple:
            self.widget_attrs['multiple'] = 'multiple'
        self._raise_error(kwargs)

    @property
    def multiple(self):
        return self.choices.multiple

    def _clean(self, value, bfield):
        if value is not None:
            try:
                return self.choices.clean(value, bfield)
            except Exception as e:
                raise ValidationError(str(e))
        return value

    def get_widget_data(self, bfield):
        return self.choices.get_widget_data(bfield)


class EmailField(CharField):
    pass


class FileField(MultipleMixin, Field):
    widget = html.FileInput()

    def value_from_datadict(self, data, files, key):
        res = self._value_from_datadict(files,key)
        if self.multiple:
            return [File(d.file,d.filename,d.content_type,d.size)\
                    for d in res]
        elif res:
            d = res
            return File(d.file,d.filename,d.content_type,d.size)


def HiddenField(**kwargs):
    return CharField(widget=html.HiddenInput(), **kwargs)

