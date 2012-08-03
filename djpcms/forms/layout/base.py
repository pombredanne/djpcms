from inspect import isclass

from djpcms.utils.httpurl import zip, to_string
from djpcms import html, ajax
from djpcms.html.layout import equally_spaced_grid, container
from djpcms.utils.text import nicename
from . import classes


__all__ = ['BaseFormLayout',
           'FormTemplate',
           'FormLayout',
           'FormWidget',
           'FormLayoutElement',
           'FieldTemplate',
           'SimpleLayout',
           'FormLayout',
           'SubmitElement',
           'Fieldset',
           'Inlineset',
           'Columns',
           'tab',
           'Tabs',
           'SUBMITS']

SUBMITS = 'submits' # string indicating submits in forms


def check_fields(fields, missings, layout=None):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            if field == SUBMITS:
                field = SubmitElement()
                field.check_fields(missings, layout)
            else:
                missings.remove(field)
        elif isinstance(field, html.WidgetMaker):
            if isinstance(field, FormLayoutElement):
                field.check_fields(missings, layout)
        else:
            field = FormTemplate(key=field)
        yield field


class FormWidget(html.Widget):
    @property
    def form(self):
        return self.internal.get('form')

    @property
    def inputs(self):
        return self.internal.get('inputs')

    @property
    def success_message(self):
        return self.internal.get('success_message')

    def is_valid(self):
        '''Proxy for :attr:`forms` ``is_valid`` method.
See :meth:`djpcms.forms.Form.is_valid` method for more details.'''
        form = self.form
        if form:
            return self.form.is_valid()

    @property
    def field(self):
        return self.internal.get('field')

    @property
    def bfield(self):
        field = self.field
        if field:
            return self.form.dfields.get(field)


class FormTemplate(html.WidgetMaker):
    _widget = FormWidget


class FieldTemplate(FormTemplate):
    '''A class:`djpcms.html.WidgetMaker` which renders a
:class:`djpcms.forms.Field`'''
    def get_context(self, request, widget, context):
        bfield = widget.bfield
        if bfield.request is not request:
            bfield.request = request
        w = bfield.widget
        w.addClass(w.tag)
        hidden = w.attr('type') == 'hidden' or  w.css('display') == 'none'
        parent = widget.internal.get('layout-element')
        # Hidden field. No need to do a lot of decoration here.
        if hidden:
            widget.add(w).addClass('hidden')
        else:
            if parent is not None:
                wrapper = parent.field_widget(widget).addClass(w.classes)
                show_label = parent.show_field_labels
            else:
                show_label = True
                wrapper = w
            wrapper.addClass(bfield.name)
            if show_label:
                wrapper.addClass(classes.control)
            if w.attr('disabled') == 'disabled':
                widget.addClass('disabled')
            if w.attr('readonly') == 'readonly':
                widget.addClass('readonly')
            if bfield.required:
                widget.addClass(classes.required)
            # Checkbox and radio are special
            input_type = w.attrs.get('type')
            if input_type in ('checkbox', 'radio'):
                wrapper.tag = 'label'
                wrapper.addClass(input_type)\
                       .addAttr('for', bfield.id).add(bfield.label)
            else:
                wrapper.addClass(classes.ui_input)
                if show_label:
                    widget.add("<label for='%s' class='%s'>%s</label>"\
                               % (bfield.id, classes.label, bfield.label))
                else:
                    if not w.attr('placeholder'):
                        w.addAttr('placeholder', bfield.label)
            widget.add(wrapper)


class BaseFormLayout(FormTemplate):
    '''A :class:`djpcms.html.WidgetMaker` for programmatic
form layout design. This is the base class for :class:`FormLayoutElement`
and :class:`FormLayout`.

.. attribute:: default_style

    default css class style for the widget.

    Default: ``None``.

.. attribute:: show_field_labels

    flag for switching off field labels rendering.

    Default: ``True``.
'''
    field_widget_tag = None
    default_style = None
    show_field_labels = True

    def __init__(self, *children, **params):
        '''Initailize the form layout:

:parameter children: list of children to include in this
    :class:`BaseFormLayout`. Depending on the type, these children can be
    field names and/or other :class:``BaseFormLayout`.
:parameter legend: optional text to display as a legend above
    this:class:`BaseFormLayout`.'''
        self._children = children
        self.default_style = params.pop('default_style', self.default_style)
        self.show_field_labels = params.pop('show_field_labels',
                                            self.show_field_labels)
        legend = params.pop('legend', None)
        self.legend_html = to_string(legend or '')
        super(BaseFormLayout, self).__init__(**params)
        if self.legend_html:
            self.add(html.WidgetMaker(tag='div',
                                      cn=classes.legend,
                                      key='legend'))

    def add(self, *widgets):
        # Modify the add method so that default_style is propagated to
        # children which haven't one.
        if self.default_style:
            ws = []
            for w in widgets:
                if isinstance(w, FormLayoutElement):
                    w.set_style(self.default_style)
                ws.append(w)
            widgets = ws
        return super(BaseFormLayout, self).add(*widgets)

    def get_context(self, request, widget, context):
        if self.legend_html:
            context = context if context is not None else {}
            context['legend'] = self.legend_html
        return context

    def field_widget(self, widget):
        bfield = widget.bfield
        wrapper = html.Widget('div', bfield.widget)
        error = bfield.error
        widget.add("<div id='%s'>%s</div>" % (bfield.errors_id, error))
        return wrapper


