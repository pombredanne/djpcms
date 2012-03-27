from djpcms import forms, html
from djpcms.forms.layout import uniforms as uni

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm',
           'ContentBlockHtmlForm',
           'HtmlEditContentForm']


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


ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    inputs = (('save',forms.SAVE_KEY),),
    layout = uni.Layout(
                  uni.Fieldset('plugin_name','container_type',
                                    'title','view_permission'),
                  uni.Columns(('for_not_authenticated',),
                                   ('requires_login',),
                                   default_style=uni.inlineLabels3),
                  html.Html(key = 'plugin')
                )
)


HtmlEditContentForm = forms.HtmlForm(
    EditContentForm,
    layout = uni.Layout(
                          uni.Fieldset('title','markup'),
                          uni.Fieldset('body', default_style=uni.blockLabels)
        )
)


