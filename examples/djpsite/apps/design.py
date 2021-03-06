from datetime import datetime

from djpcms import forms, views, html
from djpcms.cms.formutils import get_form
from djpcms.forms import layout as uni
from djpcms.apps.color import ColorField
import djpcms.apps.ui.style
from djpcms.media.style import cssv

from stdnet import odm


class Theme(odm.StdModel):
    timestamp = odm.DateTimeField(default=datetime.now)
    data = odm.JSONField()
    
    class Meta:
        ordering = '-timestamp'
    
    
def theme_field(elem, field=forms.CharField):
    name = elem.name
    return (name, field, str(elem))
    
class AddTheme(forms.Form):
    body = forms.FieldList((theme_field(cssv.body.font_family),
                            theme_field(cssv.body.font_size),
                            theme_field(cssv.body.radius),
                            theme_field(cssv.body.color, ColorField)),
                           withprefix=False)


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
    
    def render_instance_default(self, request, instance, **kwargs):
        return get_form(request, ThemeInputsHtml)
    