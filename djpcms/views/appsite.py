'''
Application Model Manager
This module define the base class for implementing Dynamic Page views based on django models
The main object handle several subviews used for searching, adding and manipulating objects
'''
from copy import deepcopy

from py2py3 import iteritems, is_string, is_bytes_or_string, to_string

import djpcms
from djpcms.forms import FormType, HtmlForm, SubmitInput, MediaDefiningClass
from djpcms.template import loader, mark_safe
from djpcms.core.orms import mapper
from djpcms.core.urlresolvers import ResolverMixin
from djpcms.core.exceptions import PermissionDenied, ApplicationUrlException
from djpcms.utils import slugify
from djpcms.forms.utils import get_form
from djpcms.plugins import register_application
from djpcms.utils.collections import OrderedDict

from .baseview import response_from_page, absolute_parent
from .appview import View, ViewView
from .utils import ObjectDefinition


__all__ = ['Application',
           'ModelApplication']


def get_declared_application_views(bases, attrs):
    """Create a list of Application views instances from the passed in 'attrs', plus any
similar fields on the base classes (in 'bases')."""
    inherit = attrs.pop('inherit',False)
    apps = ((app_name, attrs.pop(app_name)) for app_name, obj in list(attrs.items()) if isinstance(obj, View))
    apps = sorted(apps, key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Application, and inherit is True add that Application's views.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if inherit:
        for base in bases[::-1]:
            if hasattr(base, 'base_views'):
                apps = list(base.base_views.items()) + apps
                
    return OrderedDict(apps)


class ApplicationMetaClass(MediaDefiningClass):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_views'] = get_declared_application_views(bases, attrs)
        new_class = super(ApplicationMetaClass, cls).__new__(cls, name, bases, attrs)
        return new_class
    

# Needed for Python 2 and python 3 compatibility
ApplicationBase = ApplicationMetaClass('ApplicationBase', (object,), {})


def process_views(view,views,app):
    pkey = view.parent
    if pkey:
        if is_bytes_or_string(pkey):
            parent  = app.views.get(pkey,None)
            if not parent:
                raise ApplicationUrlException('Parent %s for %s not in children tree' % (pkey,view))
            view.parent = parent
        else:
            parent = pkey
        
        if parent in views:
            return process_views(parent,views,app)
        else:
            views.remove(view)
            return view
    else:
        if view is not app.root_application:
            view.parent = app.root_application
        views.remove(view)
        return view


class Application(ApplicationBase,ResolverMixin):
    '''Base class for djpcms applications.
    
.. attribute:: baseurl

    the root part of the application views urls. Must be provided with trailing slashes (ex. "/docs/")
    
.. attribute:: application_site

    instance of :class:`djpcms.views.appsite.ApplicationSite`, the application site manager.
    
.. attribute:: editavailable

    ``True`` if :ref:`inline editing <inline-editing>`
    is available for the application.
'''    
    inherit          = False
    '''Flag indicating if application views are inherited from base class. Default ``False``.'''
    name             = None
    '''Application name. Default ``None``, calculated from class name.'''
    description      = None
    '''Application description. Default ``None``, calculated from name.'''
    authenticated    = False
    '''True if authentication is required. Default ``False``.'''
    has_api          = False
    '''Flag indicating if API is available. Default ``False``.'''
    hidden           = False
    '''If ``True`` the application is only used internally. Default ``False``.'''
    form             = None
    '''Default form class used in the application. Default ``None``.'''
    form_method      ='post'
    '''Form submit method, ``get`` or ``post``. Default ``post``.'''
    form_ajax        = True
    '''The default interaction in forms. If True the default form submmission is performed using ajax. Default ``True``.'''
    form_template    = None
    '''Optional template for form. Can be a callable with parameter ``djp``. Default ``None``.'''
    in_navigation    = True
    '''True if application'views can go into site navigation. Default ``True``.
No reason to change this default unless you really don't want to see the views in the site navigation.'''
    list_per_page    = 30
    '''Number of objects per page. Default is ``30``.'''
    exclude_links    = []
    list_display     = []
    '''List of object's field to display. If available, the search view will display a sortable table
of objects. Default is ``None``.'''

    # Submit buton customization
    _form_add        = 'add'
    _form_edit       = 'change'
    _form_save       = 'done'
    _submit_cancel   = 'cancel'
    _form_continue   = 'save & continue'
    _submit_as_new   = None
    '''Set to a value if you want to include a save as new submit input when editing an instance.'''
    
    def __init__(self, baseurl, editavailable = None, name = None,
                 list_per_page = None, form = None, list_display = None):
        self.application_site = None
        self.editavailable    = editavailable
        if not baseurl.endswith('/'):
            baseurl = '%s/' % baseurl
        if not baseurl.startswith('/'):
            baseurl = '/%s' % baseurl
        self.__baseurl        = baseurl
        self.list_per_page    = list_per_page or self.list_per_page
        self.list_display = list_display or self.list_display
        self.form             = form or self.form
        self.name             = self._makename(name)
        
    def register(self, application_site):
        '''Register application with site'''
        url = self.make_url
        self.root_application = None
        self.application_site = application_site
        self.settings = application_site.settings
        if self.editavailable is None:
            self.editavailable = self.settings.CONTENT_INLINE_EDITING.get('available',False)
        self.ajax             = self.settings.HTML_CLASSES
        self.description      = self._makedescription()
        self.views            = deepcopy(self.base_views)
        self.object_views     = []
        self._create_views()
        urls = []
        for app in self.views.values():
            view_name  = self._get_view_name(app.name)
            nurl = url(regex = str(app.regex),
                       view  = app,
                       name  = view_name)
            urls.append(nurl)
        self._urls = tuple(urls)
        self.registration_done()
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.baseurl)
    
    def __str__(self):
        return self.__repr__()
    
    def registration_done(self):
        pass
    
    def getview(self, code):
        '''Get an application view from the view code.'''
        return self.views.get(code, None)
    
    def get_root_code(self):
        raise NotImplementedError
    
    def __get_baseurl(self):
        return self.__baseurl
    baseurl = property(__get_baseurl)
    
    def isroot(self):
        return True
    
    def get_the_view(self):
        return self.root_application
    
    def has_permission(self, request = None, obj = None):
        '''Return True if the page can be viewed, otherwise False'''
        return True
    
    def parentresponse(self, djp, app):
        '''Retrieve the parent :class:`djpcms.views.response.DjpResponse` instance
        '''
        parent_view = app.parent
        kwargs = djp.kwargs
        if not parent_view:
            page = app.get_page(djp)
            if page:
                return response_from_page(djp, page.parent)
            else:
                return absolute_parent(djp)
        else:
            return parent_view(djp.request, **djp.kwargs)
    
    def _makename(self, name):
        name = name or self.name
        if not name:
            name = self.__class__.__name__
        name = name.replace('-','_').lower()
        return str(slugify(name,rtx='_'))
    
    def _makedescription(self):
        return self.description or self.name
    
    def _get_view_name(self, name):
        if not self.baseurl:
            raise ApplicationUrlException('Application without baseurl')
        base = self.baseurl[1:-1].replace('/','_')
        return '%s_%s' % (base,name)
    
    def _create_views(self):
        #Build views for this application
        roots = []
        
        if not self.views:
            raise ApplicationUrlException("There are no views in {0} application. Try setting inherit equal to True.".format(self))
        
        # Find the root view
        for name,view in iteritems(self.views):
            if view.object_view:
                self.object_views.append(view)
            view.name = name
            view.code = self.name + '-' + view.name
            if not view.parent:
                if not view.urlbit:
                    if self.root_application:
                        raise ApplicationUrlException('Could not resolve root application for %s' % self)
                    self.root_application = view
                else:
                    roots.append(view)
        
        # No root application. See if there is one candidate
        if not self.root_application:
            if roots:
                #just pick one. We should not be here really! need more testing.
                self.root_application = roots[0]
            else:
                raise ApplicationUrlException("Could not define root application for %s." % self)
        
        # Pre-process urls
        views = list(self.views.values())
        while views:
            view = process_views(views[0],views,self)
            view.processurlbits(self)
            if view.isapp:
                name = self.name + ' ' + view.name.replace('_',' ')
                self.application_site.choices.append((view.code,name))
            if view.isplugin:
                register_application(view)
    
    def get_form(self, djp,
                 form_class,
                 addinputs = True,
                 form_ajax = None,
                 instance  = None,
                 **kwargs):
        '''Build a form. This method is called by editing/adding views.

:parameter djp: instance of :class:`djpcms.views.response.DjpResponse`.
:parameter form_class: form class to use.
:parameter addinputs: boolean flag indicating if submit inputs should be added. Default ``True``.
:parameter form_ajax: if form uses AJAX. Default ``False``.
:parameter instance: Instance of model or ``None`` or ``False``. If ``False`` no instance will be
                     passed to the form constructor. If ``None`` the instance will be obtained from
                     ``djp``. Default ``None``.
'''
        # Check the Form Class
        form_class = form_class or self.form
        if not form_class:
            raise ValueError("Form class not defined in {0}".format(self))
        elif isinstance(form_class,FormType):
            form_class = HtmlForm(form_class)
        
        # Check instance and model    
        if instance == False:
            instance = None
        else:
            instance = instance or djp.instance
            
        if instance:
            model = instance.__class__
        else:
            model = getattr(form_class,'model',None)
            if not model:
                model = getattr(self,'model',None)
        form_class.model = model
        
        form_ajax = form_ajax if form_ajax is not None else self.form_ajax
        return get_form(djp,
                        form_class,
                        instance = instance,
                        addinputs= self.submit if addinputs else None,
                        model=model,
                        form_ajax=form_ajax,
                        **kwargs)
        
    def submit(self, instance, own_view = False):
        '''Generate the submits elements to be added to the model form.
        '''
        if instance:
            sb = [SubmitInput(value = self._form_save, name = '_save')]
            if self._submit_as_new:
                sb.append(SubmitInput(value = self._submit_as_new, name = '_save_as_new'))
        else:
            sb = [SubmitInput(value = self._form_add, name = '_save')]
        if own_view:
            if self._form_continue:
                sb.append(SubmitInput(value = self._form_continue, name = '_save_and_continue'))
            if self._submit_cancel:
                sb.append(SubmitInput(value = self._submit_cancel, name = '_cancel'))
        return sb

    def get_label_for_field(self, name):
        '''Fallback function for retriving a label for a given field name.'''
        raise AttributeError("Attribute %s not available" % name)

    def links(self, djp, asbuttons = True, exclude = None):
        '''Create a list of application links available to the user'''
        css     = djp.css
        next    = djp.url
        request = djp.request
        post    = ('post',)
        posts   = []
        gets    = []
        exclude = exclude or []
        for ex in self.exclude_links:
            if ex not in exclude:
                exclude.append(ex)
        content = {'geturls':gets,
                   'posturls':posts}
        kwargs  = djp.kwargs
        for view in self.views.itervalues():
            if view.object_view:
                continue
            name = view.name
            if name in exclude:
                continue
            djpv = view(request, **kwargs)
            if view.has_permission(request):
                url   = '%s?next=%s' % (djpv.url,view.nextviewurl(djp))
                title = ' title="%s"' % name
                if asbuttons:
                    if view.methods(request) == post:
                        cl = ' class="%s %s"' % (css.ajax,css.nicebutton)
                    else:
                        cl = ' class="%s"' % css.nicebutton
                else:
                    if view.methods(request) == post:
                        cl = ' class="%s"' % css.ajax
                    else:
                        cl = ' '
                posts.append(mark_safe('<a href="{0}"{1}{2} name="{3}">{3}</a>'.format(url,cl,title,name)))
                content['%surl' % name] = url
        return content
    
    def table_generator(self, djp, qs):
        '''Return an iterable for an input iterable :param qs:.'''
        return qs


