import json

from djpcms import sites, forms
from djpcms.plugins import DJPplugin
from djpcms.forms.utils import form_kwargs
from djpcms.forms.layout import uniforms
from djpcms.template import mark_safe
from djpcms.core.exceptions import PermissionDenied
from djpcms.models import SiteContent
from djpcms.utils import markups


class EditingForm(forms.Form):
    pass


class ChangeTextContent(forms.Form):
    '''
    Form for changing text content during inline editing
    '''
    site_content = forms.ModelChoiceField(choices = SiteContent.objects.all,
                                          empty_label="New Content",
                                          required = False,
                                          widget = forms.Select(cn = sites.settings.HTML_CLASSES.ajax))
    new_content  = forms.CharField(label = 'New content unique title',
                                   help_text = 'When creating a new content give a unique name you like',
                                   required = False)
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        self.user = request.user
        queryset = self.queryset_for_user()
        super(ChangeTextContent,self).__init__(*args,**kwargs)
        
    def queryset_for_user(self):
        if self.user.is_authenticated() and self.user.is_active:
            pass            
        
    def clean_new_content(self):
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
        


class EditContentForm(EditingForm):
    markup       = forms.ChoiceField(choices = markups.choices,
                                     initial = markups.default,
                                     required = False)
    
    #layout = uniforms.FormLayout(uniforms.Fieldset('markup',elem_css=uniforms.inlineLabels),
    #                            uniforms.Fieldset('body',elem_css='%s editing' % uniforms.blockLabels2))
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        self.user = request.user
        super(EditContentForm,self).__init__(*args,**kwargs)
        

    
class Text(DJPplugin):
    '''The text plugin allows to write content in a straightforward manner.
You can use several different markup languages or simply raw HTML.'''
    name               = "text"
    description        = "Text Editor"
    long_description   = "Write text or raw HTML"
    form_withrequest   = True
    form               = ChangeTextContent
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return ''
            
    def render(self, djp, wrapper, prefix, site_content = None, **kwargs):
        if site_content:
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                return mark_safe('\n'.join(['<div class="djpcms-text-content">',
                                            site_content.htmlbody(),
                                            '</div>']))
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
            
    def save(self, pform):
        text = pform.update()
        return json.dumps({'site_content': text.id})
        