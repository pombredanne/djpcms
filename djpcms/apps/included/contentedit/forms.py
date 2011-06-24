import djpcms
from djpcms import forms, html, plugins
from djpcms.utils import markups


__all__ = ['TemplateForm',
           'PageForm',
           'ContentBlockForm',
           'EditContentForm']


def get_templates(*args):
    from djpcms.models import InnerTemplate
    return InnerTemplate.objects.all()


class TemplateForm(forms.Form):
    name = forms.CharField()
    template = forms.CharField(widget = html.TextArea)  


class PageForm(forms.Form):
    '''Inline Editing Page form'''
    url = forms.CharField(initial = '/')
    title = forms.CharField(label = 'Page title',
                            required = False)
    link = forms.CharField(label = 'Text to display in links',
                           required = False)
    in_navigation = forms.IntegerField(help_text = 'An integer greater or equal to 0 used for link ordering in menus.',
                                       initial = 0,
                                       required = False)
    inner_template = forms.ChoiceField(choices = get_templates,
                                       required = False)   
    requires_login = forms.BooleanField()
    soft_root = forms.BooleanField()
    doctype = forms.ChoiceField(choices = html.html_choices,
                                initial = html.htmldefaultdoc)
    layout = forms.ChoiceField(choices = ((0,'fixed'),(1,'float')),
                               initial = 0)
    
    def clean_url(self, value):
        if self.mapper:
            try:
                page = self.mapper.get(url = value)
            except self.mapper.DoesNotExist:
                page = None
            if page and self.instance != page:
                raise forms.ValidationError('A page with url "{0}" is already available'.format(value))
        else:
            raise forms.ValidationError('No page model defined. Cannot validate')
        return value
    

class PluginChoice(forms.ChoiceField):
    widget = html.Select(default_class = 'ajax')
    
    def __init__(self, *args, **kwargs):
        super(PluginChoice,self).__init__(*args, **kwargs)
    
    def _clean(self, value, bfield):
        '''Overried default value to return a Content Type object
        '''
        value = plugins.get_plugin(value) 
        if not value:
            raise forms.ValidationError('%s not a plugin object' % name)
        return value

    
class ContentBlockForm(forms.Form):
    url = forms.HiddenField(required = False)
    title = forms.CharField(required = False)
    plugin_name = PluginChoice(label = 'Plugin',
                               choices = plugins.plugingenerator)
    container_type = forms.ChoiceField(label = 'Container',
                                       widget = html.Select(default_class = 'ajax'),
                                       choices = plugins.wrappergenerator,
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
        #if commit and cb.id:
        #    ObjectPermission.objects.set_view_permission(cb, groups = pe)
        return cb

    def clean(self):
        cd = self.cleaned_data
        rl = cd['requires_login']
        na = cd['for_not_authenticated']
        if rl and na:
            raise forms.ValidationError("Cannot select 'requires login'\
 and 'for not authenticated' at the same time.")



class EditContentForm(forms.Form):
    '''Form used to edit and add Content'''
    title   = forms.CharField()
    body    = forms.CharField(widget = html.TextArea,
                              required = False)
    markup  = forms.ChoiceField(choices = lambda bf : tuple(markups.choices()),
                                initial = lambda form : markups.default(),
                                required = False)
        

def _getid(obj):
    if obj:
        try:
            return obj.id
        except:
            return obj
    else:
        return obj
        