class ModelApplication(Application):
    '''An :class:`Application` class for applications
based on a back-end database model.
This class implements the basic functionality for a general model
User should subclass this for full control on the model application.

.. attribute:: model

    The model class which own the application
    
.. attribute:: mapper

    Instance of :class:`djpcms.core.orms.BaseOrmWrapper`. Created from :attr:`model`
'''
    object_display   = None
    '''Same as :attr:`list_display` attribute at object level. The field list is used to display
the object definition. If not available, :attr:`list_display` is used. Default ``None``.'''
    filter_fields    = []
    '''List of model fields which can be used to filter'''
    search_fields    = []
    '''List of model field's names which are searchable. Default ``None``.
This attribute is used by :class:`djpcms.views.appview.SearchView` views
and by the :ref:`auto-complete <autocomplete>`
functionality when searching for model instances.'''
    exclude_object_links = []
    '''Object view names to exclude from object links. Default ``[]``.'''
    #
    list_display_links = []
    
    def __init__(self, baseurl, model, object_display = None, **kwargs):
        if not model:
            raise ValueError('Model is null not defined in application {0}'.format(self))
        self.model  = model
        super(ModelApplication,self).__init__(baseurl, **kwargs)
        self.object_display = object_display or self.object_display or self.list_display
        
    def _makename(self, name):
        name = name or self.name
        if not name:
            name = self.model.__name__
        name = name.replace('-','_').lower()
        return str(slugify(name,rtx='_'))
    
    def register(self, application_site):
        self.mapper = mapper(self.model)
        return super(ModelApplication,self).register(application_site)
        
    def get_root_code(self):
        return self.root_application.code
    
    def modelsearch(self):
        return self.model
        
    def objectbits(self, obj):
        '''Get arguments from model instance used to construct url. By default it is the object id.
* *obj*: instance of self.model

It returns dictionary of url bits which are used to uniquely identify a model instance. 
        '''
        return {'id': obj.id}
    
    def get_object(self, request, **kwargs):
        '''Retrive an instance of self.model from key-values *kwargs* forming the url.
By default it get the 'id' and get the object::

    try:
        id = int(kwargs.get('id',None))
        return self.model.objects.get(id = id)
    except:
        return None
    
Re-implement for custom arguments.'''
        try:
            id = int(kwargs.get('id',None))
            return self.model.objects.get(id = id)
        except:
            return None
        
    def object_from_form(self, form):
        '''Save form and return an instance pof self.model'''
        return form.save(commit = True)
    
    # APPLICATION URLS
    #----------------------------------------------------------------
    def appviewurl(self, request, name, obj = None, permissionfun = None, objrequired=False):
        if objrequired and not isinstance(obj,self.model):
            return None
        try:
            view = self.getview(name)
            permissionfun = permissionfun or self.has_view_permission
            if view and permissionfun(request, obj):
                djp = view(request, instance = obj)
                return djp.url
        except:
            return None
        
    def addurl(self, request):
        return self.appviewurl(request,'add',None,self.has_add_permission)
        
    def deleteurl(self, request, obj):
        return self.appviewurl(request,'delete',obj,self.has_delete_permission,objrequired=True)
        
    def editurl(self, request, obj):
        return self.appviewurl(request,'edit',obj,self.has_change_permission,objrequired=True)
    
    def viewurl(self, request, obj, field_name = None):
        return self.appviewurl(request,'view',obj,objrequired=True)
    
    def searchurl(self, request):
        return self.appviewurl(request,'search')
        
    def objurl(self, request, name, obj = None):
        '''Application view **name** url.'''
        view = self.getview(name)
        if not view:
            return None
        permission_function = getattr(self,
                                      'has_%s_permission' % name,
                                      self.has_permission)
        try:
            if permission_function(request,obj):
                djp = view(request, instance = obj)
                return djp.url
            else:
                return None
        except:
            return None
    
    # STANDARD PERMISSIONS
    #-----------------------------------------------------------------------------------------
    def has_view_permission(self, request, obj = None):
        return request.site.permissions.has(request,djpcms.VIEW,obj)
    
    def has_add_permission(self, request, obj=None):
        return request.site.permissions.has(request,djpcms.ADD,obj)
    
    def has_change_permission(self, request, obj=None):
        return request.site.permissions.has(request,djpcms.CHANGE,obj)
    
    def has_delete_permission(self, request, obj=None):
        return request.site.permissions.has(request,djpcms.DELETE,obj)
    #-----------------------------------------------------------------------------------------------
    
    def basequery(self, djp, **kwargs):
        '''
        Starting queryset for searching objects in model.
        This can be re-implemented by subclasses.
        By default returns all
        '''
        return self.model.objects.all()
    
    def orderquery(self, qs):
        return qs
    
    def object_id(self, djp):
        obj = djp.instance
        if obj:
            return self.opts.get_object_id(obj)
        
    def object_content(self, djp, obj):
        '''Utility function for getting content out of an instance of a model.
This dictionary should be used to render an object within a template. It returns a dictionary.'''
        request = djp.request
        editurl = self.editurl(request, obj)
        if editurl:
            editurl = '%s?next=%s' % (editurl,djp.url)
        content = {'item':      obj,
                   'mapper':    self.mapper,
                   'djp':       djp,
                   'user':      request.user}
        content.update(self.object_links(djp,obj))
        return content
    
    def object_links(self, djp, obj, asbuttons = True, exclude = None):
        '''Create permitted object links'''
        css     = djp.css
        next    = djp.url
        request = djp.request
        post    = ('post',)
        posts   = []
        gets    = []
        exclude = self.exclude_object_links
        content = {'geturls':gets,
                   'posturls':posts,
                   'module_name':self.mapper.module_name}
        for view in self.object_views:
            djpv = view(request, instance = obj)
            if view.has_permission(request, djpv.page, obj):
                url = djpv.url
                name = view.name
                if name in exclude:
                    continue
                if not isinstance(view,ViewView):
                    url   = '%s?next=%s' % (url,view.nextviewurl(djp))
                    title = ' title="%s %s"' % (name,obj)
                    if view.methods(request) == post:
                        cl = ' class="%s %s"' % (css.ajax,css.nicebutton)
                    else:
                        cl = ' class="%s"' % css.nicebutton
                    posts.append(mark_safe('<a href="%s"%s%s name="%s">%s</a>' % 
                                            (url,cl,title,name,name)))
                content['%surl' % name] = url
        return content
    
    def app_for_object(self, obj):
        try:
            if self.model == obj.__class__:
                return self
        except:
            pass
        return self.application_site.for_model(obj.__class__)
    
    def paginate(self, request, data, prefix, wrapper):
        '''Paginate data'''
        object_content = self.object_content
        template_name = '%s/%s_search_item.html' % (self.opts.app_label,self.opts.module_name)
        pa = Paginator(data = data, request = request)
        render = loader.render
        for obj in pa.qs:
            yield render(template_name, object_content(djp, obj))
    
    def render_object(self, djp):
        '''Render an object in its object page.
        This is usually called in the view page of the object.
        '''
        return to_string(ObjectDefinition(self, djp))
        
    def title_object(self, obj):
        '''
        Return the title of a object-based view
        '''
        return '%s' % obj
        
    def remove_object(self, obj):
        id = obj.id
        obj.delete()
        return id
    
    def data_generator(self, djp, data):
        '''
        Return a generator for the query.
        This function can be overritten by derived classes
        '''
        request = djp.request
        wrapper = djp.wrapper
        prefix = djp.prefix
        app = self
        render = loader.render
        for obj in data:
            content = app.object_content(djp, obj)
            yield render(self.get_item_template(obj, wrapper), content)
    
    def get_object_view_template(self, obj, wrapper):
        '''Return the template file which render the object *obj*.
The search looks in::

         [<<app_label>>/<<model_name>>.html,
          "djpcms/components/object.html"]
'''
        opts = self.mapper
        template_name = '%s.html' % opts.module_name
        return ['%s/%s' % (opts.app_label,template_name),
                'djpcms/components/object.html']
            
    def get_item_template(self, obj, wrapper):
        '''
        Search item template. Look in
         1 - <<app_label>>/<<module_name>>_list_item.html
         2 - djpcms/object_list_item.html (fall back)
        '''
        opts = self.mapper
        template_name = '%s_list_item.html' % opts.module_name
        return ['%s/%s' % (opts.app_label,template_name),
                'djpcms/object_list_item.html']
    
    def permissionDenied(self, djp):
        raise PermissionDenied
        
    def sitemapchildren(self, view):
        return []
    
    def instancecode(self, request, obj):
        '''Obtain an unique code for an instance.
Can be overritten to include request dictionary.'''
        return '%s:%s' % (obj._meta,obj.id)
    
    