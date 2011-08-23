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
            new_fields.append(field)
        elif is_bytes_or_string(field):
            raise ValueError('Field {0} is not part of form'\
                             .format(field))
        else:
            field.check_fields(missings, layout)
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
        return self.internal['layout']
    
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

    def get_context(self, djp, widget, keys):
        bfield = widget.internal['field']
        layout = widget.layout
        element = widget.parent.maker
        form = bfield.form
        name = bfield.name
        w = bfield.field.get_widget(djp, bfield)
        element.add_widget_classes(bfield,w)
        whtml = w.render(djp)
        return {'label': None if self.default_style == nolabel\
                                     else bfield.label,
                'name': name,
                'required_tag': element.required_tag or layout.required_tag,
                'field':bfield,
                'error': form.errors.get(name,''), 
                'inner':whtml,
                'is_hidden': w.maker.is_hidden,
                'ischeckbox':w.maker.ischeckbox()}
        
    def stream(self, w, bfield, elem, whtml, parent):
        name = bfield.name
        error = bfield.form.errors.get(name,'')
        if bfield.field.required:
            elem.addClass('required')
        label = '' if parent.default_style == nolabel else bfield.label        
        if error:
            elem.addClass('error')
            
        yield "<div id='{0}'>{1}</div>".format(bfield.errors_id,error)

        if w.maker.ischeckbox():
            yield "<p class='label'></p><div class='field-widget'>\
<label for='{0}'>{1}{2}</label></div>".format(bfield.id,whtml,label)
        else:
            if label:
                yield "<label for='{0}' class='label'>{1}</label>"\
                        .format(bfield.id,label)
            yield "<div class='field-widget input {0} ui-widget-content'>\
 {1}</div>".format(name,whtml)
            if bfield.help_text:
                yield "<div id='hint_{0}' class='formHint'>{1}</div>".\
                        format(bfield.id,bfield.help_text)

                
    def inner(self, djp, widget, keys):
        bfield = widget.internal['field']
        layout = widget.layout
        parent = widget.parent.maker
        w = bfield.field.get_widget(djp, bfield)
        parent.add_widget_classes(bfield,w)
        whtml = w.render(djp)
        if w.maker.is_hidden:
            return whtml
        else:
            elem = html.Widget('div', cn = self.default_class)
            inner = '\n'.join(self.stream(w,bfield,elem,whtml,parent))
            return elem.render(djp,inner)


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
                 **params):
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
    '''A :class:`djpcms.forms.layout.BaseFormLayout` 
class for a :class:`djpcms.forms.layout.FormLayout` element.
It defines how form fields are rendered and it can
be used to add extra html elements to the form.
'''
    default_class = 'ctrlHolder'
    
    def check_fields(self, missings, layout):
        raise NotImplementedError
    
    def child_widget(self, child, widget):
        form = widget.form
        make = super(FormLayoutElement,self).child_widget
        if child in form.dfields:
            return make(self.field_widget_maker,
                        widget, field = form.dfields[child])
        else:
            return make(child, widget)

    def add_widget_classes(self, field, widget):
        pass
    

class DivFormElement(FormLayoutElement):
    tag = 'div'
    def __init__(self, *children, **kwargs):
        super(DivFormElement,self).__init__(**kwargs)
        self.allchildren = children

    def check_fields(self, missings, layout):
        self.allchildren = check_fields(self.allchildren,missings,layout)
    

class SubmitElement(FormLayoutElement):
    tag = 'div'
    default_class = 'buttonHolder'
    
    def check_fields(self, missings, layout):
        if SUBMITS in missings:
            missings.remove(SUBMITS) 
    
    def get_context(self, djp, widget, keys):
        return {'children': [input.render(djp) for input in widget.inputs]}
        

class FormLayout(BaseFormLayout):
    '''Base form class for form layout design'''
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
        super(FormLayout,self).__init__(**kwargs)
        self.add(html.WidgetMaker(tag = 'div',
                default_class = self.form_messages_container_class))
        self.add(*fields)
        
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
            else:
                cl = '.'.join(self.form_messages_container_class.split(' '))
                name = '.{0}'.format(cl)
            ListDict.add(name,
                         html.List(data = msg, li_class = msg_class).render(),
                         alldocument = False,
                         removable=True)


        
        