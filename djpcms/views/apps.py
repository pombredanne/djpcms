from copy import copy, deepcopy

from py2py3 import iteritems, is_string, itervalues, to_string

import djpcms
from djpcms import html, forms, ajax, ResolverMixin, PermissionDenied,\
                     UrlException, AlreadyRegistered
from djpcms.html import table_header, ContextRenderer
from djpcms.core.orms import mapper
from djpcms.forms.utils import get_form
from djpcms.plugins import register_application
from djpcms.utils.structures import OrderedDict

from .baseview import RendererMixin, SPLITTER
from .appview import View, ViewView
from .objectdef import *
from .pagination import *


__all__ = ['Application',
           'application_action',
           'extend_widgets']


def get_declared_application_routes(bases, attrs):
    """Create a list of Application views instances from the passed
in 'attrs', plus any similar fields on the base classes (in 'bases')."""
    inherit = attrs.pop('inherit',False)
    routes = []
    for app_name,obj in list(attrs.items()):
        if hasattr(obj,'__class__'):
            if isinstance(obj, View) or\
                 isinstance(obj.__class__,ApplicationMetaClass):
                r = attrs.pop(app_name)
                r.name = app_name
                routes.append(r)    
    
    # order the routes by creation counter
    routes = sorted(routes, key=lambda x: x.view_ordering)
    
    # If this class is subclassing another Application,
    # and inherit is True add that Application's views.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if inherit:
        for base in bases[::-1]:
            if hasattr(base, 'base_routes'):
                routes = base.base_routes + routes
    
        routes = list(itervalues(dict(((r.path,r) for r in routes))))
        routes = sorted(routes, key=lambda x: x.view_ordering)
    
    return routes


class ApplicationMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_routes'] = get_declared_application_routes(bases, attrs)
        new_class = super(ApplicationMetaClass, cls).__new__(cls, name,
                                                             bases, attrs)
        return new_class
    

# Needed for Python 2 and python 3 compatibility
ApplicationBase = ApplicationMetaClass('ApplicationBase', (object,), {})


def extend_widgets(d, target = None):
    target = target if target is not None else Application.object_widgets
    target = target.copy()
    target.update(d)
    return target


