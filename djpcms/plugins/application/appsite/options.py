'''
Application Model Manager
This module define the base class for implementing Dynamic Page views based on django models
The main object handle several subviews used for searching, adding and manipulating objects
'''
from copy import deepcopy

from django import forms
from django.forms.models import modelform_factory
from django.utils.encoding import force_unicode
from django.utils.datastructures import SortedDict
from django.template import loader, Template, RequestContext

from djpcms.djutils import form_kwargs, UnicodeObject
from djpcms.djutils.forms import addhiddenfield
from djpcms.html import formlet, submit, form, div, ajaxbase, Paginator
from djpcms.views.baseview import editview
from djpcms.plugins.application.appsite import AppView, ArchiveApp, TagApp, SearchApp



class SearchForm(forms.Form):
    '''
    A simple search box
    '''
    search = forms.CharField(max_length=300, required = False,
                             widget = forms.TextInput(attrs={'class':'search-box'}))
    

class ModelApplicationUrlError(Exception):
    pass

def get_declared_applications(bases, attrs):
    """
    Create a list of ModelApplication children instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases').
    """
    apps = [(app_name, attrs.pop(app_name)) for app_name, obj in attrs.items() if isinstance(obj, AppView)]      
    apps.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    for base in bases[::-1]:
        if hasattr(base, 'base_applications'):
            apps = base.base_applications.items() + apps

    return SortedDict(apps)

class ModelAppMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_applications'] = get_declared_applications(bases, attrs)
        new_class = super(ModelAppMetaClass, cls).__new__(cls, name, bases, attrs)
        return new_class
    


