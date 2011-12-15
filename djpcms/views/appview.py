from copy import copy
from functools import partial

from py2py3 import zip

import djpcms
from djpcms import http, ajax, Route, async_instance, Http404
from djpcms.forms.utils import saveform, deleteinstance, get_redirect
from djpcms.utils.text import nicename

from .pagination import paginationResponse
from .baseview import djpcmsview 


__all__ = ['View',
           'ModelView',
           'SearchView',
           'AddView',
           'DeleteAllView',
           'ObjectView',
           'ViewView',
           'DeleteView',
           'ObjectActionView',
           'ChangeView']
    

class View(djpcmsview):
    '''A specialized :class:`djpcmsview` class for handling views
which belongs to an :class:`Application`. These views are specified as class
attributes of :class:`Application` or as a list ``routes`` in the
constructor (of :class:`Application`) and therefore initialized
at start up.

Views which derive from this class are special in the sense that they can also
appear as content of :class:`djpcms.plugins.DJPplugin` if
the :attr:`RendererMixin.has_plugin` attribute is set to ``True``.
In other words, application views can be turned into plugins
so that they can be rendered in any page of your site.
All parameters are optional and usually a small subset of them needs
to be used.

This is a trivial example of an application exposing two very simple
views::

    from djpcms import views
    
    class MyApplication(views.Application):
        home = views.View(renderer = lambda djp : 'Hello world')
        test = views.View('/testview/',
                          renderer = lambda djp : 'Another view')

:keyword route:

    A :class:`djpcms.Route` instance or a route string indicating the view
    relative url.
    This is the part of the url which the view add to its parent
    view path. For more information check the
    :attr:`djpcms.RouteMixin.rel_route` attribute.
    
    Default: ``"/"``.
    
:keyword icon:

    To specify the :attr:`djpcmsview.ICON` for this view.
    
:keyword linkname:

    Callable function for overriding :meth:`djpcmsview.linkname`
    
    Default: ``None``.
    
:keyword title:

    Callable function for overriding :meth:`djpcmsview.title`
    
    Default: ``None``.
    
:keyword methods:

    Tuple used to specify the response method allowed
    ('get', 'post', put').
    If specified it replaces the :attr:`_methods` attribute.
    
    Default: ``None``.
    
:keyword view_template:

    Template file used to render the view. Default ``None``.
    If specified it replaces the :attr:`view_template` attribute.
    
:keyword renderer:

    A one parameters functions which can be used to replace the
    default :meth:`render` method. Default ``None``. The function
    must return a safe string ready for rendering on a HTML page.
    
    Default: ``None``.
    
:keyword force_redirect:

    Check :attr:`force_redirect` attribute for details.
    
    Default: ``None``.
    
:keyword permission: A permission flag.

    Default: ``None``.

:keyword redirect_to_view:

    String indicating a redirection to another view within
    the same application. Check :attr:`redirect_to_view`
    for more information.
    
    Default: ``None``.
    
:keyword query:

    Optional function to override the :meth:`RendererMixin.query` method.
    
    Default: ``None``.
    
    
.. attribute:: default_route

    The default route for this view.
    
.. attribute:: isapp

    if ``True`` the view will be added to the application list and can have
    its own page object. Default ``False``.
        
.. attribute:: plugin_form

    The :attr:`djpcms.plugins.DJPplugin.form` for this view.
    
    Default ``None``.
    
.. attribute:: redirect_to_view

    String indicating a redirection to another view within the same application.
    Used in view with forms to define the behavior after a form has been
    subbmitted.
    It is used in :meth:`djpcmsview.defaultredirect`
    to calculate the redirect url.
    
    See also :attr:`force_redirect`.
    
    Default: ``None``.
    
.. attribute:: force_redirect

    Often used in conjunction with :attr:`redirect_to_view`
    to force a redirect after a form submission. For example::
    
        class MyApp(appsite.ModelApplication):
            search = ...
            add = appview.AddView(redirect_to_view = 'search',
                                  force_redirect = True) 
    
    It fine-tunes the response behaviour of your web site forms.
    
    Default: ``False``.
    
.. attribute:: inherit_page

    If ``True`` and a page is not available for the view, the parent view
    page will be used (recursive).
    
    Default ``True``.
'''
    plugin_form = None
    has_plugins = False
    force_redirect = False
    default_route = '/'
    
    def __init__(self,
                 route = None,
                 methods = None,
                 plugin_form = None,
                 renderer = None,
                 title = None,
                 linkname = None,
                 permission = None,
                 force_redirect = None,
                 icon = None,
                 table_generator = None,
                 success_message = None,
                 redirect_to_view = None,
                 inherit_page = True,
                 is_soft = False,
                 query = None,
                 **kwargs):
        super(View,self).__init__(route = route or self.default_route,
                                  **kwargs)
        self.func = None
        self.code = None
        self.inherit_page = inherit_page
        self.redirect_to_view = redirect_to_view if redirect_to_view\
                                     is not None else self.redirect_to_view
        if title:
            self.title = title
        if linkname:
            self.linkname = linkname 
        if table_generator:
            self.table_generator = table_generator
        if renderer:
            self.render = renderer
        if success_message:
            self.success_message = success_message
        if force_redirect is not None:
            self.force_redirect = force_redirect
        if query:
            self.query = query
        # Overrides
        self.PERM = permission if permission is not None else self.PERM
        self.ICON = icon if icon is not None else self.ICON
        self._methods = methods if methods else self._methods
        self.plugin_form = plugin_form or self.plugin_form
        self._is_soft = is_soft
        
    def _isbound(self):
        return self.appmodel is not None
    
    def media(self, request):
        return self.appmodel.media(request)
    
    def in_navigation(self, request):
        if self.appmodel.in_nav:
            if self.in_nav:
                page = request.page
                if page:
                    return page.in_navigation
                    if self.regex.names and page.url != self.path:
                        return 0
                    else:
                        return page.in_navigation
            return self.in_nav
        return 0
    
    def isroot(self):
        '''True if this application view represents the root
 view of the application.'''
        return self.appmodel.root_view is self
    
    def get_form(self, request, form = None, **kwargs):
        return self.appmodel.get_form(request, form or self.form, **kwargs)
        
    def is_soft(self, request):
        page = request.page
        return self._is_soft if not page else page.soft_root
    
    def table_generator(self, request, qs):
        '''Generator of a table view. This function is invoked by
:meth:`View.render_query` for a table layout.'''
        return self.appmodel.table_generator(request, qs)
            
    def for_user(self, request):
        return self.appmodel.for_user(request)
    
    def warning_message(self, request):
        return None
    
    def save(self, request, f, commit = True):
        return f.save(commit = commit)
    
    def save_as_new(self, request, f, commit = True):
        return f.save_as_new(commit = commit)
    
    def __deepcopy__(self, memo):
        return copy(self)
    
    
