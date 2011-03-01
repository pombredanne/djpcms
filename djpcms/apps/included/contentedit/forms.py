from djpcms import sites, forms, empty_choice
from djpcms.forms.layout import uniforms
from djpcms.utils import force_str, slugify
from djpcms.plugins import get_plugin, plugingenerator, wrappergenerator


def allsites():
    from djpcms.models import Site
    return Site.objects.all()

def siteapp_choices():
    return sites.get_site().choices


def CalculatePageUrl(data, mapper, page):
    '''Calculate url for a page'''
    site = sites.get_site()
    application_view = data['application_view']
    url_pattern  = data['url_pattern']
    parent = data['parent']
    website = data['site']
    if application_view:
        app = site.getapp(application_view)
        if not app:
            raise ValueError("Application view %s not available on site." % application_view)
        data['application_view'] = app.code
        data['application'] = app.appmodel.name
        purl = app.urlbit.url
        if app.isroot():
            url  = app.baseurl
            root = mapper.filter(site = website, level = 0)
            if url == '/':
                if root:
                    root = root[0]
                    if root != page:
                        raise forms.ValidationError("Root page already available, cannot set application as root. Delete the flat root page first")
                parent = None
            else:
                url  = url[1:-1]
                urls = url.split('/')
                if len(urls) > 1:
                    url     = urls[-1]
                    parent_url = '/%s/' % '/'.join(urls[:-1])
                    root    = mapper.filter(site = website, url = parent_url)
                else:
                    parent_url = '/'
                    
                if root:
                    parent = root[0]
                else:
                    raise forms.ValidationError('Parent page "%s" not available, cannot set application %s' % (parent_url,application_view))
        else:
            if not parent:
                pages = mapper.filter(application_view = app.parent.code,
                                      site = website,
                                      url_pattern = '')
                if pages.count() == 1:
                    parent = pages[0]
                else:
                    raise forms.ValidationError('Parent page not defined for %s' % app.code)
            
            bit = url_pattern
            if bit and app.regex.names and parent.url_pattern != bit:
                bits = bit.split('/')
                kwargs = dict(zip(app.regex.names,bits))
                purl = app.regex.get_url(**kwargs)
            url = purl
    else:
        page.application = ''
        url = url_pattern
    
    data['parent'] = parent
    if parent:
        url = '%s%s' % (parent.url,url)
    if not url.endswith('/'):
        url += '/'
    if not url.startswith('/'):
        url = '/%s' % url
    return url    


def application_view_for_parent(bfield):
    '''Generator of application view choices for a given page form'''
    form = bfield.form
    parent = form.parent
    if parent:
        yield empty_choice
    else:
        # No parent, must be root page
        try:
            site,view,kwargs = sites.resolve('')
            yield (view.code,view.code)
        except:
            yield empty_choice


