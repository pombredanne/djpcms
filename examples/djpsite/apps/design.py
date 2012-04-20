from datetime import datetime

from djpcms import forms, views, html
from djpcms.forms.utils import get_form
from djpcms.forms import layout as uni
from djpcms.style.plugins.color import ColorField

from stdnet import orm


class Theme(orm.StdModel):
    timestamp = orm.DateTimeField(default=  datetime.now)
    data = orm.JSONField()
    
    class Meta:
        ordering = '-timestamp'
    
    
class AddTheme(forms.Form):
    pass

class ThemeInputs(forms.Form):
    '''input form for theme variables'''
    body = forms.FieldList((('color',ColorField),
                            ('background',ColorField)))
    
    
AddThemeHtml = forms.HtmlForm(
    AddTheme,
    inputs=(('add new theme','add'),),
)

ThemeInputsHtml = forms.HtmlForm(
    ThemeInputs,
    layout=uni.FormLayout(default_style=uni.inlineLabels)
)

class DesignApplication(views.Application):
    pagination = html.Pagination(('id','timestamp'))
    home = views.SearchView()
    add = views.AddView(form=AddThemeHtml, has_plugins=True, name='Add theme')
    view = views.ViewView()
    forms_view = views.View('/forms')
    
    def render_instance(self, request, **kwargs):
        return get_form(request, ThemeInputsHtml)
    