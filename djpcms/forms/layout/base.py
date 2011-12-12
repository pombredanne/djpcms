from inspect import isclass

from py2py3 import is_bytes_or_string

from djpcms import html, ajax
from djpcms.utils.text import nicename


__all__ = ['FormWidget',
           'FormWidgetMaker',
           'BaseFormLayout',
           'FormLayout',
           'FormLayoutElement',
           'DivFormElement',
           'FormWidgetMaker',
           'FieldWidget',
           'FormLayout',
           'SubmitElement',
           'nolabel',
           'SUBMITS']

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
    def layout(self):
        return self.internal.get('layout',None)
    
    @property 
    def inputs(self):
        return self.internal['inputs']
    
    def is_valid(self):
        '''Proxy for :attr:`forms` ``is_valid`` method.
See :meth:`djpcms.forms.Form.is_valid` method for more details.'''
        return self.form.is_valid()
 
 
class FormWidgetMaker(html.WidgetMaker):
    _widget = FormWidget
            

class FieldWidget(FormWidgetMaker):
    default_class = 'ctrlHolder'
    
    def get_context(self, request, widget, keys):
        bfield = widget.internal['field']
        parent = widget.parent.maker
        w = bfield.widget(request)
        parent.add_widget_classes(bfield,w)
        wrapper_class = getattr(w.maker,'wrapper_class',None)
        wrapper_class = wrapper_class + ' ' + bfield.name if wrapper_class else\
                        bfield.name
        hidden = w.attr('type')=='hidden'
        checkbox = w.maker.ischeckbox()
        
        if hidden or checkbox:
            wrapper = w
        else:
            wrapper = html.Widget('div', w, cn = wrapper_class)\
                                        .addClass(' '.join(w.classes))
            
        return {'field':bfield,
                'name':bfield.name,
                'widget':wrapper,
                'parent':parent,
                'error': bfield.form.errors.get(bfield.name,''),
                'error_id': bfield.errors_id,
                'ischeckbox':checkbox,
                'hidden': hidden}
        
    def _stream(self, request, elem, context):
        w = context['widget']
        bfield =  context['field']
        parent = context['parent']
        if w.attr('disabled') == 'disabled':
            elem.addClass('disabled')
        if w.attr('readonly') == 'readonly':
            elem.addClass('readonly')
        error = context['error']
        if bfield.field.required:
            elem.addClass('required')
        label = '' if parent.default_style == nolabel else bfield.label        
        if error:
            elem.addClass('error')
            
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

    def stream(self, request, widget, context):
        if context['hidden']:
            yield context['widget'].render(request)
        else:
            elem = html.Widget('div', cn = self.default_class)
            inner = '\n'.join(self._stream(request,elem,context))
            elem.add(inner)
            yield elem.render(request)


class BaseFormLayout(FormWidgetMaker):
    '''\
A :class:`djpcms.html.WidgetMaker` for programmatic
form layout design.
    
.. attribute:: field_widget_maker

    A template name or tuple for rendering a bound field. If not provided
    the field will render the widget only.
    
    Default: ``None``.
'''
    _widget = FormWidget
    field_widget_maker = FieldWidget()
    required_tag = ''
    legend_class = 'legend ui-state-default'
    
    def __init__(self, required_tag = None,
                 field_template = None, legend = None,
                 field_widget_maker = None,
                 **params):
        self.field_widget_maker = field_widget_maker or self.field_widget_maker
        self.required_tag = required_tag or self.required_tag
        if legend:
            legend = '{0}'.format(legend)
        else:
            legend = ''
        self.legend_html = legend
        super(BaseFormLayout,self).__init__(**params)
        
    def inner(self, djp, widget, keys):
        html = super(BaseFormLayout,self).inner(djp, widget, keys)
        if html and self.legend_html:
            html = '<div class="{0}">{1}</div>\n{2}'.\
                        format(self.legend_class,self.legend_html,html)
        return html


class FormLayoutElement(BaseFormLayout):
    '''Base :class:`djpcms.html.WidgetMaker` class for :class:`FormLayout`
components. An instance of this class render one or several form
:class:`djpcms.forms.Field`.

:parameter children: collection of strings indicating
    :class:`djpcms.forms.Field` names and other :class:`FormLayoutElement`
    instances (allowing for nested specification).
    
.. attribute:: field_widget_maker

    The :class:`WidgetMaker` for fields included in this layout element.
    There shouldn't be any reason to override this attribute.
    
    Default: :class:`FieldWidget`
'''
    def __init__(self, *children, **kwargs):
        super(FormLayoutElement,self).__init__(**kwargs)
        self.allchildren = children
        
    def check_fields(self, missings, layout):
        '''Check if the specified fields are available in the form and
remove available fields from the missing set.'''
        self.allchildren = check_fields(self.allchildren,missings,layout)
    
    def child_widget(self, child, widget, form = None):
        '''Override the :meth:`djpcms.html.WidgetMaker.child_widget` method
 in order to account for *child* which are form :class:`djpcms.forms.Fields`
 names.'''
        form = form if form is not None else widget.internal.get('form')
        make = super(FormLayoutElement,self).child_widget
        if form and child in form.dfields:
            w =  make(self.field_widget_maker,
                      widget, field = form.dfields[child])
        else:
            w = make(child, widget)
        w.internal['form'] = form
        return w

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
    
    def get_context(self, djp, widget, keys):
        return {'children': [input.render(djp) for input in widget.inputs]}
        

class FormLayout(BaseFormLayout):
    '''A :class:`djpcms.html.WidgetMaker` class for :class:`djpcms.forms.Form`
 layout design.'''
    submit_element = None
    '''Form template'''
    '''Template file for rendering form fields'''
    form_class = None
    '''form css class'''
    form_messages_container_class = 'form-messages'
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
    
    def get_context(self, djp, widget, keys):
        '''Overwrite the :meth:`djpcms.html.WidgetMaker.get_context` method.'''
        ctx = super(FormLayout,self).get_context(djp, widget, keys)
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
            ListDict.add(name, ul.render(),
                         alldocument = False, removable=True)


        
        