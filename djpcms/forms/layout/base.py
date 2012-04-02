from inspect import isclass

from djpcms.utils.py2py3 import is_bytes_or_string
from djpcms.utils import zip
from djpcms import html, ajax
from djpcms.html.layout import equally_spaced_grid
from djpcms.utils.text import nicename

inlineLabels   = 'inlineLabels'
inlineLabels2  = 'inlineLabels fullwidth'
inlineLabels3  = 'inlineLabels auto'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'


__all__ = ['BaseFormLayout',
           'FormTemplate',
           'FormLayout',
           'FormLayoutElement',
           'DivFormElement',
           'FieldTemplate',
           'FormLayout',
           'SubmitElement',
           'Fieldset',
           'Row',
           'Columns',
           'nolabel',
           'SUBMITS',
           'inlineLabels',
           'inlineLabels2',
           'inlineLabels3',
           'blockLabels',
           'blockLabels2',
           'inlineFormsets']

nolabel = 'nolabel'
SUBMITS = 'submits' # string indicating submits in forms


def check_fields(fields, missings, layout):
    '''Utility function for checking fields in layouts'''
    new_fields = []
    for field in fields:
        if field in missings:
            if field == SUBMITS:
                field = SubmitElement()
                field.check_fields(missings,layout)
            else:
                missings.remove(field)
        elif isinstance(field,html.WidgetMaker):
            if isinstance(field,FormLayoutElement):
                field.check_fields(missings, layout)
        else:
            field = html.Html(field)
        new_fields.append(field)
    return new_fields


class FormWidget(html.Widget):
    '''A :class:`djpcms.html.HtmlWidget` used to display
forms using the :mod:`djpcms.forms.layout` API.'''    
    @property 
    def form(self):
        return self.internal['form']
    
    @property 
    def field(self):
        return self.internal.get('field')
    
    @property 
    def layout(self):
        return self.internal.get('layout',None)
    
    @property 
    def inputs(self):
        return self.internal['inputs']
    
    @property
    def success_message(self):
        return self.internal['success_message']
    
    def is_valid(self):
        '''Proxy for :attr:`forms` ``is_valid`` method.
See :meth:`djpcms.forms.Form.is_valid` method for more details.'''
        return self.form.is_valid()
    
    
class FormTemplate(html.WidgetMaker):
    _widget = FormWidget
    
    
class FieldTemplate(FormTemplate):
    
    def get_context(self, request, widget, context):
        bfield = widget.field
        parent = widget.parent.maker
        if bfield.request is not request:
            bfield.request = request
        w = bfield.widget
        parent.add_widget_classes(bfield,w)
        wrapper_class = getattr(w.maker,'wrapper_class',None)
        wrapper_class = wrapper_class + ' ' + bfield.name if wrapper_class else\
                        bfield.name
        hidden = w.attr('type')=='hidden' or  w.css('display') == 'none'
        checkbox = w.attrs.get('type') == 'checkbox'
        
        if hidden or checkbox:
            wrapper = w
        else:
            wrapper = html.Widget('div', w, cn = wrapper_class)\
                                        .addClass(' '.join(w.classes))
        context = context.copy()
        if w.attr('disabled') == 'disabled':
            wrapper.addClass('disabled')
        if w.attr('readonly') == 'readonly':
            wrapper.addClass('readonly')
        if bfield.field.required:
            wrapper.addClass('required')
        context.update({'field':bfield,
                        'name':bfield.name,
                        'widget':wrapper,
                        'parent':parent,
                        'error': bfield.form.errors.get(bfield.name,''),
                        'error_id': bfield.errors_id,
                        'ischeckbox':checkbox,
                        'hidden': hidden})
        return context

    def stream(self, request, widget, context):
        w = context['widget']
        if context['hidden']:
            yield w.render(request)
        else:
            bfield =  context['field']
            parent = context['parent']
            error = context['error']
            label = '' if parent.default_style == nolabel else bfield.label        
            yield "<div id='{0}'>{1}</div>".format(bfield.errors_id,error)
            whtml = w.render(request)
            if context['ischeckbox']:
                yield "<p class='label'></p><div class='field-widget'>\
    <label for='{0}'>{1}{2}</label></div>".format(bfield.id,whtml,label)
            else:
                if label:
                    yield "<label for='{0}' class='label'>{1}</label>"\
                            .format(bfield.id,label)
                yield whtml


