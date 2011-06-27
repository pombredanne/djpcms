import json

from djpcms import forms, html
from djpcms.plugins.apps import RenderObject
from djpcms.forms.utils import form_kwargs
from djpcms.core.exceptions import PermissionDenied
from djpcms.utils import mark_safe
from djpcms.models import SiteContent


def get_site_content(form):
    from djpcms.models import SiteContent
    if SiteContent:
        return SiteContent.objects.all()
    else:
        return ()


class ChangeTextContent(forms.Form):
    '''
    Form for changing text content during inline editing
    '''
    site_content = forms.ChoiceField(choices = get_site_content,
                                     empty_label="New Content",
                                     required = False,
                                     widget = html.Select(default_class = forms.AJAX))
    new_content  = forms.CharField(label = 'New content unique title',
                                   help_text = 'When creating a new content give a unique name you like',
                                   required = False)
        
    def queryset_for_user(self):
        if self.user.is_authenticated() and self.user.is_active:
            pass            
        
    def clean_new_content(self, sc):
        sc = self.cleaned_data['site_content']
        nc = self.cleaned_data['new_content']
        if not sc:
            if not nc:
                raise forms.ValidationError('New content name must be provided')
            avail = SiteContent.objects.filter(code = nc)
            if avail:
                raise forms.ValidationError('New content name already used')
        return nc
    
    def update(self):
        if self.is_valid():
            cd   = self.cleaned_data
            text = cd.get('site_content',None)
            nc   = cd.get('new_content','')
            # If new_content is available. A new SiteContent object is created
            if not text:
                text = SiteContent(code = nc)
            text.user_last = self.user
            text.save()
            return text
        

    
class Text(RenderObject):
    '''The text plugin allows to write content in a straightforward manner.
You can use several different markup languages or simply raw HTML.'''
    name = "text"
    description = "Text Editor"
    long_description = "Write text or raw HTML"
    for_model = SiteContent
    
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
            
        
