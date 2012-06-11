from copy import copy

from djpcms import forms, html
from djpcms.utils import orms, markups
from djpcms.utils.text import nicename
from djpcms.html import html_choices, htmldefaultdoc
from djpcms.html.layout import grid_systems, grids
from djpcms.cms import plugins 


__all__ = ['TemplateForm',
           'PageForm',
           'ContentBlockForm',
           'EditContentForm']


def get_layout_templates(bfield):
    if bfield.request:
        root = bfield.request.view.root
        for name in root._page_layout_registry:
            yield name, nicename(name)
    
grid_choices = lambda bfield: ((name, nicename(name)) for name in grids())

def initial_layout(f):
    request = f.request
    if request:
        return request.view.settings.LAYOUT_GRID_SYSTEM
    else:
        return ''


class TemplateForm(forms.Form):
    name = forms.CharField()
    template = forms.CharField(widget = html.TextArea())  


class PageForm(forms.Form):
    '''Inline Editing Page form'''
    url = forms.CharField(initial='/')
    title = forms.CharField(label='Page title', required=False)
    link = forms.CharField(help_text='Text to display in links',
                           required=False)
    in_navigation = forms.IntegerField(
                        initial=0,
                        required=False,
                        label='position',
                        help_text="An integer greater or equal 0 used for "\
                                  " link ordering in menus. If zero the page "\
                                  "won't appear in naviagtions")
    layout = forms.ChoiceField(choices=get_layout_templates,
                               label='Page layout')
    inner_template = forms.ChoiceField(label='content grid',
                                       choices=grid_choices)
    grid_system = forms.ChoiceField(choices=grid_systems)
    requires_login = forms.BooleanField()
    soft_root = forms.BooleanField()
    doctype = forms.ChoiceField(choices=html_choices, initial=htmldefaultdoc)
    
    def clean_url(self, value):
        if self.mapper:
            try:
                page = self.mapper.get(url = value)
            except self.mapper.DoesNotExist:
                page = None
            if page and self.instance != page:
                raise forms.ValidationError('A page with url "{0}"\
 is already available'.format(value))
        else:
            raise forms.ValidationError('No page model defined.')
        return value
    

class PluginChoice(forms.ChoiceField):
    widget = html.Select(cn='ajax')
    
    def _clean(self, value, bfield):
        '''Overried default value to return a Content Type object
        '''
        value = plugins.get_plugin(value) 
        if not value:
            raise forms.ValidationError('%s not a plugin object' % name)
        return value

    
class ContentBlockForm(forms.Form):
    '''Form for editing a content block within a page.'''
    url = forms.HiddenField(required = False)
    title = forms.CharField(required = False)
    plugin_name = PluginChoice(label = 'Plugin',
                               choices = plugins.plugingenerator)
    container_type = forms.ChoiceField(
                            label = 'Container',
                            widget = html.Select(cn='ajax'),
                            choices = plugins.wrappergenerator,
                            help_text = 'A HTML element which wraps the plugin\
 before it is rendered in the page.')
    for_not_authenticated = forms.BooleanField(default = False)
    view_permission = forms.CharField(required = False)
    requires_login = forms.BooleanField(default = False)
        
    def save(self, commit = True):
        data = self.cleaned_data
        pt = data.pop('plugin_name')
        pe = data.pop('view_permission')
        instance = self.instance
        if pt:
            instance.plugin_name = pt.name
        else:
            instance.plugin_name = ''
        if pe:
            instance.requires_login = True
        if 'container_type' in data:
            instance.container_type = data['container_type'] 
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
    body    = forms.CharField(widget=html.TextArea(cn='taboverride'),
                              required=False)
    markup  = forms.ChoiceField(choices=lambda bf : tuple(markups.choices()),
                                initial=lambda form : markups.default(),
                                required=False)
        

def _getid(obj):
    if obj:
        try:
            return obj.id
        except:
            return obj
    else:
        return obj
        