class BaseFormLayout(FormTemplate):
    '''\
A :class:`djpcms.html.WidgetMaker` for programmatic
form layout design.'''
    field_widget_class = None
    
    def __init__(self, legend = None, **params):
        self.field_template = self.get_field_template()
        self.legend_html = '{0}'.format(legend) if legend else ''
        super(BaseFormLayout,self).__init__(**params)
        
    def stream(self, request, widget, context):
        if self.legend_html:
            yield html.legend(self.legend_html).render(request)
        for text in self.layout_stream(request, widget, context):
            yield text
            
    def layout_stream(self, request, widget, context):
        for text in super(BaseFormLayout,self).stream(request, widget, context):
            yield text

    def get_field_template(self):
        '''Create the template for a field.'''
        if self.field_widget_class:
            return FieldTemplate(tag='div',
                                 default_class=self.field_widget_class)
        else:
             return FieldTemplate()


class FormLayoutElement(BaseFormLayout):
    '''Base :class:`djpcms.html.WidgetMaker` class for :class:`FormLayout`
components. An instance of this class render one or several form
:class:`djpcms.forms.Field`.

:parameter children: collection of strings indicating
    :class:`djpcms.forms.Field` names and other :class:`FormLayoutElement`
    instances (allowing for nested specification).
'''
    default_class = 'layout-element'
    field_widget_class = 'ctrlHolder'
    
    def __init__(self, *children, **kwargs):
        super(FormLayoutElement,self).__init__(**kwargs)
        self.allchildren = children
        
    def check_fields(self, missings, layout):
        '''Check if the specified fields are available in the form and
remove available fields from the missing set.'''
        self.allchildren = check_fields(self.allchildren,missings,layout)
    
    def child_widget(self, child, widget, form = None, **kwargs):
        '''Override the :meth:`djpcms.html.WidgetMaker.child_widget` method
 in order to account for *child* which are form :class:`djpcms.forms.Fields`
 names.'''
        form = form if form is not None else widget.internal.get('form')
        make = super(FormLayoutElement,self).child_widget
        if form and child in form.dfields:
            return make(self.field_template, widget, form = form,
                        field=form.dfields[child], **kwargs)
        else:
            return make(child, widget, form = form, **kwargs)

    def add_widget_classes(self, field, widget):
        pass
    

class DivFormElement(FormLayoutElement):
    tag = 'div'
    

class SubmitElement(FormLayoutElement):
    tag = 'div'
    default_class = 'buttonHolder'
    
    def check_fields(self, missings, layout):
        if SUBMITS in missings:
            missings.remove(SUBMITS) 
    
    def children_widgets(self, widget):
        return widget.inputs