class ModelView(View):
    '''A :class:`View` class for applications with
:attr:`Application.model` attribute defined.'''
    pass

    
class SearchView(ModelView):
    '''A :class:`ModelView` class for searching objects in a model.
By default :attr:`View.in_navigation` is set to ``True``.
There are three additional parameters that can be set:
    
:keyword table_generator: Optional function to generate table content.

     Default ``None``.
     
:keyword search_text: string identifier for text queries.
    '''
    has_plugin = True
    in_nav = 1
    
    def render(self, request, **kwargs):
        kwargs['query'] = self.query(request, **kwargs)
        return self.appmodel.render(request, **kwargs)
        
    def ajax__autocomplete(self, request):
        fields = self.appmodel.autocomplete_fields
        qs = self.query(request)
        if fields:
            qs = qs.load_only(*fields)
        params = request.REQUEST
        maxRows = params.get('maxRows')
        auto_list = list(self.appmodel.gen_autocomplete(qs, maxRows))
        return ajax.CustomHeaderBody('autocomplete',auto_list)
    
    def ajax_get_response(self, request):
        query = self.query(request)
        return paginationResponse(request, query)
    ajax_post_response = ajax_get_response
    

class AddView(ModelView):
    '''A :class:`ModelView` class which renders a form for adding instances
and handles the saving as default ``POST`` response.'''
    default_route = '/add'
    default_title = 'add'
    default_link = 'add'
    PERM = djpcms.ADD
    ICON = 'ui-icon-circle-plus'
    has_plugin = True
    in_nav = 1
    ajax_enabled = False
    
    def render(self, request, **kwargs):
        return self.get_form(request).render(request, **kwargs)
    
    def post_response(self, request):
        return saveform(request, force_redirect = self.force_redirect)


