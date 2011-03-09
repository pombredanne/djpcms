from djpcms import forms
from djpcms.forms.layout import uniforms

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm']

HtmlTemplateForm = forms.HtmlForm(TemplateForm)

HtmlPageForm = forms.HtmlForm(
    PageForm,
    submits = (('change', '_save'),)
)
    

ChildFormHtml = forms.HtmlForm(
    ChildPageForm,
    submits = (('create', '_child'),)
)


ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    layout = uniforms.Layout(
                          uniforms.Fieldset('plugin_name','container_type','title',
                                            'view_permission'),
                          uniforms.Columns(('for_not_authenticated',),
                                           ('requires_login',),
                                           default_style=uniforms.inlineLabels3)
                           )
)
