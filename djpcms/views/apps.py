from copy import copy, deepcopy

from py2py3 import iteritems, is_string,\
                    is_bytes_or_string, to_string

import djpcms
from djpcms import html, forms, ajax
from djpcms.html import SubmitInput, table_header
from djpcms.core.orms import mapper, DummyMapper
from djpcms.core.urlresolvers import ResolverMixin
from djpcms.core.exceptions import PermissionDenied, ApplicationUrlException,\
                                     AlreadyRegistered
from djpcms.utils import slugify, closedurl, openedurl, mark_safe, SLASH
from djpcms.forms.utils import get_form
from djpcms.plugins import register_application
from djpcms.utils.text import nicename
from djpcms.utils.structures import OrderedDict

from .baseview import RendererMixin
from .appview import View, ViewView
from .objectdef import *
from .pagination import *


__all__ = ['Application',
           'ModelApplication',
           'application_action',
           'extend_widgets']

SPLITTER = '-'


def makename(self, name, description):
    name = name or self.name
    if not name:
        name = openedurl(self.baseurl.path)
        if not name:
            name = self.__class__.__name__
    name = name.replace(SPLITTER,'_').replace(SLASH,'_')
    self.description = description or self.description or nicename(name)
    self.name = str(slugify(name.lower(),rtx='_'))


