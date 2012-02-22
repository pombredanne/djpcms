from copy import deepcopy

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
           'extend_widgets',
           'store_on_instance']


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


def store_on_instance(f):
    name = '_djpcms_' + f.__name__
    
    def _(self, instance):
        if not hasattr(instance,name):
            res = f(self, instance)
            if res:
                setattr(instance,name,res)
            return res
        return getattr(instance,name)
    
    _.__name__ = f.__name__
    _.__doc__ = f.__doc__
    return _


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
        
.. attribute:: autocomplete_fields

    List of fields to load when querying for autocomplete. Usually you may
    want to limit this to a small set to speed up retrieval.
    
    Default: ``None``.
    
.. attribute:: always_load_fields

    list or tuple of :attr:`model` fields which must be loaded every time
    we query the model. Used by the :meth:`load_fields` method.
    
    Default: ``None``.
        
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
    
    Dictionary of object :class:`djpcms.html.WidgetMaker`.
    
    
.. attribute:: object_display

    The field list is used to display the object definition.
    If not available, :attr:`pagination.list_display` is used.
    
    Default ``None``.
    
.. attribute:: inherit

    Flag indicating if application views are inherited from base class.
    
    Default ``False``.    
    
.. attribute:: url_bits_mapping
    
    An optional dictionary for mapping :class:`djpcms.Route` variable names
    into attribute names of :attr:`model`. It is used when
    a :attr:`model` is available only. A typical usage::
    
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
    always_load_fields = None
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

    def __init__(self, route, model = None, editavailable = None,
                 list_display_links = None, object_display = None,
                 related_field = None, url_bits_mapping = None,
                 routes = None, always_load_fields = None, **kwargs):
        self.model = model
        self.mapper = None
        self.root_view = None
        self.instance_view = None
        self.views = OrderedDict()
        views = deepcopy(self.base_routes)
        if routes:
            views.extend(deepcopy(routes))
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
        self.always_load_fields = always_load_fields or self.always_load_fields
        if self.parent_view and not self.related_field:
            raise UrlException('Parent view "{0}" specified in\
 application {1} without a "related_field".'.format(self.parent_view,self))
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
        #
        self.addroutes(views)
        
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
                #else:
                #    p,c = route.route.split()
                #    route.parent_view = proutes.get(p.path)
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
    
    def get_from_parent_object(self, parent, urlargs):
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
                 block = None, **kwargs):
        '''Build a form. This method is called by editing/adding views.

:parameter form_class: form class to use.

:parameter addinputs: boolean flag indicating if submit inputs should be added.
    
    Default ``True``.

:parameter instance: Instance of model or ``None`` or ``False``. If ``False``
    no instance will be passed to the form constructor.
    If ``None`` the instance will be obtained from '`request``.
                     
    Default ``None``.
    
:parameter block: The content block holding the form.

:rtype: An instance of :class:`djpcms.forms.Form`.
'''
        # Check the Form Class
        form_class = form_class or self.form
        if not form_class:
            raise ValueError('Form class not defined for view "{0}" in\
 application "{1}" @ "{2}".\
 Make sure to pass a class form to the view or application constructor.'\
                    .format(request.view,self.__class__.__name__,self))
        elif isinstance(form_class, forms.FormType):
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
    
    def query(self, request, query = None, **kwargs):
        '''Overrides the :meth:`RendererMixin.query` to perform the base
query from the request input parameters. If a :attr:`mapper` is available,
it delegates the query to it, otherwise it returns the children views for
the *request*.'''
        if self.mapper:
            inputs = request.REQUEST
            qs = query if query is not None else self.mapper.query()
            related_field = self.related_field
            if related_field:
                parent = request.parent
                if parent:
                    instance = parent.instance
                    if instance and not isinstance(instance,self.model):
                        qs = qs.filter(**{related_field:instance})
            search_string = inputs.get('search_string',forms.SEARCH_STRING)
            search = inputs.get(search_string)
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
        
    def table_column_groups(self, request):
        '''A hook for returning group of table headers before sending
data to the client.

:rtype: an iterable over two dimensional tuples::

    (view name, [list of headers]),
    (view2 name, [list of headers])

    By default it returns ``None``.'''
        pass
    
    def load_fields(self, headers = None):
        '''Return a tuple containing the name of the fields to be loaded
from attr:`model` if available. These fields are obtained from the
input *headers*.'''
        if headers:
            load_only = set((h.attrname for h in headers))
            # If the application has a related_field make sure it is in the
            # load_only tuple.
            if self.related_field:
                load_only.add(self.related_field)
            if self.always_load_fields:
                load_only.update(self.always_load_fields)
            return tuple(load_only)
        else:
            return ()
        
    ############################################################################
    ##    MODEL INSTANCE RELATED FUNCTIONS
    ############################################################################
    
    def view_for_instance(self, instance):
        '''Return the view for *instance*. By default it returns the
:attr:`instance_view`.
This is used when an :ref:`instance view <instance-views>`
has been requested.'''
        return self.instance_view
    
    def instance_from_variables(self, environ, urlargs):
        '''Retrieve an :attr:`model` instance from a dictionary of route
variables values. This is used when an :ref:`instance view <instance-views>`
has been requested. This function overrides the
:meth:`RouteMixin.instance_from_variables` method.

:parameter environ: The request WSGI environment. This function is called
    before the :class:`djpcms.core.http.Request` is created, that is why the
    environment is passed instead.
:parameter urlargs: dictionary of url variables with their values.
:rtype: an instance of :attr:`model`

It uses the :meth:`urlbits` generator for the purpose.
If the instance could not be retrieved, it raises a 404 exception.'''
        try:
            query = dict(self.urlbits(data = urlargs))
        except KeyError:
            raise djpcms.Http404('View Cannot retrieve instance from url')
        
        if self.mapper:
            try:
                return self.mapper.get(**query)
            except (self.mapper.DoesNotExist, self.mapper.FieldValueError):
                # Not found. If this application has a parent application
                # try to get the retrieve the parent object
                if self.appmodel:
                    pi = self.appmodel.instance_from_variables(environ, urlargs)
                    if pi:
                        return self.get_from_parent_object(pi, urlargs)
        raise djpcms.Http404('Cannot retrieve instance from url parameters\
 {0}'.format(query))
    
    @store_on_instance        
    def variables_from_instance(self, instance):
        '''Override the :meth:`RouteMixin.variables_from_instance` method
to obtain a dictionary of url variables from an instance of :attr:`model`.
This is used when an :ref:`instance view <instance-views>`
has been requested. It uses the :meth:`urlbits` generator for the purpose.'''
        bits = {}
        if isinstance(instance,self.model):
            if self.appmodel and self.related_field:
                related = getattr(instance,self.related_field)
                bits.update(self.appmodel.variables_from_instance(related))
            bits.update(self.urlbits(instance = instance, bits = bits))
        return bits
    
    def render_instance(self, request, instance = None,
                        context = None, cn = None, **kwargs):
        '''Render an instance of :attr:`model`.
This is used when an :ref:`instance view <instance-views>`
has been requested.

:parameter instance: instance of :attr:`model` or ``None``. If not provided, the
    instance on the *request* parameter will be used.
:parameter context: string representing the context for rendering. If not
    provided, the ``"home"`` renderer will be used. This parameter is closely
    linked with the :attr:`Application.object_widgets`` dictionary
    of widgets.
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
    
    def instance_field_value(self, request, instance, field_name, val = None):
        '''Return the value associated with *field_name* for the
 object *instance*, an instance of :attr:`model`. This function is only used
 when the application as a model associated with it.

