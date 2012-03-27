from copy import copy

import djpcms
from djpcms import forms, html, plugins
from djpcms.core import orms
from djpcms.html import layout
from djpcms.utils import markups
from djpcms.utils.text import nicename


__all__ = ['TemplateForm',
           'PageForm',
           'ContentBlockForm',
           'EditContentForm']


def get_templates(bfield):
    for name in layout.page_layouts(grid = True):
        yield name, nicename(name)
    

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
    url = forms.CharField(initial = '/',
                          widget = html.TextInput(readonly='readonly'))
    title = forms.CharField(label = 'Page title',
                            required = False)
    link = forms.CharField(label = 'Text to display in links',
                           required = False)
    in_navigation = forms.IntegerField(help_text = 'An integer greater or equal\
 to 0 used for link ordering in menus.',
                                       initial = 0,
                                       required = False)
    inner_template = forms.ChoiceField(choices = get_templates,
                                       required = False)   
    requires_login = forms.BooleanField()
    soft_root = forms.BooleanField()
    doctype = forms.ChoiceField(choices = layout.html_choices,
                                initial = layout.htmldefaultdoc)
    layout = forms.ChoiceField(choices = lambda r : copy(html.grid_systems),
                               initial = initial_layout)
    
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
    widget = html.Select(default_class = 'ajax')
    
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
                            widget = html.Select(default_class = 'ajax'),
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
        