class FormLayout(BaseFormLayout):
    '''A :class:`djpcms.html.WidgetMaker` class for :class:`djpcms.forms.Form`
 layout design.'''
    default_style  = 'inlineLabels'
    submit_element = None
    '''Form template'''
    '''Template file for rendering form fields'''
    form_class = 'uniForm'
    '''form css class'''
    form_messages_container_class = 'form-messages ctrlHolder'
    '''Class used to hold form-wide messages'''
    form_error_class = 'errorlist ui-state-error'
    '''Class for form errors'''
    form_message_class = 'messagelist ui-state-highlight'
    '''Class for form messages'''
    from_input_class = 'buttonHolder'
    default_element = DivFormElement
    
    def __init__(self, *fields, **kwargs):
        self.setup(kwargs)
        super(FormLayout,self).__init__(**kwargs)
        if self.form_messages_container_class:
            self.add(html.WidgetMaker(tag = 'div',
                    default_class = self.form_messages_container_class))
        self.add(*fields)
        
    def setup(self, kwargs):
        attrs = ('form_messages_container_class',
                 'form_error_class',
                 'form_message_class',
                 'from_input_class')
        for att in attrs:
            if att in kwargs:
                setattr(self,att,kwargs.pop(att))
        
    def check_fields(self, missings):
        '''Add missing fields to ``self``. This
method is called by the Form widget factory :class:`djpcms.forms.HtmlForm`.

:parameter form: a :class:`djpcms.forms.Form` class.
'''
        if SUBMITS not in missings:
            missings.append(SUBMITS)
        for field in self.allchildren:
            if isinstance(field,FormLayoutElement):
                field.check_fields(missings,self)
        if missings:
            addinputs = False
            if SUBMITS in missings:
                addinputs = True
                missings.remove(SUBMITS)
            self.add(self.default_element(*missings))
            if addinputs:
                self.add(SubmitElement())
    
    def get_context(self, djp, widget, context):
        '''Overwrite the :meth:`djpcms.html.WidgetMaker.get_context` method.'''
        ctx = super(FormLayout,self).get_context(djp, widget, context)
        ctx['messages'] = ''
        return ctx

    def json_messages(self, f):
        '''Convert errors in form into a JSON serializable dictionary with keys
        given by errors html id.'''
        dfields = f._fields_dict
        ListDict = ajax.jhtmls()
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
                cl = '.'.join(self.form_messages_container_class.split(' '))
                name = '.{0}'.format(cl)
            else:
                continue
            ul = html.Widget('ul',
                             (html.Widget('li',d,cn=msg_class) for d in msg))   
            ListDict.add(name, ul.render(), removable=True)


class SimpleLayoutElement(FormLayoutElement):
    tag = None
    default_style = nolabel
    default_class = 'layout-element'
    
    
class Fieldset(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to a <fieldset>.'''
    tag = 'fieldset'
    def __init__(self, *children, **kwargs):
        super(Fieldset,self).__init__(**kwargs)
        self.allchildren = children
    
    def check_fields(self, missings, layout):
        self.allchildren = check_fields(self.allchildren,missings,layout)
      

class Row(Fieldset):
    '''A :class:`FormLayoutElement` which renders to a <div>.'''
    tag = 'div'
    default_style = "formRow"
    

class Columns(FormLayoutElement):
    '''A :class:`FormLayoutElement` which defines a set of columns using
yui3_ grid layout.

:parameter columns: tuple of columns
:parameter grid: optional :class:`djpcms.html.layout.grid`. If not provided, an
    equally spaced columns grid is used.
'''
    tag = 'div'
    default_style = "formColumns"
    
    def __init__(self, *columns, **kwargs):
        grid = kwargs.pop('grid',None) 
        super(Columns,self).__init__(**kwargs)
        self.allchildren = columns
        ncols = len(columns)
        if not grid:
            grid = equally_spaced_grid(ncols)
        if grid.numblocks != ncols:
            raise ValueError('Number of column {0} does not match number of\
 html elements {1}'.format(ncols,grid.numblocks))
        self.grid = grid

    def check_fields(self, missings, layout):
        newcolumns = []
        for column in self.allchildren:
            if isinstance(column,(list,tuple)):
                kwargs = {'default_style':self.default_style}
                column = layout.default_element(*column, **kwargs)
            elif not isinstance(column,html.WidgetMaker):
                column = layout.default_element(column,
                                        default_style = self.default_style)
            column.check_fields(missings,layout)
            newcolumns.append(column)
        self.allchildren = newcolumns
    
    def layout_stream(self, request, widget, context):
        children = (self.child_widget(c, widget) for c in self.allchildren)
        return self.grid(children).render(request, context)

    