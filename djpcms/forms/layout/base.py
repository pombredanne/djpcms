from inspect import isclass

from djpcms.forms.html import HtmlWidget
from djpcms.template import loader

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
    '''Base form class for programmatic form layout design'''
    field_template = "djpcms/uniforms/field.html"
    
    def __init__(self, auto_id='id_{0[html_name]}', **kwargs):
        super(FormLayout,self).__init__(**kwargs)
        self._allfields = []
        self.auto_id = auto_id
        
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
        rf = getattr(form, '_rendered_fields', [])
        form.rendered_fields = rf
        return rf


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
        if isinstance(field,FormLayoutElement):
            return field.render(djp,layout)
        form = field.form
        rendered_fields = layout.get_rendered_fields(form)
        if not field in rendered_fields:
            rendered_fields.append(field)
        else:
            raise Exception("A field should only be rendered once: %s" % field)
        widget = field.field.widget
        if isclass(widget):
            widget = widget()
        ctx = {'label': None if self.default_style == nolabel else field.label,
               'required_tag': self.required_tag or layout.required_tag,
               'field':field,
               'auto_id':layout.auto_id.format(field.__dict__),
               'widget':widget.render(djp,field)}
        field_template = self.field_template or layout.field_template
        return loader.render_to_string(field_template,ctx)



class Html(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to `self`.'''
    def __init__(self, html, **kwargs):
        self.html = loader.mark_safe(html)

    def inner(self, djp, layout):
        return self.html
    