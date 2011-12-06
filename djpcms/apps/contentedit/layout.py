from djpcms import forms, html
from djpcms.forms.layout import uniforms as uni

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm',
           'ContentBlockHtmlForm',
           'HtmlEditContentForm',
           'BlockLayoutFormHtml']

PLUGIN_DATA_FORM_CLASS = 'plugin-data-form'

HtmlTemplateForm = forms.HtmlForm(TemplateForm)

HtmlPageForm = forms.HtmlForm(
    PageForm,
    layout = uni.Layout(
                uni.Columns(('title','link','in_navigation'),
                            ('layout','inner_template','doctype'),
                            ('url','requires_login','soft_root'))
                          ),
    inputs = (('done',forms.SAVE_KEY),
              ('save',forms.SAVE_AND_CONTINUE_KEY)
              )
)


BlockLayoutFormHtml = forms.HtmlForm(
    BlockLayoutForm,
    inputs = (('change','change'),)
    )

ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    inputs = (('save',forms.SAVE_KEY),),
    layout = uni.Layout(
                  uni.Fieldset('plugin_name','container_type',
                                    'title','view_permission'),
                  uni.Columns(('for_not_authenticated',),
                                   ('requires_login',),
                                   default_style=uni.inlineLabels3),
                  html.Html(key = 'plugin',
                            tag = 'div',
                            default_class = PLUGIN_DATA_FORM_CLASS,
                            description = "Add an Html element with key so that\
 we can inject extra form data at runtime")
                )
)


HtmlEditContentForm = forms.HtmlForm(
    EditContentForm,
    layout = uni.Layout(
                          uni.Fieldset('title','markup'),
                          uni.Fieldset('body', default_style=uni.blockLabels)
        )
)


