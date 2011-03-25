from djpcms import forms
from djpcms.forms.layout import uniforms

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm',
           'ContentBlockHtmlForm',
           'HtmlEditContentForm']

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
                          # Add an Html element with key so that we can inject extra form data
                          uniforms.Html(key = 'plugin', tag = 'div').addClass(PLUGIN_DATA_FORM_CLASS)
                )
)


HtmlEditContentForm = forms.HtmlForm(
    EditContentForm,
    layout = uniforms.Layout(
                          uniforms.Fieldset('title','markup'),
                          uniforms.Fieldset('body', default_style=uniforms.blockLabels)
        )
)