class Application(ApplicationBase,ResolverMixin,RendererMixin):
    '''Application class which implements :class:`djpcms.ResolverMixin` and
:class:`RendererMixin` and defines a set of :class:`View` instances
which are somehow related
to each other and share a common application object in the
:attr:`RendererMixin.appmodel` attribute which is an instance of this class.
Application views
(instances or :class:`View`) can be specified as class attributes as well as
input parameters in the :class:`Application` constructor. For example, the
snippets::

    from djpcms import views
    
    VIEWS = (
        views.View(name = 'home', renderer = lambda djp : 'Hello world!'),
        views.View('/what'/, renderer = lambda djp : 'Whatever view!')
        )
    
    app = views.Application('/', views = VIEWS)
                    
and::

    from djpcms import views
    
    class MyApplication(views.Application):
        home = views.View(renderer = lambda djp : 'Hello world!')
        what = views.View("/what/", renderer=Lambda djp : 'whatever view!')
                              
    app = MyApplication('/')
    
are equivalent and define an application serving on '/' with two views,
the `home` serving at "/" and the `whatever` view serving at "/what/".
The application class has several :ref:`attributes <application-attributes>`
and :ref:`methods <application-methods>`, some of which can be
overwritten to customize its behavior.
    
:parameter editavailable: ``True`` if :ref:`inline editing <inline-editing>`
                          is available for the application.
:parameter list_display_links: set the :attr:`list_display_links`.
:parameter object_display: set the :attr:`object_display`.
:parameter url_bits_mapping: set the :attr:`url_bits_mapping`.
:parameter apps: an optional iterable over :class:`Application` instances.
:parameter views: an optional iterable over two elements tuples
    ``(name,view instance)``.
:parameter kwargs: key-valued parameters to be passed to the
    :class:`RendererMixin` constructor.

--

.. _application-attributes:

**Application attributes**
    
.. attribute:: model

    Model associated with this application.
    Check :ref:`Object relational mapper <orms>` for more information.
    
    Default: ``None``.
    
.. attribute:: mapper

    Instance of :class:`djpcms.core.orms.OrmWrapper` or ``None``.
    Created from :attr:`model` if available, during construction.
    
.. attribute:: list_display

    An list or a tuple over attribute's names to display in pagination views.
    
        Default ``()``
        
.. attribute:: autocomplete_fields

    List of fields to load when querying for autocomplete. Usually you may
    want to limit this to a small set to speed up retrieval.
    
    Default ``None``.
        
.. attribute:: list_display_links

    List of model fields to render as a link.
     
     Default is ``None``.
        
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
    
.. attribute:: instance_view

    An instance of :class:`ViewView` which represents view which render
    the instance of a :attr:`model`.
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
    
    A dictionary for mapping :class:`djpcms.Route` variable names into
    attribute names of :attr:`model`. This attribute is used only when
    a model. A typical usage::
    
        from djpcms import views
        
        class MyModel:
            id = ...
            
        class MyApp(views.Application):
            model = MyModel
            url_bits_mapping = {'pid':'id'}
            view = views.ViewView('<pid>')
            
    Here the ``pid`` variable is mapped to the ``id`` attribute of your model.
    
    Default: ``None``.

.. attribute:: views

    Dictionary of :class:`View` instances created during registration. The
    keys of the dictionary are the the view names.
    
--

.. _application-methods:

**Application methods**

'''
    inherit = False
    authenticated = False
    related_field = None
    autocomplete_fields = None
    editavailable = True
    object_display = None
    form = None
    exclude_links = ()
    list_display_links = ()
    nice_headers_handler = None
    url_bits_mapping = None
    in_nav = 1
    object_widgets = {
          'home': ObjectDef(),
          'list': ObjectItem(),
          'pagination': ObjectPagination()
          }    

    DELETE_ALL_MESSAGE = "No really! Are you sure you want to remove \
 all {0[model]} from the database?"
    
    def __init__(self, route, model = None, editavailable = None,
                 list_display_links = None, object_display = None,
                 related_field = None, url_bits_mapping = None,
                 routes = None, **kwargs):
        # Set the model first
        self.model = model
        self.mapper = None
        self.root_view = None
        self.instance_view = None
        self.views = OrderedDict()
        views = deepcopy(self.base_routes)
        if routes:
            views.extend(routes)
        ResolverMixin.__init__(self, route)
        RendererMixin.__init__(self, **kwargs)
        if not self.pagination:
            self.pagination = html.Pagination()
        self.object_views = []
        self.model_url_bits = ()
        self.editavailable = editavailable if editavailable is not None else\
                                self.editavailable
        self.list_display_links = list_display_links or self.list_display_links
        self.related_field = related_field or self.related_field
        if self.parent_view and not self.related_field:
            raise UrlException('Parent view "{0}" specified in\
 application {1} without a "related_field".'.format(self.parent_view,self))
        self.addroutes(views)
        object_display = object_display or self.object_display
        if not object_display:
            self.object_display = self.pagination.list_display
        else:
            d = []
            for head in object_display or ():
                head = table_header(head)
                d.append(self.pagination.headers.get(head.code,head))
            self.object_display = tuple(d)   
        
        self.url_bits_mapping = self.url_bits_mapping or url_bits_mapping
        
    def _site(self):
        if self.appmodel:
            return self.appmodel.site
        else:
            return self.parent
        
    def addroutes(self, routes):
        if routes:
            self.__dict__.pop('_urls',None)
            
            # add routes to the views dictionary and check for duplicates
            for route in routes:
                if not isinstance(route,RendererMixin):
                    raise UrlException('Route "{0}" is not a view instance.\
 Error in constructing application "{2}".'.format(route,self))
                route.code = self.name + SPLITTER + route.name                    
                self.views[route.name] = route
            
            #and now set the routes
            processed = {}
            routes = list(itervalues(self.views))
            proutes = list(routes)
            while proutes:
                N = len(proutes)
                for idx,route in enumerate(proutes):
                    if route.parent_view:
                        if route.parent_view in processed:
                            p = processed[route.parent_view]
                            route.rel_route = p.rel_route + route.rel_route
                        else:
                            continue
                    processed[route.name] = route
                    proutes.pop(idx)
                    break
                if len(proutes) == N:
                    raise UrlException('Cannot find parent views in "{0}"'\
                                        .format(self))
                    
            proutes = dict(((p.route.path,p) for p in routes\
                             if isinstance(p,View)))
    
            # Refresh routes dictionary with updated routes paths
            for route in routes:
                if route.path == '/':
                    self.root_view = route
                else:
                    p,c = route.route.split()
                    route.parent_view = proutes.get(p.path)
                if isinstance(route,View) and route.object_view:
                    self.object_views.append(route)
                self.routes.append(route)
                
    def applications(self):
        for app in self:
            if isinstance(app,Application):
                yield app
                for app in app.applications():
                    yield app
                    
    def for_model(self, model, all = False):
        return self.parent.for_model(model, all = all)
    
    def get_from_parent_object(self, parent, id):
        return parent
    
    def _get_view_name(self, name):
        return '%s_%s' % (self.name,name)
    
    def _load(self):        
        if not self.routes:
            raise UrlException("There are no views in {0}\
 application. Try setting inherit equal to True.".format(self))
        if not self.site:
            raise UrlException("There is no site for {0}\
 application.".format(self))
        # Set the in_nav if required
        if self.in_nav and self.root_view:
            self.root_view.in_nav = self.in_nav
        
        self.mapper = None if not self.model else mapper(self.model)
        self.site.register_app(self)
        for view in self:
            view.parent = self
            view.appmodel = self
            if isinstance(view,View):
                if isinstance(view,ViewView):
                    if self.instance_view is not None:
                        raise UrlException('Application {0} has more\
 than one ViewView instance. Not possible.'.format(self))
                    self.instance_view = view
                    # url bit mapping
                    vars = view.route.ordered_variables()
                    if not vars:
                        raise UrlException('Application {0} has no\
 parameters to initialize objects.'.format(self.name))
                    self.model_url_bits = vars
                    if not self.url_bits_mapping:
                        self.url_bits_mapping = dict(((v,v) for v in vars))   
                if self.has_plugins and view.has_plugins:
                    register_application(view)
            else:
                view.load()
        return tuple(self)
    
    def get_form(self, request, form_class, addinputs = True, instance  = None,
                 **kwargs):
        '''Build a form. This method is called by editing/adding views.

:parameter form_class: form class to use.
:parameter addinputs: boolean flag indicating if submit inputs should be added.
                    
                      Default ``True``.
:parameter instance: Instance of model or ``None`` or ``False``. If ``False``
                     no instance will be passed to the form constructor.
                     If ``None`` the instance will be obtained from '`request``.
                     
                     Default ``None``.
'''
        # Check the Form Class
        form_class = form_class or self.form
        if not form_class:
            raise ValueError('Form class not defined for view "{0}" in\
 application "{1}" @ "{2}".\
 Make sure to pass a class form to the view or application constructor.'\
                    .format(request.view,self.__class__.__name__,self))
        elif isinstance(form_class,forms.FormType):
            form_class = forms.HtmlForm(form_class)
        
        # Check instance and model    
        if instance == False:
            instance = None
        else:
            instance = instance or request.instance
            
        model = instance.__class__ if instance else self.model
        return get_form(request,
                        form_class,
                        instance = instance,
                        addinputs=addinputs,
                        model=model,
                        **kwargs)
    
    def table_generator(self, request, headers, qs):
        '''Return an generator from an iterable to be used
to render a table.'''
        return qs

    def addurl(self, request, name = 'add'):
        return None
    
    def query(self, request, **kwargs):
        '''Perform the base query from the request input parameters'''
        if self.mapper:
            inputs = request.REQUEST
            qs = self.mapper.all()
            related_field = self.related_field
            if related_field:
                parent = request.parent
                if parent:
                    instance = parent.instance
                    if instance and not isinstance(instance,self.model):
                        qs = qs.filter(**{related_field:instance})
            search = inputs.get(forms.SEARCH_STRING)
            if search:
                qs = qs.search(search)
            if hasattr(qs,'ordering') and not qs.ordering and\
                                                 self.pagination.ordering:
                qs = qs.sort_by(self.pagination.ordering)
            return qs
        else:
            return request.auth_children()  
    
    def render(self, request, **context):
        if 'query' not in context:
            context['query'] = self.query(request)
        return ContextRenderer(request, context = context,
                               renderer = self.render_query)
    
    def render_query(self, request, query = None, **kwargs):
        '''Render a *query* as a table or a list of items.

:param query: an iterable over items.
'''
        return paginationResponse(request, query, **kwargs)
        
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
            
    def delete_all(self, request):
        '''Remove all model instances from database.'''
        self.mapper.delete_all()
        
    def table_column_groups(self, request):
        '''A hook for returning group of table headers before sending
data to the client.

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
    
    def instance_from_variables(self, environ, urlargs):
        '''Retrive an instance of self.model from request.'''
        try:
            query = dict(self.urlbits(data = urlargs))
        except KeyError:
            raise djpcms.Http404('View Cannot retrieve instance from url')
            
        try:
            return self.mapper.get(**query)
        except self.mapper.DoesNotExist:
            if self.appmodel:
                pi = self.appmodel.instance_from_variables(environ, urlargs)
                if pi:
                    return self.get_from_parent_object(pi,urlargs)
            raise djpcms.Http404('Cannot retrieve instance from url')
            
    def variables_from_instance(self, instance):
        bits = {}
        if isinstance(instance,self.model):
            if self.appmodel and self.related_field:
                related = getattr(instance,self.related_field)
                bits.update(self.appmodel.variables_from_instance(related))
            bits.update(self.urlbits(instance = instance))
        return bits
    
    def render_object(self, request, instance = None,
                      context = None, cn = None):
        '''Render an object in its object page.
        This is usually called in the view page of the object.
        '''
        instance = instance or request.instance
        maker = self.object_widgets.get(context,None)
        if not maker:
            maker = self.object_widgets.get('home',None)
        if maker:
            return maker.widget(instance = instance,
                                appmodel = self,
                                cn = cn)\
                      .addClass(self.mapper.class_name(instance))\
                      .addClass(self.mapper.unique_id(instance))\
                      .render(request)
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
    
    def urlbits(self, instance = None, data = None):
        '''generator of key,value pair for urls construction'''
        # loop over the url bits for the instance
        mapping = self.url_bits_mapping
        for name in self.model_url_bits:
            attrname = mapping.get(name)
            if attrname:
                if instance:
                    yield name,getattr(instance,attrname)
                else:
                    yield attrname,data[name]

    def viewurl(self, request, instance = None, name = None, field_name = None):
        name = name or 'view'
        views = list(instance_field_views(request,
                                         instance,
                                         field_name = field_name,
                                         include = (name,)))
        if views:
            return views[0].url
    
    def remove_instance(self, instance):
        '''Remove a model instance. must return the unique id for
the instance.'''
        id = self.mapper.unique_id(instance)
        instance.delete()
        return id
    
    def get_instances(self, request):
        data = request.REQUEST
        if 'ids[]' in data:
            return self.mapper.filter(id__in = data.getlist('ids[]'))
    
    def ajax__bulk_delete(self, request):
        '''An ajax view for deleting a list of ids.'''
        objs = self.get_instances(request)
        mapper = self.mapper
        c = ajax.jcollection()
        if objs:
            for instance in objs:
                id = self.remove_instance(instance)
                c.append(ajax.jremove('#'+id))
        return c
    
    ############################################################################    
    #TODO
    #
    # OLD ModelApplication methods. NEEDS TO CHECK THEIR USE
    
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
    
    def sitemapchildren(self, view):
        return []
    
    def instancecode(self, request, obj):
        '''Obtain an unique code for an instance.
Can be overritten to include request dictionary.'''
        return '%s:%s' % (obj._meta,obj.id)
    
    