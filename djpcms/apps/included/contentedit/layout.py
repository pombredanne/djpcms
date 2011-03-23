from djpcms import forms
from djpcms.forms.layout import uniforms

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm']

PLUGIN_DATA_FORM_CLASS = 'plugin-data-form'

HtmlTemplateForm = forms.HtmlForm(TemplateForm)

HtmlPageForm = forms.HtmlForm(
    PageForm,
    layout = uniforms.Layout(
                          uniforms.Fieldset('url','title','link','in_navigation','inner_template'),
                          uniforms.Row('requires_login','soft_root')
                          )
)


ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    layout = uniforms.Layout(
                          uniforms.Fieldset('plugin_name','container_type','title',
                                            'view_permission'),
                          uniforms.Columns(('for_not_authenticated',),
                                           ('requires_login',),
                                           default_style=uniforms.inlineLabels3),
                          uniforms.Html(tag = 'div').addClass(PLUGIN_DATA_FORM_CLASS)
                           )
)
