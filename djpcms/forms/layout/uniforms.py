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
from djpcms.html import get_grid960
from djpcms.template import loader

from .base import FormLayout, FormLayoutElement, Inputs, check_fields,\
                  render_field
from .tablefield import TableRelatedFieldset


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
    
    def check_fields(self, missings):
        check_fields(self.fields,missings)
                
    def inner(self, djp, widget, keys):
        html = '\n'.join((render_field(self, djp, field, widget) for field in self.fields))
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
        if not self.template or self.template_name:
            self.template_name = self.template_dict.get(ncols,None)
        if not self.template or self.template_name:
            raise ValueError('Template not available in uniform Column.')

    def check_fields(self, missings):
        for column in self.columns:
            check_fields(column,missings)
            
    def get_context(self, djp, widget):
        context = {}
        div = html.Widget('div')
        for i,column in enumerate(self.columns):
            inner = '\n'.join(render_field(self, djp, field, widget) for field in column)
            context['content%s' % i] = div.render(djp,inner)
            
        context['grid'] = get_grid960(djp)
        return context    

class Layout(FormLayout):
    '''Main class for defining the layout of a uniform.'''
    default_style  = 'inlineLabels'
    form_class = 'uniForm'
    default_element = Fieldset
    template = loader.template_class('''\
{% if csrf_token %}{{ csrf_token }}{% endif %}
<div class="{{ maker.form_messages_container_class }} ctrlHolder">{{ messages }}</div>
{% for child in children %}
{{ child }}{% endfor %}{% for si in inputs %}
{{ si }}{% endfor %}''')
    field_template = loader.template_class("""\
{% if is_hidden %}{{ widget }}{% else %}
<div class='ctrlHolder{% if error %} error{% endif %}{% if field.field.required %} required{% endif %}'>
    <div id='{{ field.errors_id }}'>{{ errors }}
    </div>{% if ischeckbox %}
    <p class='label'></p>
    <div class='field-widget'>
    <label for='{{ field.id }}'>
     {{ widget }}{% if label %}
      {{ label }}{% endif %}
    </label>
    {% if field.help_text %}
    <div id="hint_{{ field.id }}" class="formHint">{{ field.help_text }}</div>{% endif %}
    </div>{% else %}{% if label %}
    <label for="{{ field.id }}" class="label">
      {{ label }}
    </label>{% endif %}
    <div class="field-widget input {{ name }}">
      {{ widget }}
    </div>{% if field.help_text %}
    <div id='hint_{{ field.id }}' class='formHint'>{{ field.help_text }}</div>{% endif %}
    {% endif %}
</div>{% endif %}""")