class FormLayoutElement(BaseFormLayout):
    '''A :class:`BaseFormLayout` class for :class:`FormLayout`
components. An instance of this class render one or several
:class:`Field` of a form.

.. attribute:: field_widget_tag

    HTML tag for the widget wrapping each form fields included in this
    :class:`FormLayoutElement`.
'''
    field_widget_class = classes.ctrlHolder
    field_widget_tag = 'div'

    def get_context(self, request, widget, context):
        widget.addClass(self.default_style)
        return super(FormLayoutElement, self).get_context(
                                                request, widget, context)

    def check_fields(self, missings, layout=None):
        '''Check if the specified fields are available in the form and
remove available fields from the *missings* set.'''
        children = self._children
        del self._children
        for field in check_fields(children, missings, layout):
            if not isinstance(field, html.WidgetMaker):
                if self.field_widget_tag:
                    ft = FieldTemplate(tag=self.field_widget_tag,
                                       cn=self.field_widget_class)
                else:
                    ft = FieldTemplate()
                # set the field
                ft.internal['field'] = field
            else:
                ft = field
            ft.internal['layout-element'] = self
            self.add(ft)

    def set_style(self, style):
        if not self.default_style:
            self.default_style = style
        if self.default_style == classes.nolabel:
            self.show_field_labels = False


class SubmitElement(FormLayoutElement):
    tag = 'div'
    key = SUBMITS
    classes = classes.ctrlHolder

    def check_fields(self, missings, layout):
        del self._children
        if self.key in missings:
            missings.remove(self.key)

    def get_context(self, request, widget, context):
        inputs = widget.inputs or ()
        hidden = True
        for inp in inputs:
            if inp.attr('type') != 'hidden':
                hidden = False
                break
        if hidden:
            widget.tag = None
            inner = inputs
        else:
            inner = html.Widget('div', inputs,
                                cn=(classes.control, classes.button_holder))
        widget.add(inner)
        return super(SubmitElement, self).get_context(request, widget, context)


