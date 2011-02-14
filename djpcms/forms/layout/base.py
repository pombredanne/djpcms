from inspect import isclass

from djpcms.forms.html import HtmlWidget, List
from djpcms.template import loader
from djpcms.utils.ajax import jhtmls

__all__ = ['FormLayout',
           'FormLayoutElement',
           'Html',
           'nolabel']


nolabel = 'nolabel'


class BaseFormLayout(HtmlWidget):
    '''Base form class for programmatic form layout design'''
    field_template = None
    default_style = None
    required_tag = ''
    
    def __init__(self, default_style = None, required_tag = None,
                 field_template = None, **kwargs):
        self.default_style = default_style or self.default_style
        self.required_tag = required_tag or self.required_tag
        self.default_style = default_style or self.default_style
        super(BaseFormLayout,self).__init__(**kwargs)


class FormLayout(BaseFormLayout):
    '''Base form class for form layout design'''
    
    '''Form template'''
    field_template = "djpcms/uniforms/field.html"
    '''Template file for rendering form fields'''
    form_class = None
    '''form css class'''
    form_messages_container_class = 'form-messages'
    '''Class used to hold form-wide messages'''
    form_error_class = 'errorlist'
    '''Class for form errors'''
    form_message_class = 'messagelist'
    '''Class for form messages'''
    
    def __init__(self, **kwargs):
        super(FormLayout,self).__init__(**kwargs)
        self._allfields = []
        
    def render(self, djp, form, inputs):
        raise NotImplementedError
    
    def add(self,*fields):
        '''Add *fields* to all fields. A field must be an instance of :class:`FormLayoutElement`.'''
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


class FormLayoutElement(BaseFormLayout):
    '''Base form class for programmatic form layout design'''
    elem_css = None
    template = None
    
    def __init__(self, key = None, elem_css = None, **kwargs):
        super(FormLayoutElement,self).__init__(**kwargs)
        self.key = key
        self.elem_css = elem_css or self.elem_css
        
    def make_classes(self):
        self.addClass(self.elem_css).addClass(self.default_style)
        
    def render_field(self, djp, field, layout):
        '''Render a single field'''
        if isinstance(field,FormLayoutElement):
            return field.render(djp,layout)
        form = field.form
        rendered_fields = layout.get_rendered_fields(form)
        if not field.name in rendered_fields:
            rendered_fields[field.name] = field
        else:
            raise Exception("A field should only be rendered once: %s" % field)
        widget = field.field.widget
        if isclass(widget):
            widget = widget()
        self.add_widget_classes(field,widget)
        ctx = {'label': None if self.default_style == nolabel else field.label,
               'required_tag': self.required_tag or layout.required_tag,
               'field':field,
               'error': form.errors.get(field.name,''), 
               'widget':widget.render_from_field(djp, field),
               'is_hidden': widget.is_hidden,
               'ischeckbox':widget.ischeckbox()}
        field_template = self.field_template or layout.field_template
        return loader.render_to_string(field_template,ctx)

    def add_widget_classes(self, field, widget):
        pass


class Html(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, html, **kwargs):
        self.html = loader.mark_safe(html)

    def inner(self, djp, layout):
        return self.html
    