def get_declared_application_views(bases, attrs):
    """Create a list of Application views instances from the passed
in 'attrs', plus any similar fields on the base classes (in 'bases')."""
    inherit = attrs.pop('inherit',False)
    views = []
    apps = []
    for app_name,obj in list(attrs.items()):
        if hasattr(obj,'__class__'):
            if isinstance(obj, View):
                views.append((app_name, attrs.pop(app_name)))
            elif isinstance(obj.__class__,ApplicationMetaClass):
                apps.append((app_name, attrs.pop(app_name)))
    
    views = sorted(views, key=lambda x: x[1].creation_counter)                     
    apps = sorted(apps, key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Application,
    # and inherit is True add that Application's views.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if inherit:
        for base in bases[::-1]:
            if hasattr(base, 'base_views'):
                views = list(base.base_views.items()) + views
                
    return OrderedDict(views),OrderedDict(apps)


class ApplicationMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        views,apps = get_declared_application_views(bases, attrs)
        attrs['base_views'] = views
        attrs['base_apps'] = apps
        new_class = super(ApplicationMetaClass, cls).__new__(cls, name,
                                                             bases, attrs)
        return new_class
    

# Needed for Python 2 and python 3 compatibility
ApplicationBase = ApplicationMetaClass('ApplicationBase', (object,), {})


def process_views(view,views,app):
    pkey = view.parent
    if pkey:
        if is_bytes_or_string(pkey):
            parent  = app.views.get(pkey,None)
            if not parent:
                raise ApplicationUrlException('Parent view "%s" for view "%s"\
 not in children tree. Check application "%s".' %\
                 (pkey,view,app.__class__.__name__))
            view.parent = parent
        else:
            parent = pkey
        
        if parent in views:
            return process_views(parent,views,app)
        else:
            views.remove(view)
            return view
    else:
        if view is not app.root_view:
            view.parent = app.root_view
        views.remove(view)
        return view


def extend_widgets(d, target = None):
    target = target if target is not None else Application.object_widgets
    target = target.copy()
    target.update(d)
    return target


def clean_url_bits(mapper, urlbits, mapping):
    if not mapping:
        mapping = {}
    check = set()
    for bit in urlbits:
        b = mapping.get(bit,None)
        if b is None:
            b = mapper.model_attribute(bit) or 'id'
        if b in check or not b:
            raise ValueError('bad url mapping')
        check.add(b)
        yield bit,b


class Application(ApplicationBase,ResolverMixin,RendererMixin):
    '''A :class:`RendererMixin` which defines a set of :class:`View` instances
which are somehow related
to each other and share a common application object in the
:attr:`RendererMixin.appmodel` attribute which is an instance of this class.
Application views
(instances or :class:`View`) can be specified as class attributes as well as
input parameters in the :class:`Application` constructor. For example, the
snippets::

    from djpcms import views
    
    app = views.Application('/',
                    home = views.View(
                        renderer = lambda djp : 'Hello world!'),
                    whatever = views.View("/what/",
                        renderer = lambda djp : 'I'm on whatever view!')
                    )
                    
and::

    from djpcms import views
    
    class MyApplication(views.Application):
        home = views.View(renderer = lambda djp : 'Hello world!')
        whatever = views.View("/what/",
                              renderer = lambda djp : 'I'm on whatever view!')
                              
    app = MyApplication('/')
    
are equivalent and define an application serving on '/' with two views,
the `home` serving at "/" and the `whatever` view serving at "/what/".
The application class has several :ref:`attributes <application-attributes>`
and :ref:`methods <application-methods>`, some of which can be
overwritten to customize its behavior.
    
:parameter baseurl: the root part of the application views urls.
                    Check :attr:`baseurl` for more information.
:parameter editavailable: ``True`` if :ref:`inline editing <inline-editing>`
                          is available for the application.
:parameter name: Application name. Check :attr:`name` for more information.
                    
                 Default ``None``.
:parameter has_plugins: set the :attr:`has_plugins` attribute.
:parameter in_navigation: If provided it overrides the
                          :attr:`root_view` ``in_nav`` attribute.
                          
                          Default ``None``.
:parameter views: key valued of :class:`View` instances.


--

.. _application-attributes:

**Application attributes**


.. attribute:: baseurl

    the root part of the application views urls::
    
        '/docs/'
        '/myapp/long/path/'
        '/'
        
    and so forth. Trailing slashes will be appended if missing.
    
.. attribute:: model

    Model associated with this application.
    Check :ref:`Object relational mapper <orms>` for more information.
    
    Default: ``None``.
    
.. attribute:: mapper

    Instance of :class:`djpcms.core.orms.OrmWrapper` or ``None``.
    Created from :attr:`model` if available, during construction.
    
.. attribute:: has_plugins

    Boolean indicating if the current application should register plugins
    from views which have the :attr:`View.isplugin` attribute set to ``True``.
    If this flag is ``False`` no view plugin from this application will
    be available.
    
    Default: ``True``
    
.. attribute:: list_display

    An list or a tuple over attribute's names to display in pagination views.
    
        Default ``()``
        
.. attribute:: autocomplete_fields

    List of fields to load when querying for autocomplete. Usually you may
    want to limit this to a small set to speed up retrieval.
    
    Default ``None``.
        
.. attribute:: list_display_links

    List of object's field to display. If available, the search view
    will display a sortable table of objects.
     
     Default is ``None``.
     
.. attribute:: list_per_page_choices
    
    Number of objects per page.
    
    Default is ``(10,25,50,100)``
        
.. attribute:: exclude_links

    List or tuple of view names to exclude form visible views.
    
    Default: ``()``
    
.. attribute:: editavailable

    ``True`` if :ref:`inline editing <inline-editing>`
    is available for the application.
    
.. attribute:: root_view

    An instance of :class:`View` which represents the root view
    of the application.
    This attribute is calculated by djpcms and specified by the user.
    
.. attribute:: related_field
    
    When a :attr:`parent` view is defined, this field represent the
    related field in the model which refers to the parent
    view instance.

.. attribute:: object_widgets
    
    Dictioanry of object renderers.
    
    
.. attribute:: object_display

    Same as :attr:`list_display` attribute at object level.
    The field list is used to display the object definition.
    If not available, :attr:`list_display` is used.
    
    Default ``None``.
    
.. attribute:: inherit

    Flag indicating if application views are inherited from base class.
    
    Default ``False``.    
    
.. attribute:: url_bits_mapping
    
    A dictionary for mapping url keys into model fields.
    
    Default: ``None``.

--

.. _application-methods:

**Application methods**

'''
    creation_counter = 0
    inherit = False
    authenticated = False
    has_plugins = True
    hidden = False
    related_field = None
    list_display = None
    autocomplete_fields = None
    object_display = None
    form = None
    list_per_page = 25
    list_per_page_choices = (10,25,50,100)
    exclude_links    = ()
    list_display_links = ()
    nice_headers_handler = None
    object_widgets = {
          'home': ObjectDef(),
          'list': ObjectItem(),
          'pagination': ObjectPagination()
          }
    in_navigation = None
    table_actions = []
    table_links = None
    table_parameters = {}
    url_bits_mapping = None
    

    DELETE_ALL_MESSAGE = "No really! Are you sure you want to remove \
 all {0[model]} from the database?"
    
    def __init__(self, baseurl, model = None, editavailable = None,
                 list_per_page = None, list_display = None,
                 list_display_links = None, object_display = None,
                 in_navigation = None,
                 related_field = None, apps = None,
                 url_bits_mapping = None, has_plugins = None,
                 # RendererMixin
                 name = None, parent = None, pagination = None,
                 description = None, template_name = None, form = None,
                 #
                  **views):
        # Set the model first
        self.model = model
        self.mapper = None if not self.model else mapper(self.model)
        RendererMixin.__init__(self, parent = parent, name = name,
                               pagination = pagination,
                               template_name = template_name,
                               description = description,
                               form = form)
        if not self.pagination:
            self.pagination = html.Pagination()
        self.views = deepcopy(self.base_views)
        self.apps = deepcopy(self.base_apps)
        self.root_view = None
        self.url_bits_mapping = self.url_bits_mapping or url_bits_mapping
        self.model_url_bits = ()
        self.in_navigation = in_navigation if in_navigation is not None else\
                             self.in_navigation
        self.has_plugins = has_plugins if has_plugins is not None else\
                             self.has_plugins
        self.editavailable = editavailable
        self.baseurl = djpcms.RegExUrl(baseurl)
        # Obsolete
        self.list_per_page = list_per_page or self.list_per_page
        self.list_display = list_display or self.list_display
        self.list_display_links = list_display_links or self.list_display_links
        #
        self.related_field = related_field or self.related_field
        self.creation_counter = Application.creation_counter
        Application.creation_counter += 1
        makename(self,self.name,self.description)
        if self.parent and not self.related_field:
            raise ApplicationUrlException('Parent view {0} specified in\
 application {1} without a "related_field".'.format(self.parent,self))
        if views:
            for name,view in views.items():
                if name in self.views:
                    raise ApplicationUrlException("Could not define add \
view {0}. Already available." % name)
                self.views[name] = view
        if apps:
            for app in apps:
                name = app.name
                if name in self.apps:
                    raise ApplicationUrlException("Could not define add \
application {0}. Already available.".format(name))
                self.apps[name] = app
        
        object_display = object_display or self.object_display
        if not object_display:
            self.object_display = self.pagination.list_display
        else:
            d = []
            for head in object_display or ():
                head = table_header(head)
                d.append(self.pagination.headers.get(head.code,head))
            self.object_display = tuple(d)   
    
    def __deepcopy__(self,memo):
        obj = copy(self)
        obj.views = deepcopy(self.views)
        obj.apps = deepcopy(self.apps)
        return obj
        
    @property
    def tree(self):
        '''application site tree'''
        if self.site:
            return self.site.tree
        
    def __unicode__(self):
        if not self.site:
            v = str(self.baseurl) + ' - Not Registered'
        else:
            v = self.path
        return to_string(v)

    def route(self):
        return self.site.route() + self.baseurl
        
    def registration_done(self):
        '''Invoked by the :class:`ApplicationSite` site to which the
application is registered once registraton is done. It can be used to perform
any task once all applications have been imported.
By default it does nothing.'''
        pass
    
    def getview(self, code):
        '''Get an application view from the view code.
Return ``None`` if the view is not available.'''
        if code in self.views:
            return self.views[code]
        else:
            codes = code.split(SPLITTER)
            code = codes[0]
            if code in self.apps:
                app = self.apps[code]
                if len(codes) > 1:
                    return app.getview(SPLITTER.join(codes[1:]))
    
    def get_from_parent_object(self, parent, id):
        return parent
    
    def get_root_code(self):
        raise NotImplementedError
    
    def isroot(self):
        return True
    
    def get_the_view(self):
        return self.root_view
    
    def _get_view_name(self, name):
        return '%s_%s' % (self.name,name)
    
    def _create_views(self, application_site):
        #Build views for this application. Called by the application site
        if self.site:
            raise AlreadyRegistered(
                    'Application %s already registered as application' % self)
        parent = self.parent
        roots = []
        self._site = application_site
        
        if not self.views:
            raise ApplicationUrlException("There are no views in {0}\
 application. Try setting inherit equal to True.".format(self))
        
        self.object_views = []
                    
        # Find the root view
        for name,view in iteritems(self.views):
            if view.object_view:
                self.object_views.append(view)
            view.name = name
            view.code = self.name + SPLITTER + view.name
            if not view.parent:
                if not view.urlbit:
                    if self.root_view:
                        raise ApplicationUrlException(\
                            'Could not resolve root application for %s' % self)
                    self.root_view = view
                else:
                    roots.append(view)
        
        # No root application. See if there is one candidate
        if not self.root_view:
            if roots:
                #just pick one. We should not be here really! need more testing.
                self.root_view = roots[0]
            else:
                raise ApplicationUrlException(\
                        "Could not define root application for %s." % self)
        
        # Set the in_na if required
        if self.in_navigation is not None:
            self.root_view.in_nav = self.in_navigation
            
        # Pre-process urls
        views = list(self.views.values())
        names = set(parent.names()) if parent else None
        while views:
            view = process_views(views[0],views,self)
            view.processurlbits(self)
            if isinstance(view,ViewView):
                if self.model_url_bits:
                    raise ApplicationUrlException('Application {0} has more\
 than one ViewView instance. Not possible.'.format(self))
                self.model_url_bits = view.names()
                if not self.model_url_bits:
                    raise ApplicationUrlException('Application {0} has no\
 parameters to initialize objects.'.format(self))
            if names:
                na2 = names.intersection(view.names())
                if na2:
                    k = 'key' if len(na2) == 1 else 'keys'
                    ks = ','.join(na2)
                    raise ApplicationUrlException('View "{0}" in application\
 {1} has {2} "{3}" matching parent view "{4}" of application "{5}"'.\
                    format(view,self,k,ks,parent,parent.appmodel))            
            if self.has_plugins and view.isplugin:
                register_application(view)
                
        self.url_bits_mapping = dict(clean_url_bits(self.mapper,
                                                    self.model_url_bits,
                                                    self.url_bits_mapping))
    
    def get_form(self, djp, form_class, addinputs = True, instance  = None,
                 **kwargs):
        '''Build a form. This method is called by editing/adding views.

:parameter djp: instance of :class:`DjpResponse`.
:parameter form_class: form class to use.
:parameter addinputs: boolean flag indicating if submit inputs should be added.
                    
                      Default ``True``.
:parameter instance: Instance of model or ``None`` or ``False``. If ``False``
                     no instance will be passed to the form constructor.
                     If ``None`` the instance will be obtained from '`djp``.
                     
                     Default ``None``.
'''
        # Check the Form Class
        form_class = form_class or self.form
        if not form_class:
            raise ValueError('Form class not defined for view "{0}" in\
 application "{1}" @ "{2}".\
 Make sure to pass a class form to the view or application constructor.'\
                    .format(djp.view,self.__class__.__name__,self))
        elif isinstance(form_class,forms.FormType):
            form_class = forms.HtmlForm(form_class)
        
        # Check instance and model    
        if instance == False:
            instance = None
        else:
            instance = instance or djp.instance
            
        model = instance.__class__ if instance else self.model
        return get_form(djp,
                        form_class,
                        instance = instance,
                        addinputs=addinputs,
                        model=model,
                        **kwargs)

    def get_label_for_field(self, name):
        '''Fallback function for retriving a label for a given field name.'''
        raise AttributeError("Attribute %s not available" % name)
    
    def table_generator(self, djp, headers, qs):
        '''Return an generator from an iterable to be used
to render a table.'''
        return qs

    def addurl(self, request, name = 'add'):
        return None
    
    def basequery(self, djp, **kwargs):
        '''The base query for the application.'''
        if self.mapper:
            user = self.for_user(djp)
            if user:
                qs = self.mapper.filter(user = user)
            else:
                qs = self.mapper.all()
            related_field = self.related_field
            if related_field:
                parent = djp.parent
                if parent:
                    instance = parent.instance
                    if instance and not isinstance(instance,self.model):
                        qs = qs.filter(**{related_field:instance})
            if hasattr(qs,'ordering') and not qs.ordering and\
                                                 self.pagination.ordering:
                qs = qs.sort_by(self.pagination.ordering)
            return qs
        else:
            return djp.auth_children()  
    
    def render_query(self, djp, query):
        '''Render a *query* as a table or a list of items.

:param query: an iterable over items.
'''
        return paginationResponse(djp, query)
            
    def for_user(self, djp):
        if self.parent:
            djp = self.tree[self.parent.path].djp(djp.request,**djp.kwargs)
            return djp.for_user()
        
    def gen_autocomplete(self, qs, maxRows = None):
        '''generator of 3-elements tuples for autocomplete responses.

:parameter qs: the autocomplete query
:paramater maxRows: optional number of rows.
''' 
        if maxRows:
            qs = qs[:int(maxRows)]
        for q in qs:
            l = str(q)
            yield l,l,q.id
            
    def delete_all(self, djp):
        '''Remove all model instances from database.'''
        self.mapper.delete_all()
        
    def table_column_groups(self, djp):
        '''A hook for returning group of table headers before sending
data to the client.

:parameter djp: instance of :class:`DjpResponse`.

:rtype: an iterable over two dimensional tuples::

    (view name, [list of headers]),
    (view2 name, [list of headers])

    By default it returns ``None``.'''
        pass
    
    def load_fields(self, headers = None):
        if headers:
            load_only = tuple((h.attrname for h in headers))
            # If the application has a related_field make sure it is in the
            # load_only tuple.
            if self.related_field and self.related_field not in load_only:
                load_only += (self.related_field,)
            return load_only
        else:
            return ()
        
    ############################################################################
    ##    MODEL INSTANCE RELATED FUNCTIONS
    ############################################################################
    
    def get_object(self, request, **kwargs):
        '''Retrive an instance of self.model from key-values
*kwargs* forming the url.'''
        query = {}
        for name,val in self.urlbits(data = kwargs):
            if isinstance(val,self.model):
                return val
            query[name] = val
            
        try:
            return self.mapper.get(**query)
        except:
            try:
                if self.parent:
                    parent_object = self.parent.appmodel.get_object(\
                                                request, **kwargs)
                    if parent_object:
                        return self.get_from_parent_object(parent_object,id)
            except:
                pass
            
    def render_object(self, djp, instance = None, context = None, cn = None):
        '''Render an object in its object page.
        This is usually called in the view page of the object.
        '''
        instance = instance or djp.instance
        maker = self.object_widgets.get(context,None)
        if not maker:
            maker = self.object_widgets.get('home',None)
        if maker:
            return maker.widget(instance = instance,
                                appmodel = self,
                                cn = cn)\
                                .addClass(self.mapper.class_name(instance))\
                                .addClass(self.mapper.unique_id(instance))\
                                .render(djp)
        else:
            return ''
    
    def object_field_value(self, request, obj, field_name, val = None):
        '''Return the value associated with *field_name* for the
 object *obj*, an instance of :attr:`model`. This function is only used
 when the application as a model associated with it.

:parameter request: a WSGI request. 
:parameter obj: an instance of :attr:`model`.
:parameter field_name: name of the field to obtain value from.
:parameter val: A value of the field already obtained.
:return: the value of *field_name*.
 
 By default it returns *val*.
 '''
        return val
    
    def objectbits(self, obj):
        '''Get arguments from model instance used to construct url.
By default it is the object id.

:parameter obj: instance of self.model

It returns dictionary of url bits which are used to uniquely
identify a model instance.
This function should not be overitten. Overwrite `_objectbits` instead.'''
        bits = {}
        if isinstance(obj,self.model):
            if self.parent and self.related_field:
                related = getattr(obj,self.related_field)
                bits.update(self.parent.appmodel.objectbits(related))
            bits.update(self.urlbits(obj = obj))
        return bits
    
    def urlbits(self, obj = None, data = None):
        '''generator of key,value pair for urls construction'''
        for name in self.model_url_bits:
            attrname = self.url_bits_mapping[name]
            if obj:
                yield name,getattr(obj,attrname)
            else:
                yield attrname,data[name]
    
    
    
    
        
class ModelApplication(Application):
    filter_fields    = []
    '''List of model fields which can be used to filter'''
    search_fields    = []
    '''List of model field's names which are searchable. Default ``None``.
This attribute is used by :class:`SearchView` views
and by the :ref:`auto-complete <autocomplete>`
functionality when searching for model instances.'''
    exclude_object_links = []
    '''Object view names to exclude from object links. Default ``[]``.'''
    table_actions = [application_action('bulk_delete','delete',djpcms.DELETE)]
        
    def get_root_code(self):
        return self.root_view.code
    
    def modelsearch(self):
        return self.model
    
    def object_from_form(self, form, commit = True):
        '''Save form and return an instance pof self.model'''
        return form.save(commit = commit)
    
    # APPLICATION URLS
    #----------------------------------------------------------------
    def appviewurl(self, request, name, obj = None, objrequired=False):
        if not name or (objrequired and not isinstance(obj,self.model)):
            return None
        view = name
        if not isinstance(view,View):
            view = self.getview(name)
        if view:
            djp = view(request, instance = obj)
            if djp.has_permission():
                return djp.url
        
    def addurl(self, request, name = 'add'):
        return self.appviewurl(request,name,None)
        
    def deleteurl(self, request, obj, name = 'delete'):
        return self.appviewurl(request,name,obj,objrequired=True)
        
    def changeurl(self, request, obj, name = 'change'):
        return self.appviewurl(request,name,obj,objrequired=True)
    
    def viewurl(self, request, instance, name = None, field_name = None):
        '''\
Evaluate the view urls for an *instance*.

:parameter request: a Http Request class.
:parameter instance: instance of model (not necessarely self.model)
:parameter name: Optional name of the view
:parameter field_name: Optional name of a field.'''
        if field_name and self.model:
            value = getattr(instance,field_name,None)
            if hasattr(value,'_meta') and not isinstance(value,self.model):
                appmodel = self.site.for_model(value.__class__)
                if appmodel:
                    return appmodel.viewurl(request,value)
        if not name:
            for view in self.object_views:
                if isinstance(view,ViewView):
                    name = view.name
                    break
        return self.appviewurl(request,name,instance,objrequired=True)
    
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
    
    def app_for_object(self, obj):
        try:
            if self.model == obj.__class__:
                return self
        except:
            pass
        return self.site.for_model(obj.__class__)
        
    def remove_object(self, obj):
        id = self.mapper.unique_id(obj)
        obj.delete()
        return id
    
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
            
    def get_item_template(self, obj):
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
    
    def get_instances(self, djp):
        data = djp.request.REQUEST
        if 'ids[]' in data:
            return self.mapper.filter(id__in = data.getlist('ids[]'))
    
    def ajax__bulk_delete(self, djp):
        '''An ajax view for deleting a list of ids.'''
        objs = self.get_instances(djp)
        mapper = self.mapper
        c = ajax.jcollection()
        if objs:
            for obj in objs:
                id = mapper.unique_id(obj)
                obj.delete()
                c.append(ajax.jremove('#'+id))
        return c
    