class Fieldset(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to a <fieldset>.'''
    tag = 'fieldset'


class Inlineset(FormLayoutElement):
    tag = 'div'
    field_widget_class = classes.inline
    classes = classes.ctrlHolder
    show_field_labels = False

    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        super(Inlineset, self).__init__(*args, **kwargs)
        self.add(html.WidgetMaker(tag='label', key='label', cn='label'),
                 html.WidgetMaker(tag='div', key='inputs', cn=classes.control))

    def add(self, *widgets):
        if 'inputs' in self:
            widgets = [w.addClass(self.field_widget_class) for w in widgets]
            return self['inputs'].add(*widgets)
        else:
            return super(Inlineset, self).add(*widgets)

    def get_context(self, request, widget, context):
        if self.label:
            context = context if context is not None else {}
            context['label'] = self.label
        return super(Inlineset, self).get_context(request, widget, context)


class MultiElement(FormLayoutElement):
    tag = 'div'

    def check_fields(self, missings, layout):
        newcolumns = []
        children = self._children
        del self._children
        elements = []
        for column in children:
            if isinstance(column, (list, tuple)):
                group = []
                for el in column:
                    if isinstance(el, html.WidgetMaker):
                        if group:
                            elements.append(
                                    self.default_element(layout, *group))
                            group = []
                        elements.append(el)
                    else:
                        group.append(el)
                if group:
                    elements.append(self.default_element(layout, *group))
            elif not isinstance(column, html.WidgetMaker):
                elements.append(self.default_element(layout, column))
            else:
                elements.append(column)
        for element in elements:
            element.check_fields(missings, layout)
            self.add(element)

    def default_element(self, layout, *elems):
        kwargs = {'default_style': self.default_style}
        return layout.default_element(*elems, **kwargs)


class Columns(MultiElement):
    '''A :class:`FormLayoutElement` which defines a set of columns.

:parameter columns: tuple of columns
:parameter grid: optional :class:`djpcms.html.layout.grid`. If not provided, an
    equally spaced columns grid is used.
'''
    classes = "formColumns"

    def __init__(self, *columns, **kwargs):
        grid = kwargs.pop('grid', None)
        super(Columns, self).__init__(*columns, **kwargs)
        ncols = len(self._children)
        if not grid:
            grid = equally_spaced_grid(ncols)
        if grid.numcolumns != ncols:
            raise ValueError('Number of column {0} does not match number of\
 html elements {1}'.format(ncols, grid.numcolumns))
        self.internal['grid_fixed'] = False
        self.grid = grid

    def stream(self, request, widget, context):
        grid = self.child_widget(self.grid, widget)
        grid.add(widget.allchildren())
        return grid.stream(request, context)


class tab(object):

    def __init__(self, name, *fields):
        self.name = name
        self.fields = fields


class Tabs(MultiElement):
    classes = "formTabs"
    tabtemplate = html.tabs

    def __init__(self, *tabs, **kwargs):
        tab_type = kwargs.pop('tab_type', None)
        columns = []
        self.names = []
        for n, t in enumerate(tabs, 1):
            if not isinstance(t, tab):
                if not isinstance(t, (list, tuple)):
                    t = (t,)
                t = tab('tab-%s' % n, *t)
            self.names.append(t.name)
            columns.append(t.fields)
        super(Tabs, self).__init__(*columns, **kwargs)
        if tab_type == 'pills':
            self.tab = html.pills
        elif tab_type == 'accordion':
            self.tab = html.accordion
        else:
            self.tab = html.tabs

    def stream(self, request, widget, context):
        tab = self.child_widget(self.tab, widget)
        tab.add(zip(self.names,widget.allchildren()))
        return tab.stream(request, context)


class SimpleLayout(BaseFormLayout):
    tag = None
    form_class = None
    default_element = FormLayoutElement

    def check_fields(self, missings):
        '''Add missing fields to ``self``. This
method is called by the Form widget factory :class:`djpcms.forms.HtmlForm`.

:parameter form: a :class:`djpcms.forms.Form` class.
'''
        children = self._children
        del self._children
        if SUBMITS not in missings:
            missings.append(SUBMITS)
        for field in children:
            if isinstance(field, FormLayoutElement):
                field.check_fields(missings, self)
            self.add(field)
        if missings:
            addinputs = False
            if SUBMITS in missings:
                addinputs = True
                missings.remove(SUBMITS)
            fields = [self.default_element(*missings)]
            if addinputs:
                fields.append(SubmitElement())
            for field in fields:
                self.add(field)
                field.check_fields(missings, self)


class FormLayout(SimpleLayout):
    '''A :class:`djpcms.html.WidgetMaker` class for :class:`djpcms.forms.Form`
 layout design.'''
    default_style = classes.inlineLabels
    submit_element = None
    '''Form template'''
    '''Template file for rendering form fields'''
    form_class = classes.form
    '''form css class'''
    form_messages_container_class = ('form-messages', classes.ctrlHolder)
    '''Class used to hold form-wide messages'''
    form_error_class = 'alert alert-error'
    '''Class for form errors'''
    form_message_class = 'alert alert-success'
    default_element = Fieldset

    def __init__(self, *fields, **kwargs):
        self.setup(kwargs)
        super(FormLayout, self).__init__(*fields, **kwargs)
        if self.form_messages_container_class:
            msg = html.WidgetMaker(tag='div',
                                   cn=self.form_messages_container_class,
                                   key='messages')
            self.add(msg)

    def setup(self, kwargs):
        attrs = ('form_messages_container_class',
                 'form_error_class',
                 'form_message_class')
        for att in attrs:
            if att in kwargs:
                setattr(self,att,kwargs.pop(att))

    def get_context(self, request, widget, context):
        '''Overwrite the :meth:`djpcms.html.WidgetMaker.get_context` method.'''
        context = context if context is not None else {}
        context = super(FormLayout,self).get_context(request, widget, context)
        context['messages'] = ''
        return context

    def json_messages(self, f):
        '''Convert errors in form into a JSON serializable dictionary with keys
        given by errors html id.'''
        dfields = f._fields_dict
        ListDict = ajax.jhtmls(f.environ)
        self._add(ListDict,dfields,f.errors,self.form_error_class)
        self._add(ListDict,dfields,f.messages,self.form_message_class)
        for fset in f.form_sets.values():
            for f in fset.forms:
                dfields = f._fields_dict
                self._add(ListDict,dfields,f.errors,self.form_error_class)
                self._add(ListDict,dfields,f.messages,self.form_message_class)
        return ListDict

    def _add(self, ListDict, fields, container, msg_class):
        # Add messages to the list dictionary
        for name,msg in container.items():
            if name in fields:
                name = '#' + fields[name].errors_id
            elif self.form_messages_container_class:
                cl = '.'.join(self.form_messages_container_class)
                name = '.{0}'.format(cl)
            else:
                continue
            ul = html.Widget('ul',
                             (html.Widget('li',d,cn=msg_class) for d in msg))
            ListDict.add(name, ul.render(), removable=True)