:parameter request: a WSGI request. 
:parameter instance: an instance of :attr:`model`.
:parameter field_name: name of the field to obtain value from.
:parameter val: A value of the field already obtained.
:return: the value of *field_name*.
 
 By default it returns *val*.
 '''
        return val
    
    def urlbits(self, instance = None, data = None, bits = None):
        '''Generator of key, value pairs of url variables
from an *instance* of :attr:`model` or from a *data* dictionary.
It loops through the :attr:`djpcms.RouteMixin.route` variables, map them
to :attr:`model` attributes by using the :attr:`url_bits_mapping`
and get the values. If an instance is provided it yields::

    url_variable_name, url_variable_value
    
otherwise::

    url_model_attribute, url_variable_value
    
This method is called by both :meth:`variables_from_instance` and
:meth:`instance_field_value`.
'''
        # loop over the url bits for the instance
        bits = bits if bits is not None else ()
        mapping = self.url_bits_mapping
        for name in self.model_url_bits:
            attrname = mapping.get(name)
            if attrname:
                if instance:
                    if name not in bits and hasattr(instance, attrname):
                        yield name,getattr(instance,attrname)
                else:
                    yield attrname,data[name]

    def instance_field_view(self, request, instance = None, field_name = None,
                            name = None, urlargs = None, asbutton = None,
                            icon = True):
        '''Obtain a link for instance field if possible.
        
:parameter instance: an instance of :attr`model`
:parameter name: optional view name. By default it is the object view.
:parameter field_name: the instance field name.
:parameter asbutton: optional boolean. If specified it returns a link widget.
:rtype: a url string or ``None``.

It uses the :func:`instance_field_view_value` for the purpose.
'''
        instance = instance or request.instance
        view,value = instance_field_view_value(request, instance, field_name,
                                               name = name, urlargs = urlargs)
        if asbutton is not None:
            return application_link(view, value = value, asbutton = asbutton,
                                    icon = icon)
        else:
            return view
    
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
        objs = objs.delete()
        if objs:
            for id in objs:
                id = mapper.unique_id(id)
                c.append(ajax.jremove('#'+id))
        return c
    
    def redirect_url(self, request, instance = None, name = None):
        '''Evaluate a url for an applicationview.
It uses the following algorithm:
        
* Checks if *name* correspond to a valid view in the :attr:`views` dictionary.
* Checks if the view has a :attr:`View.redirect_to_view` attribute available.
* Checks for the instance view via :meth:`view_for_instance` if the input
  *instance* is not ``None``.
* Last it picks the :attr:`root_view`.
        
:parameter instance: optional instance.
:parameter name: optional :class:`View` name in :attr:`views` dictionary.
:rtype: a url string or ``None``.

.. seealso::

    The :attr:`View.force_redirect` attribute af a view class can
    be used to force the call of this function to evaluate
    a redirect url. For example the ``force_redirect`` of the
    :class:`AddView` is set to ``True`` and it will redirect to
    the instance view.
'''
        name = name or request.view.redirect_to_view
        view = None
        if hasattr(name,'__call__'):
            view = name(request,instance)
        elif name:
            view = self.views.get(name)
        if not view:
            if instance and instance.id:
                view = self.view_for_instance(instance)
            if not view:
                view = self.root_view
        if isinstance(view,RendererMixin):
            view = request.for_path(view.path,instance=instance)
        if view:
                return view.url
            
    ############################################################################    
    #TODO
    #
    # OLD ModelApplication methods. NEEDS TO CHECK THEIR USE
    
    def instancecode(self, request, instance):
        '''Obtain an unique code for an instance.
Can be overritten to include request dictionary.'''
        return '%s:%s' % (instance._meta,instance.id)
    
    