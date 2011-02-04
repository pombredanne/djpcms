from djpcms.template import loader
from djpcms.utils.ajax import jhtmls

from .base import FormLayout, FormLayoutElement


inlineLabels   = 'inlineLabels'
inlineLabels2  = 'inlineLabels fullwidth'
inlineLabels3  = 'inlineLabels auto'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'


def default_csrf():
    return 'django.middleware.csrf.CsrfViewMiddleware' in sites.settings.MIDDLEWARE_CLASSES


    
def get_rendered_fields(form):
    rf = getattr(form, 'rendered_fields', [])
    form.rendered_fields = rf
    return rf


class Fieldset(FormLayoutElement):
    '''A :class:`FormLayoutElement` which renders to a <fieldset>.'''
    tag = 'fieldset'
    
    def __init__(self, *fields, **kwargs):
        legend_html = kwargs.pop('legend','')
        super(Fieldset,self).__init__(**kwargs)
        if legend_html:
            legend_html = '<legend>{0}</legend>'.format(legend_html)
        self.legend_html = legend_html
        self.fields = fields

    def inner(self, djp, layout):
        render_field = self.render_field
        html = '\n'.join((render_field(djp, field, layout) for field in self.fields))
        if html:
            return self.legend_html + '\n' + html
        else:
            return html


class Row(Fieldset):
    '''A :class:`FormLayoutElement` which renders to a <div>.'''
    tag = 'div'
    elem_css = "formRow"


class Columns(FormLayoutElement):
    '''A :class:`FormLayoutElement` whiche defines a set of columns. Renders to a set of <div>.'''
    elem_css  = "formColumn"
    templates = {2: 'djpcms/yui/yui-simple.html',
                 3: 'djpcms/yui/yui-simple3.html'}
    
    def __init__(self, *columns, **kwargs):
        super(Columns,self).__init__(**kwargs)
        self.columns = columns
        ncols = len(columns)
        if not self.template:
            self.template = self.templates.get(ncols,None)
        if not self.template:
            raise ValueError('Template not available in uniform Column.')

    def _render(self, layout):
        css = self._css(layout)
        content = {}
        for i,column in enumerate(self.columns):
            output = '<div class="%s">' % css
            for field in column:
                output += render_field(field, form, layout, self.css)
            output += '</div>'
            content['content%s' % i] = loader.mark_safe(output)
        return loader.render_to_string(self.template, content)
    

class Layout(FormLayout):
    '''Main class for defining the layout of a uniform.
'''
    template = "djpcms/uniforms/uniform.html"
    default_style  = 'inlineLabels'
    form_class = 'uniForm'
    
    def __init__(self, *fields, **kwargs):
        super(Layout,self).__init__(**kwargs)
        self.add(*fields)
    def render(self, djp, form, inputs):
        '''Render the uniform layout of *form*.
This function is called by an instance of
:class:`djpcms.forms.html.FormWidget`'''
        ctx  = {}
        html = ''
        for field in self._allfields:
            h = field.render(form, self)
            if field.key and self.template:
                ctx[field.key] = h
            else:
                html += h
        
        missing_fields = []
        rendered_fields = get_rendered_fields(form)
        for field in form.fields:
            if not field.name in rendered_fields:
                missing_fields.append(field)
        
        if missing_fields:
            fset  = Fieldset(*missing_fields).addClass(self.default_style)
            html += fset.render(djp,self)
               
        ctx['has_inputs'] = len(inputs)
        ctx['inputs'] = (input.render(djp) for input in inputs)
        ctx['form']   = loader.mark_safe(html)
        ctx['errors'] = ''
        
        return loader.render_to_string(self.template, ctx)
        
    
      