import json

from djpcms import forms, html
from djpcms.plugins.apps import RenderObject
from djpcms.forms.utils import form_kwargs
from djpcms.core.exceptions import PermissionDenied
from djpcms.utils import mark_safe


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
    description = "Text Editor"
    long_description = "Write text or raw HTML"
    
    def for_model(elf, request):
        return request.view.SiteContent
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return ''
            
    def __render(self, djp, wrapper, prefix, site_content = None, **kwargs):
        if site_content:
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                return '\n'.join(('<div class="djpcms-text-content">',
                                  site_content.htmlbody(),
                                  '</div>'))
            except Exception as e:
                if djp.settings.DEBUG:
                    return str(e) 
                else:
                    return ''
        else:
            return ''
    
    def edit_form(self, djp, site_content = None, **kwargs):
        if site_content:
            try:
                obj = SiteContent.objects.get(id = int(site_content))
            except Exception as e:
                return None
            # Check for permissions
            if has_permission(djp.request.user,get_change_permission(obj), obj):
                return EditContentForm(**form_kwargs(request = djp.request,
                                                     instance = obj,
                                                     withrequest = True,
                                                     **kwargs))
            else:
                raise PermissionDenied("Cannot edit '%s'. You don't have the right permissions" % obj)
            
        
