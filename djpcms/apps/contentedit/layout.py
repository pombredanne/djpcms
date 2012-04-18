from djpcms import forms, html
from djpcms.forms import layout as uni

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm',
           'ContentBlockHtmlForm',
           'HtmlEditContentForm']


HtmlTemplateForm = forms.HtmlForm(TemplateForm)

HtmlPageForm = forms.HtmlForm(
    PageForm,
    layout = uni.FormLayout(
                
                uni.Columns(
                    ('doctype','layout','inner_template','grid_system'),
                    ('title','link','in_navigation','url'),
                    ('requires_login','soft_root',uni.SUBMITS))
                ),
    inputs = (('save',forms.SAVE_AND_CONTINUE_KEY),
              )
)


ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    inputs = (('save',forms.SAVE_KEY),),
    layout = uni.FormLayout(
                  uni.Fieldset('plugin_name','container_type',
                                    'title','view_permission'),
                  uni.Columns(('for_not_authenticated',),
                                   ('requires_login',),
                                   default_style=uni.inlineLabels3),
                  html.WidgetMaker(tag='div', key='plugin')
                )
)


HtmlEditContentForm = forms.HtmlForm(
    EditContentForm,
    layout = uni.FormLayout(
                          uni.Columns('title','markup',uni.SUBMITS),
                          uni.Fieldset('body', default_style=uni.blockLabels)
        )
)


