from inspect import isclass

from djpcms.utils.httpurl import zip
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
    for field in fields:
        if field in missings:
            if field == SUBMITS:
                field = SubmitElement(key=SUBMITS)
                field.check_fields(missings, layout)
            else:
                missings.remove(field)
        elif isinstance(field, html.WidgetMaker):
            if isinstance(field, FormLayoutElement):
                field.check_fields(missings, layout)
        else:
            field = html.WidgetMaker(key=field)
        yield field


class FormWidget(html.Widget):  
    @property 
    def form(self):
        return self.internal['form']
    
    @property 
    def field(self):
        return self.internal.get('field')
    
    @property 
    def inputs(self):
        return self.internal['inputs']
    
    @property
    def success_message(self):
        return self.internal['success_message']
    
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
        field_name = widget.field
        bfield = widget.form.dfields.get(field_name)
        parent = widget.internal.get('layout-element')
        if bfield.request is not request:
            bfield.request = request
        w = bfield.widget
        parent.add_widget_classes(bfield, w)
        hidden = w.attr('type')=='hidden' or  w.css('display') == 'none'        
        # Hidden
        if hidden:
            widget.tag = None
            widget.add(w)
        else:
            wr = parent.field_wrapper(w).addClass(w.classes)\
                                        .addClass(bfield.name)
            wr.addClass(getattr(w.maker, 'wrapper_class', None))
            if w.attr('disabled') == 'disabled':
                widget.addClass('disabled')
            if w.attr('readonly') == 'readonly':
                widget.addClass('readonly')
            if bfield.field.required:
                widget.addClass('required')
            label = bfield.label
            error = bfield.form.errors.get(bfield.name,'')
            widget.add("<div id='{0}'>{1}</div>".format(bfield.errors_id,error))
            if w.attrs.get('type') == 'checkbox':
                wr.tag = 'label'
                wr.addAttr('for', bfield.id).add((w,label))
            else:
                if parent.default_style == nolabel:
                    w.addAttr('placeholder',label)
                elif label:
                    widget.add("<label for='{0}' class='label'>{1}</label>"\
                               .format(bfield.id,label))
                wr.add(w)
            widget.add(wr)
                    


class BaseFormLayout(FormTemplate):
    '''\
A :class:`djpcms.html.WidgetMaker` for programmatic
form layout design.'''
    field_widget_class = None
    
    def __init__(self, *children, **params):
        self._children = children
        legend = params.pop('legend', None) 
        self.legend_html = '{0}'.format(legend) if legend else ''
        super(BaseFormLayout, self).__init__(**params)
        if self.legend_html:
            self.add(html.WidgetMaker(tag='div',cn='legend',key='legend'))
        
    def get_context(self, request, widget, context):
        if self.legend_html:
            context = context if context is not None else {}
            context['legend'] = self.legend_html
        return context


class FormLayoutElement(BaseFormLayout):
    '''Base :class:`djpcms.html.WidgetMaker` class for :class:`FormLayout`
components. An instance of this class render one or several form
:class:`djpcms.forms.Field`.

:parameter children: collection of strings indicating
    :class:`djpcms.forms.Field` names and other :class:`FormLayoutElement`
    instances (allowing for nested specification).
'''
    classes = 'layout-element'
    field_widget_class = 'ctrlHolder'
    field_wrapper_tag = 'div'
    submit_container_tag = 'div'
        
    def check_fields(self, missings, layout):
        '''Check if the specified fields are available in the form and
remove available fields from the missing set.'''
        children = self._children
        del self._children
        for field in check_fields(children, missings, layout):
            if not isinstance(field, html.WidgetMaker):
                if self.field_widget_class:
                    ft = FieldTemplate(tag='div', cn=self.field_widget_class)
                else:
                    ft = FieldTemplate()
                ft.internal['field'] = field
            else:
                ft = field
            ft.internal['layout-element'] = self
            self.add(ft)

    def add_widget_classes(self, field, widget):
        pass
    
    def field_wrapper(self, w):
        return html.Widget(self.field_wrapper_tag)
    

class DivFormElement(FormLayoutElement):
    tag = 'div'
    

class SubmitElement(FormLayoutElement):
    tag = 'div'
    classes = 'buttonHolder'
    
    def check_fields(self, missings, layout):
        del self._children
        if SUBMITS in missings:
            missings.remove(SUBMITS)
            
    def get_context(self, request, widget, context):
        parent = widget.internal.get('layout-element')
        if parent:
            widget.tag = parent.submit_container_tag
        widget.add(widget.inputs)


class SimpleLayoutElement(FormLayoutElement):
    tag = None
    default_style = nolabel
    classes = 'layout-element'
    
    
class Fieldset(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to a <fieldset>.'''
    tag = 'fieldset'
      

class Row(Fieldset):
    '''A :class:`FormLayoutElement` which renders to a <div>.'''
    tag = 'div'
    classes = "formRow"
    field_widget_class = None
    submit_container_tag = None
    
    def __init__(self, *children, **params):
        super(Row, self).__init__(*children, **params)
        table = html.WidgetMaker(tag='table')
        body = html.WidgetMaker(tag='body')
        row = html.WidgetMaker(tag='tr')
        self.row = row
        body.add(row)
        table.add(body)
        super(Row,self).add(table)
        
    def add(self, field):
        td = html.WidgetMaker(tag='td')
        td.add(field)
        return self.row.add(td)
    

class Columns(FormLayoutElement):
    '''A :class:`FormLayoutElement` which defines a set of columns using
yui3_ grid layout.

:parameter columns: tuple of columns
:parameter grid: optional :class:`djpcms.html.layout.grid`. If not provided, an
    equally spaced columns grid is used.
'''
    tag = 'div'
    classes = "formColumns"
    
    def __init__(self, *columns, **kwargs):
        grid = kwargs.pop('grid',None) 
        super(Columns, self).__init__(*columns, **kwargs)
        ncols = len(self._children)
        if not grid:
            grid = equally_spaced_grid(ncols)
        if grid.numcolumns != ncols:
            raise ValueError('Number of column {0} does not match number of\
 html elements {1}'.format(ncols, grid.numcolumns))
        self.internal['grid_fixed'] = False
        self.grid = grid

    def check_fields(self, missings, layout):
        newcolumns = []
        children = self._children
        del self._children
        for column in children:
            if isinstance(column,(list,tuple)):
                kwargs = {'default_style':self.default_style}
                column = layout.default_element(*column, **kwargs)
            elif not isinstance(column, html.WidgetMaker):
                column = layout.default_element(column,
                                        default_style = self.default_style)
            column.check_fields(missings, layout)
            self.add(column)
    
    def stream(self, request, widget, context):
        grid = self.child_widget(self.grid, widget)
        grid.add(widget.allchildren())
        return grid.stream(request, context)


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
    form_error_class = 'alert alert-error'
    '''Class for form errors'''
    form_message_class = 'alert alert-success'
    '''Class for form messages'''
    from_input_class = 'buttonHolder'
    default_element = Fieldset
    
    def __init__(self, *fields, **kwargs):
        self.setup(kwargs)
        super(FormLayout,self).__init__(*fields, **kwargs)
        if self.form_messages_container_class:
            msg = html.WidgetMaker(tag='div',
                                   cn=self.form_messages_container_class,
                                   key='messages')
            self.add(msg)
        
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
                fields.append(SubmitElement(key=SUBMITS))
            for field in fields:
                self.add(field)
                field.check_fields(missings, self)
    
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

    