class ModelApplicationBase(ajaxbase):
    '''
    Base class for model applications
    This class implements the basic functionality for a general model
    User should subclass this for full control on the model application.
    Each one of the class attributes are optionals
    '''
    # Name for this application. Optional (the model name will be used if None)
    name             = None
    # Base URL for the application including trailing slashes. Optional
    baseurl          = None
    # Does require authenticated user?
    autheinticated   = True
    # Form used for adding/editing objects.
    form             = forms.ModelForm
    # Form layout.
    form_layout      = None
    # Whether the form requires the request object to be passed to the constructor
    form_withrequest = False
    # Form response method, POST by default
    form_method      ='post'
    # if True add/edit/delete will be performed via AJAX xhr POST requests
    form_ajax        = True
    search_form      = None
    date_code        = None
    search_form      = SearchForm
    search_item_template = '''<div>{{ item }}</div>'''
    # Template file for displaying an object
    object_template_file = None
    # Number of arguments to create an instance of model
    num_obj_args     = 1
    # True if applications can go into navigation
    in_navigation    = True
    
    def __init__(self, model, application_site):
        self.model = model
        self.opts  = model._meta
        self.root_application = None
        self.application_site = application_site
        self.name             = self.name or self.opts.module_name
        if not self.baseurl:
            raise ModelApplicationUrlError('Base url for application %s not defined' % model)
        self.applications     = deepcopy(self.base_applications)
        self.edits            = []
        parent_url            = '/'.join(self.baseurl[1:-1].split('/')[:-1])
        if not parent_url:
            parent_url = '/'
        else:
            parent_url = '/%s/' % parent_url
        self.parent_url = parent_url
        parents = self.application_site.parent_pages
        children = parents.get(self.parent_url,None)
        if not children:
            children = []
            parents[self.parent_url] = children
        children.append(self)
        self.create_applications()
        
    def create_applications(self):
        roots = []
        for app_name,child in self.applications.items():
            child.name = app_name
            pkey       = child.parent
            if pkey:
                parent  = self.applications.get(pkey,None)
                if not parent:
                    raise ModelApplicationUrlError('Parent %s for %s not in children tree' % (pkey,child))
                child.parent = parent
            else:
                if not child.urlbit:
                    self.root_application = child
                else:
                    roots.append(child)
            child.processurlbits(self)
            code = u'%s-%s' % (self.name,child.name)
            child.code = code
            if child.isapp:
                name = u'%s %s' % (self.name,child.name.replace('_',' '))
                self.application_site.choices.append((code,name))
        #
        # Check for parents
        if len(roots) > 1:
            #TODO. Authomatic parent selections
            if self.root_application:
                for app in roots:
                    app.parent = self.root_application
                                
                
    def get_view_name(self, name):
        if not self.baseurl:
            raise ModelApplicationUrlError('Application without baseurl')
        base = self.baseurl[1:-1].replace('/','_')
        return '%s_%s' % (base,name)
        
    def objectbits(self, obj):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: tuple of url bits 
        '''
        return (obj.id,)
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        id = int(kwargs.get('id',None))
        return self.model.objects.get(id = id)
        
    def get_baseurl(self):
        if self.baseurl:
            return self.baseurl
        else:
            return '/%s/' % self.name
    
    def getapp(self, code):
        return self.applications.get(code, None)
        
    def get_form(self, request, prefix = None, wrapper = None, url = None, instance = None):
        '''
        Build an add/edit form for the application model
        @param request: django HttpRequest instance
        @param instance: instance of self.model or None
        @param prefix: prefix to use in the form
        @param wrapper: instance of djpcms.plugins.wrapper.ContentWrapperHandler with information on layout
        @param url: action url in the form     
        '''
        mform = mform = addhiddenfield(modelform_factory(self.model, self.form),'prefix')
        initial = None
        if prefix:
            initial = {'prefix':prefix}
                
        f     = mform(**form_kwargs(request,
                                    instance = instance,
                                    initial = initial,
                                    withrequest = self.form_withrequest,
                                    prefix = prefix))
        fhtml = form(method = self.form_method, url = url)
        
        sbvalue = 'add'
        sbname  = 'add'
        if instance:
            sbvalue = 'save'
            sbname  = 'edit'
        if wrapper:
            layout = wrapper.form_layout
        else:
            layout = None
        fl = formlet(form = f, layout = layout, submit = submit(value = sbvalue, name = sbname))
        if self.form_ajax:
            fhtml.addclass(self.ajax.ajax)            
        fhtml.make_container(div).append(fl)
        return fhtml
    
    def get_searchform(self, request, prefix = None, wrapper = None, url = None):
        '''
        Build a search form for model
        '''
        mform = addhiddenfield(self.search_form,'prefix')
        initial = {'prefix':prefix}
        f = mform(**form_kwargs(request, initial = initial, prefix = prefix))
        fhtml = form(method = 'get', url = url)
        fhtml.make_container(div).append(formlet(form = f, layout = 'flat-notag', submit = submit(value = 'search', name = 'search')))
        return fhtml        
    
    def get_page(self):
        from djpcms.models import Page
        if self.haspage:
            pages = Page.object.get_for_model(self.model).filter(app_type = '')
            if not pages:
                raise valueError
            return page[0]
        else:
            return None
        
    def make_urls(self):
        '''
        Loop over children and create the django url view objects
        '''
        from django.conf.urls.defaults import patterns, url
        from djpcms.settings import CONTENT_INLINE_EDITING
        edit = CONTENT_INLINE_EDITING.get('available',False)
        if edit:
            edit = CONTENT_INLINE_EDITING.get('preurl','edit')
        else:
            edit = None
            
        urls  = []
        for child in self.applications.values():
            #func = child.func
            #child.func = func(child)
            view_name  = self.get_view_name(child.name)
            urls.append(url(child.rurl, child.response, name = view_name))
            if edit:
                eview = editview(child,edit)
                self.edits.append(eview)
                urls.append(url(child.edit_rurl(edit), eview.response, name = '%s_%s' % (edit,view_name)))
                
        return tuple(urls)
    urls = property(fget = make_urls)
    
    def deleteurl(self, request, obj):
        #TODO: change this so that we are not tide up with name
        view = self.getapp('delete')
        if view and self.has_delete_permission(request, obj):
            view = view(obj)
            return view.get_url()
        
    def editurl(self, request, obj):
        '''
        Get the edit url if available
        '''
        #TODO: change this so that we are not tide up with name
        edit = self.getapp('edit')
        if edit and self.has_edit_permission(request, obj):
            editview = edit(obj)
            return editview.get_url()
    
    def viewurl(self, request, obj):
        '''
        Get the view url if available
        '''
        #TODO: change this so that we are not tide up with name
        view = self.getapp('view')
        if view and self.has_view_permission(request, obj):
            view = view(obj)
            return view.get_url()
        
    def tagurl(self, request, tag):
        return None
            
    def has_edit_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())
    
    def has_view_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.

        If `obj` is None, this should return True if the given request has
        permission to delete *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission())
    
    def basequery(self, request):
        '''
        Starting queryset for searching objects in model.
        This can be re-implemented by subclasses.
        By default returns all
        '''
        return self.model.objects.all()
    
    def object_content(self, request, prefix, wrapper, obj):
        return {}
    
    def paginate(self, request, data, prefix, wrapper):
        '''
        paginate data
        @param request: HTTP request 
        @param data: a queryset 
        '''
        template_name = '%s/%s_search_item.html' % (self.opts.app_label,self.opts.module_name)
        pa = Paginator(data = data, request = request)
        for obj in pa.qs:
            content = self.object_content(request, prefix, wrapper, obj)
            content.update({'item': obj,
                            'editurl': self.editurl(request, obj),
                            'viewurl': self.viewurl(request, obj),
                            'deleteurl': self.deleteurl(request, obj)})
            yield loader.render_to_string(template_name    = template_name,
                                          context_instance = RequestContext(request, content))
    
    def render_object(self, request, prefix, wrapper, obj):
        '''
        Render an object
        '''
        template_name = self.object_template_file or \
                '%s/%s.html' % (self.opts.app_label,self.opts.module_name)
        content = self.object_content(request, prefix, wrapper, obj)
        content.update({'item': obj,
                        'editurl': self.editurl(request, obj),
                        'deleteurl': self.deleteurl(request, obj)})
        return loader.render_to_string(template_name    = template_name,
                                       context_instance = RequestContext(request, content))


class ModelApplication(ModelApplicationBase):
    __metaclass__ = ModelAppMetaClass
    
    
class ArchiveApplication(ModelApplication):
    search        = SearchApp()
    year_archive  = ArchiveApp('(?P<year>\d{4})',  in_navigation = False)
    month_archive = ArchiveApp('(?P<month>\d{2})', 'year_archive', in_navigation = False)
    day_archive   = ArchiveApp('(?P<day>\d{2})',   'month_archive', in_navigation = False)

class TaggedApplication(ArchiveApplication):
    search         = SearchApp()
    tags1          = TagApp('tags1/(\w+)', in_navigation = False)
    tags2          = TagApp('tags2/(\w+)/(\w+)', in_navigation = False)
    tags3          = TagApp('tags3/(\w+)/(\w+)/(\w+)', in_navigation = False)
    tags4          = TagApp('tags4/(\w+)/(\w+)/(\w+)/(\w+)', in_navigation = False)
    
    def tagurl(self, request, *tags):
        N = len(tags)
        view = self.getapp('tags%s' % N)
        if view:
            return view.get_url(*tags)    
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tags1')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                tagurls.append({'url':tagview.get_url(tag),'name':tag})
        return {'tagurls': tagurls}
    
class ArchiveTaggedApplication(ArchiveApplication):
    tags1          = TagApp('tags1/(\w+)', in_navigation = False)
    tags2          = TagApp('tags2/(\w+)/(\w+)', in_navigation = False)
    tags3          = TagApp('tags3/(\w+)/(\w+)/(\w+)', in_navigation = False)
    tags4          = TagApp('tags4/(\w+)/(\w+)/(\w+)/(\w+)', in_navigation = False)
    
    def tagurl(self, request, *tags):
        N = len(tags)
        view = self.getapp('tags%s' % N)
        if view:
            return view.get_url(*tags)
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tags1')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                tagurls.append({'url':tagview.get_url(tag),'name':tag})
        return {'tagurls': tagurls}
    