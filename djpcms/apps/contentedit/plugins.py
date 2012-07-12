import json

from djpcms import forms, html
from djpcms.cms.plugins.apps import RenderObject
from djpcms.cms.formutils import form_kwargs
from djpcms.cms import PermissionDenied
from djpcms.utils.text import mark_safe


def get_site_content(form):
    from djpcms.models import SiteContent
    if SiteContent:
        return SiteContent.objects.all()
    else:
        return ()


class Text(RenderObject):
    '''The text plugin allows to write content in a straightforward manner.
You can use several different markup languages or simply raw HTML.'''
    name = "text"
    description = "Html"
    
    def for_model(self, request):
        return request.view.root.internals.get('SiteContent')
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return ''