class PageForm(forms.Form):
    '''Inline Editing Page form'''
    site = forms.ModelChoiceField(choices = allsites, widget = forms.HiddenInput, required = False)
    link = forms.CharField(required = False)
    url_pattern = forms.CharField(required = False)
    application_view = forms.ChoiceField(choices = application_view_for_parent,
                                         required = False)
    
    def __init__(self, **kwargs):
        self.parent = kwargs.pop('parent',None)
        super(PageForm,self).__init__(**kwargs)
    
    def additional_data(self):
        if self.parent:
            return {'parent': self.parent.id}
        
    def get_application_view(self, app):
        '''If application type is specified, than it must be unique
        '''
        cd = self.cleaned_data
        site = sites.get_site()
        if app:
            try:
                application_view = site.getapp(app)
            except KeyError:
                raise forms.ValidationError('Application view %s not available' % app)
            parent = self.get_parent()
            # Parent page is available
            if parent:
                if not application_view.parent:
                    parent = None
                    self.data.pop('parent',None)
                elif application_view.parent.code != parent.application_view:
                    raise forms.ValidationError("Page %s is not a parent of %s" % (parent,application_view))
            
            bit = data.get('url_pattern','')
            if not application_view.regex.names:
                data['url_pattern'] = ''
                bit = ''
            elif parent and application_view.parent:
                if parent.application_view == application_view.parent.code and parent.url_pattern:
                    bit = parent.url_pattern
                    data['url_pattern'] = bit
            others = mapper.filter(application_view = application_view.code,
                                         site = self.clean_site(),
                                         url_pattern = bit)
            for other in others:
                if other != self.instance:
                    raise forms.ValidationError('Application page %s already avaiable' % app)
        else:
            parent = self.get_parent()
            if not parent:
                # No parent specified. Let's check that a root is not available
                root = self.mapper.filter(site = cd['site'], url = '/')
                if root and root != self.instance:
                    # We assume the page to be child of root. Lets check it is not already avialble
                    self.data['parent'] = root[0].id
                    #raise forms.ValidationError('Page root already avaiable')
        return app

    def get_parent(self):
        pid = self.data.get('parent',None)
        if pid:
            return self.mapper.get(id = int(pid))
        else:
            return None
        
    def clean_url_pattern(self, value):
        if value:
            value = slugify(force_str(value))
        return value
        
    def clean(self):
        '''\
Check for url patterns
    No need if:
        1 - it is the root page
        2 - oit is an application page
    Otherwise it is required
        '''
        cd = self.cleaned_data
        app = self.get_application_view(cd['application_view'])
        url_pattern = cd['url_pattern']
        parent = self.get_parent()
        if app is None:
            if parent:
                if not url_pattern:
                    raise forms.ValidationError('url_pattern or application view must be provided if not a root page')
                page = parent.children.filter(url_pattern = value)
                if page and page[0].id != self.instance.id:
                    raise forms.ValidationError("page %s already available" % page)
        cd['parent'] = self.parent
        cd['url'] = CalculatePageUrl(cd,self.mapper,self.instance)
        return cd


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
    container_type = forms.ChoiceField(label = 'Container', choices = wrappergenerator)
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
            raise forms.ValidationError("Cannot select 'requires login' and 'for not authenticated' at the same time.")

# Short Form for a Page. Used only for editing an existing page
class ShortPageForm(forms.Form):
    '''Form to used to edit inline a page'''
    title = forms.CharField(label = 'Page title', required = False)
    link = forms.CharField(label = 'Text to display in links', required = False)
    in_navigation = forms.IntegerField(help_text = 'An integer greater or equal to 0 used for link ordering in menus.',
                                       required = False)
    requires_login = forms.BooleanField()
    soft_root = forms.BooleanField()
    #inner_template = 
    #cssinfo = 
    #view_permission = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required = False)
    
    def save(self, commit = True):
        #pe = self.cleaned_data.pop('view_permission')
        page = super(ShortPageForm,self).save(commit)
        #if page.pk:
        #    sites.permissions.set_permission(page, 'view', groups = pe)
        return page


class NewChildForm(forms.Form):
    #url_pattern = forms.CharField(label = 'New child page url', required = True)
   # 
    #layout = FormLayout(Fieldset('url_pattern', css_class = inlineLabels))
    
    #class Meta:
    #    model = Page
    #    fields = ['soft_root','in_navigation','requires_login','inner_template']
    
    def clean_url_pattern(self):
        parent = self.instance
        if not parent.id:
            raise forms.ValidationError('Parent page not available')
        name = self.cleaned_data.get('url_pattern',None)
        child = parent.children.filter(url_pattern = name)
        if child:
            raise forms.ValidationError('child page %s already available' % name)
        return name
    
    def clean(self):
        cd = self.cleaned_data
        self.page_form = create_page(parent = self.instance, commit = False, **cd)
        return cd
    
    def save(self, commit = True):
        return self.page_form.save()


def ferrors(errdict):
    for el in errdict.itervalues():
        for e in el:
            yield e


def _getid(obj):
    if obj:
        try:
            return obj.id
        except:
            return obj
    else:
        return obj
        

ChildFormHtml = forms.HtmlForm(
    NewChildForm,
    submits = (('create', '_child'),)
)


PageFormHtml = forms.HtmlForm(
    ShortPageForm,
    submits = (('change', '_save'),)
)


ContentBlockHtmlForm = forms.HtmlForm(
    ContentBlockForm,
    layout = uniforms.Layout(
                          uniforms.Fieldset('plugin_name','container_type','title',
                                            'view_permission'),
                          uniforms.Columns(('for_not_authenticated',),
                                           ('requires_login',),
                                           default_style=uniforms.inlineLabels3)
                           )
)
