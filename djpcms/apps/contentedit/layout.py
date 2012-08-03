from djpcms import forms, html, media
from djpcms.forms import layout as uni

from .forms import *

__all__ = ['HtmlTemplateForm',
           'HtmlPageForm',
           'ContentBlockHtmlForm',
           'HtmlEditContentForm']


HtmlTemplateForm = forms.HtmlForm(TemplateForm)

HtmlPageForm = forms.HtmlForm(
    PageForm,
    layout=uni.FormLayout(
        uni.Columns(
            ('doctype', 'layout', 'inner_template', 'grid_system', 'url'),
            ('title', 'link', 'in_navigation', 'soft_root', uni.SUBMITS))
        ),
    inputs=(('save', forms.SAVE_AND_CONTINUE_KEY),)
)

ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    inputs=(('save',forms.SAVE_KEY),),
    layout=uni.FormLayout(
                uni.Fieldset('plugin_name', 'container_type', 'title'),
                uni.Inlineset('for_not_authenticated'),
                html.WidgetMaker(tag='div', key='plugin',
                                 cn='form-plugin-container')
        ),
    media=media.Media(js=['djpcms/plugins/filters.js'])
)

HtmlEditContentForm = forms.HtmlForm(
    EditContentForm,
    layout=uni.FormLayout(
        uni.Columns('title','markup',uni.SUBMITS),
        uni.Tabs(uni.tab('html', uni.Fieldset('body')),
                 uni.tab('javascript', uni.Fieldset('javascript')),
                 default_style=uni.nolabel,
                 tab_type='pills')
        )
)