class DeleteAllView(ModelView):
    '''An POST only :class:`ModelView` which deletes all objects
in a model. Quite drastic.'''
    default_route = '/deleteall'
    PERM = djpcms.DELETEALL
    DEFAULT_METHOD = 'post'
    ICON = 'ui-icon-alert'
    default_title = 'delete all objects'
    default_link = 'delete all objects'
    ajax_enabled = True
    _methods = ('post',)
    
    def post_response(self, request):
        qs = self.query(request)
        num = qs.count()
        qs.delete()
        if request.is_xhr:
            c = ajax.jcollection()
            for instance in qs:
                c.append(ajax.jremove('#'+instance.id))
            return c
        else:
            url = get_redirect(request,force_redirect=True)
            return self.redirect(url)
        
        
class ObjectView(ModelView):
    '''A :class:`ModelView` class view for model instances.
A view of this type has an embedded object available which is used to 
generate the full url.'''
    object_view = True


class ViewView(ObjectView):
    '''An :class:`ObjectView` class specialised for displaying
an object.'''
    default_route = '/<id>/'
    default_title = '{1}'
    default_link = '{1}'
    
    def render(self, request, **kwargs):
        '''Override the :meth:`djpcmsview.render` method
to display a html string for an instance of the application model.
By default it calls the :meth:`ModelApplication.render_instance`
method of the :attr:`View.appmodel` attribute.
        '''
        return self.appmodel.render_instance(request, **kwargs)
    
    def sitemapchildren(self):
        return self.appmodel.sitemapchildren(self)
    
    
# Delete an object. POST method only. not GET method should modify databse
class DeleteView(ObjectView):
    '''An :class:`ObjectView` class specialised for deleting an object.
    '''
    default_route = '/delete'
    parent_view = 'view'
    PERM = djpcms.DELETE
    DEFAULT_METHOD = 'post'
    ICON = 'ui-icon ui-icon-trash'
    force_redirect = True
    ajax_enabled = True
    link_class = 'minibutton ui-state-error-text'
    default_title = 'delete {1}'
    default_link = 'delete'
    _methods      = ('post',)
    
    def post_response(self, request):
        return deleteinstance(request, force_redirect = self.force_redirect)
    
    def warning_message(self, request):
        return {'title':'Deleting',
                'body':'<p>Once you have deleted <b>{0}</b>,\
 there is no going back.</p>\
 <p>Are you really sure? If so press OK.</p>'.format(request.instance)}
    
    def nextviewurl(self, request):
        view = request.view
        if view.object_view and getattr(view,'model',None) == self.model:
            return request.for_view(self.appmodel.root_view).url
        else: 
            return request.url
    
    
class ObjectActionView(ObjectView):
    '''An :class:`ObjectView` class specialised for performing actions
on an instance of a model.'''
    parent_view = 'view'
        
    @async_instance
    def render(self, request, **kwargs):
        return self.get_form(request).render(request, **kwargs)
    
    @async_instance
    def post_response(self, request):
        return saveform(request, force_redirect = self.force_redirect)  
      

# Edit/Change an object
class ChangeView(ObjectActionView):
    '''An :class:`ObjectActionView` class specialised for changing
an instance of a model.'''
    default_route = '/change'
    PERM = djpcms.CHANGE
    ICON = 'ui-icon-pencil'
    default_title = 'edit {1}'
    default_link = 'edit'
    
