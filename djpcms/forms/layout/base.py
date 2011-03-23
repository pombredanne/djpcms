from inspect import isclass

from djpcms.html import List
from djpcms.forms.html import HtmlWidget
from djpcms.template import loader
from djpcms.utils.ajax import jhtmls

__all__ = ['BaseFormLayout',
           'FormLayout',
           'FormLayoutElement',
           'DivFormElement',
           'Html',
           'nolabel']


nolabel = 'nolabel'


class BaseFormLayout(HtmlWidget):
    '''\
A :class:`djpcms.html.HtmlWidget` base class for programmatic
form layout design.
    
.. attribute:: field_template

    A template name or tuple for rendering a bound field. If not provided
    the field will render the widget only.
    
    Default: ``None``.
'''
    field_template = None
    default_style = None
    required_tag = ''
    
    def __init__(self, default_style = None, required_tag = None,
                 field_template = None, **kwargs):
        self.default_style = default_style or self.default_style
        self.required_tag = required_tag or self.required_tag
        self.default_style = default_style or self.default_style
        super(BaseFormLayout,self).__init__(**kwargs)


class FormLayoutElement(BaseFormLayout):
    '''A :class:`djpcms.forms.layout.BaseFormLayout` 
class for a :class:`djpcms.forms.layout.FormLayout` element.
It defines how form fields are rendered and it can
be used to add extra html elements to the form.

:parameter key: An optional string. It is used to easily retrieve the
                element in the layout which holds it.
                If specified, the element
                will be an attribute named ``key`` of the layout itself.
                
                Default: ``None``
                
:parameter elem_css: defining element class name.
:parameter kwargs: additional parameters to be passed to the
                   :class:`djpcms.forms.layout.BaseFormLayout` base class.
'''
    elem_css = None
    template = None
    
    def __init__(self, key = None, elem_css = None, **kwargs):
        super(FormLayoutElement,self).__init__(**kwargs)
        self.key = key
        self.elem_css = elem_css or self.elem_css
        
    def make_classes(self):
        self.addClass(self.elem_css).addClass(self.default_style)
        
    def render_field(self, djp, bfield, layout):
        '''\
Render a single bound field using a layout.

:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter bfield: instance of :class:`djpcms.forms.BoundField` to render.
:parameter layout: the instance of :class:`djpcms.forms.layout.FormLayout`
                   to which ``self`` belongs to.

It uses the :attr:`djpcms.forms.layout.BaseFormLayout.field_template`
attribute to render the bounded field.
        '''
        form = bfield.form
        name = bfield.name
        rendered_fields = layout.get_rendered_fields(form)
        if not bfield.name in rendered_fields:
            rendered_fields[bfield.name] = bfield
        else:
            raise Exception("A field should only be rendered once: %s" % bfield)
        widget = bfield.field.widget
        if isclass(widget):
            widget = widget()
        self.add_widget_classes(bfield,widget)
        field_template = self.field_template or layout.field_template
        whtml = widget.render(djp, bfield)
        if not field_template:
            return whtml
        else:
            ctx = {'label': None if self.default_style == nolabel else bfield.label,
                   'required_tag': self.required_tag or layout.required_tag,
                   'field':bfield,
                   'error': form.errors.get(name,''), 
                   'widget':whtml,
                   'is_hidden': widget.is_hidden,
                   'ischeckbox':widget.ischeckbox()}
            return loader.render(field_template,ctx)

    def add_widget_classes(self, field, widget):
        pass


class Html(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, html = '', renderer = None, **kwargs):
        super(Html,self).__init__(**kwargs)
        self.html = html

    def inner(self, *args, **kwargs):
        return self.html
    

class DivFormElement(FormLayoutElement):
    
    def __init__(self, *fields, **kwargs):
        super(DivFormElement,self).__init__(**kwargs)
        self.fields = fields

    def _innergen(self, djp, form, layout):
        attr = self.flatatt()
        dfields = form.dfields
        for field in self.fields:
            yield '<div{0}>'.format(attr)
            yield self.render_field(djp,dfields[field],layout)
            yield '</div>'
            
    def inner(self, djp, form, layout):
        return '\n'.join(self._innergen(djp, form, layout))
    

class FormLayout(BaseFormLayout):
    '''Base form class for form layout design'''
    
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
    default_element = DivFormElement
    
    def __init__(self, *fields, **kwargs):
        super(FormLayout,self).__init__(**kwargs)
        self._allfields = []
        self.add(*fields)
        
    def render(self, djp, form, inputs, **keys):
        ctx  = {'layout':self}
        html = ''
        template = self.template
        for field in self._allfields:
            key = field.key
            if key and key in keys:
                html += field.render(djp, form, self, inner = keys[key])
            else:
                h = field.render(djp, form, self)
                if key and template:
                    ctx[field.key] = h
                else:
                    html += h
        
        missing_fields = self.get_missing_fields(form)        
        if missing_fields:
            fset  = self.default_element(*missing_fields).addClass(self.default_style)
            html += fset.render(djp,form,self)
               
        ctx['has_inputs'] = len(inputs)
        ctx['inputs'] = (input.render(djp) for input in inputs)
        ctx['form']   = html
        ctx['messages'] = ''
        
        return loader.render(template, ctx)
        
    def add(self,*fields):
        '''Add *fields* to all fields.
A field must be an instance of :class:`djpcms.forms.layout.FormLayoutElement`.'''
        for field in fields:
            if isinstance(field,FormLayoutElement):
                if not field.default_style:
                    field.default_style = self.default_style
                field.make_classes()
                self._allfields.append(field)
                if field.key:
                    setattr(self,field.key,field)
    
    def get_rendered_fields(self,form):
        rf = getattr(form, '_rendered_fields', {})
        form._rendered_fields = rf
        return rf
    
    def get_missing_fields(self,form):
        mf = []
        rendered_fields = self.get_rendered_fields(form)
        for field in form.fields:
            if not field.name in rendered_fields:
                mf.append(field.name)
        return mf

    def json_messages(self, f):
        '''Convert errors in form into a JSON serializable dictionary with keys
        given by errors html id.'''
        dfields = f._fields_dict
        ListDict = jhtmls()
        self._add(ListDict,dfields,f.errors,self.form_error_class)
        self._add(ListDict,dfields,f.messages,self.form_message_class)
        return ListDict
        
    def _add(self, ListDict, fields, container, msg_class):
        # Add messages to the list dictionary
        for name,msg in container.items():
            if name in fields:
                name = '#' + fields[name].errors_id
            else:
                name = '.' + self.form_messages_container_class
            ListDict.add(name,
                         List(data = msg, cn = msg_class).render(),
                         alldocument = False)
