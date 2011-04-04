'''\
This module complements the django forms library by adding ajax functionality,
inline forms, and custom layout based on uni-form_ style.

Using uniforms to render form is easy::

    from djpcms import forms
    from djcms.forms.layout.uniforms import Layout, Fieldset, blockLabels2
    
    class MyForm(forms.Form):
        name = forms.CharField()

    HtmlMyForm = forms.HtmlForm(
       MyForm,
       layout = Layout(Fieldset('name'))
    )


There are three types of layout:

* ``inlineLabels``
* ``blockLabels``
* ``blockLabels2`` (default)   

.. _uni-form: http://sprawsm.com/uni-form/
'''
from .base import FormLayout, FormLayoutElement, Html


inlineLabels   = 'inlineLabels'
inlineLabels2  = 'inlineLabels fullwidth'
inlineLabels3  = 'inlineLabels auto'
blockLabels    = 'blockLabels'
blockLabels2   = 'blockLabels2'
inlineFormsets = 'blockLabels2'


WIDGET_CLASSES = {'CharField': 'textInput',
                  'DateField': 'dateInput'}


def default_csrf():
    return 'django.middleware.csrf.CsrfViewMiddleware' in sites.settings.MIDDLEWARE_CLASSES


class UniFormElement(FormLayoutElement):
            
    def add_widget_classes(self, field, widget):
        cls = field.field.__class__.__name__
        if cls in WIDGET_CLASSES:
            widget.addClass(WIDGET_CLASSES[cls])


class Fieldset(UniFormElement):
    '''A :class:`FormLayoutElement` which renders to a <fieldset>.'''
    tag = 'fieldset'
    
    def __init__(self, *fields, **kwargs):
        super(Fieldset,self).__init__(**kwargs)
        self.fields = fields

    def inner(self, djp, form, layout):
        render_field = self.render_field
        dfields = form.dfields
        html = '\n'.join((render_field(djp, dfields[field], layout) for field in self.fields))
        if html:
            return self.legend_html + '\n' + html
        else:
            return html
      

class Row(Fieldset):
    '''A :class:`FormLayoutElement` which renders to a <div>.'''
    tag = 'div'
    elem_css = "formRow"


class Columns(UniFormElement):
    '''A :class:`FormLayoutElement` whiche defines a set of columns. Renders to a set of <div>.'''
    elem_css  = "formColumn"
    template_dict = {2: 'djpcms/yui/yui-simple.html',
                     3: 'djpcms/yui/yui-simple3.html'}
    
    def __init__(self, *columns, **kwargs):
        super(Columns,self).__init__(**kwargs)
        self.columns = columns
        ncols = len(columns)
        if not self.template:
            self.template = self.template_dict.get(ncols,None)
        if not self.template:
            raise ValueError('Template not available in uniform Column.')

    def get_context(self, context, djp, form, layout):
        render_field = self.render_field
        dfields = form.dfields
        
        def _data(column):
            yield '<div>'
            for field in column:
                if not isinstance(field,FormLayoutElement):
                    field = dfields[field]
                    yield render_field(djp, field, layout)
                else:
                    yield field.render(djp,form,layout)
            yield '</div>'
            
        for i,column in enumerate(self.columns):
            context['content%s' % i] = '\n'.join(_data(column))
            
        return context    

class Layout(FormLayout):
    '''Main class for defining the layout of a uniform.'''
    template = "djpcms/form-layouts/uniform.html"
    field_template = "djpcms/form-layouts/field.html"
    default_style  = 'inlineLabels'
    form_class = 'uniForm'
    default_element = Fieldset
    