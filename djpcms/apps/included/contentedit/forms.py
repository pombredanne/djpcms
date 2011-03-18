import djpcms
from djpcms import sites, forms, empty_choice
from djpcms.utils import force_str, slugify
from djpcms.plugins import get_plugin, plugingenerator, wrappergenerator

__all__ = ['TemplateForm',
           'PageForm',
           'ContentBlockForm']


def get_templates():
    from djpcms.models import InnerTemplate
    return InnerTemplate.objects.all()


def siteapp_choices():
    return sites.get_site().choices


class TemplateForm(forms.Form):
    name = forms.CharField()
    template = forms.CharField(widget = forms.TextArea)  


class PageForm(forms.Form):
    '''Inline Editing Page form'''
    url = forms.CharField(required = False)
    title = forms.CharField(label = 'Page title', required = False)
    link = forms.CharField(label = 'Text to display in links', required = False)
    in_navigation = forms.IntegerField(help_text = 'An integer greater or equal to 0 used for link ordering in menus.',
                                       initial = 1,
                                       required = False)
    inner_template = forms.ChoiceField(choices = get_templates)   
    requires_login = forms.BooleanField()
    soft_root = forms.BooleanField()
    layout = forms.ChoiceField(choices = ((0,'fixed'),(1,'float')))
    
    def clean_url(self, value):
        try:
            page = self.mapper.get(url = value)
        except self.mapper.DoesNotExist:
            page = None
        if page and self.instance != page:
            raise forms.ValidationError('A page with url "{0}" is already available'.format(value))
        return value
    

class PluginChoice(forms.ChoiceField):
    widget = forms.Select(cn = sites.settings.HTML_CLASSES.ajax)
    
    def __init__(self, *args, **kwargs):
        super(PluginChoice,self).__init__(*args, **kwargs)
    
    def _clean(self, value):
        '''Overried default value to return a Content Type object
        '''
        value = get_plugin(value) 
        if not value:
            raise forms.ValidationError('%s not a plugin object' % name)
        return value

    
class ContentBlockForm(forms.Form):
    url = forms.CharField(widget=forms.HiddenInput, required = False)
    title = forms.CharField(required = False)
    plugin_name = PluginChoice(label = 'Plugin', choices = plugingenerator)
    container_type = forms.ChoiceField(label = 'Container',
                                       choices = wrappergenerator,
                                       help_text = 'A HTML element which wraps the plugin before it is rendered in the page.')
    for_not_authenticated = forms.BooleanField(default = False)
    view_permission = forms.CharField(required = False)
    requires_login = forms.BooleanField(default = False)
        
    def save(self, commit = True):
        pt = self.cleaned_data.pop('plugin_name')
        pe = self.cleaned_data.pop('view_permission')
        instance = self.instance
        if pt:
            instance.plugin_name = pt.name
        else:
            instance.plugin_name = ''
        if pe:
            instance.requires_login = True
        cb = super(ContentBlockForm,self).save(commit = commit)
        if commit and cb.id:
            ObjectPermission.objects.set_view_permission(cb, groups = pe)
        return cb

    def clean(self):
        cd = self.cleaned_data
        rl = cd['requires_login']
        na = cd['for_not_authenticated']
        if rl and na:
            raise forms.ValidationError("Cannot select 'requires login'\
 and 'for not authenticated' at the same time.")


def _getid(obj):
    if obj:
        try:
            return obj.id
        except:
            return obj
    else:
        return obj
        