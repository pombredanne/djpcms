import operator
import re
from copy import copy
from datetime import datetime

from py2py3 import zip

import djpcms
from djpcms import http, html, ajax
from djpcms.utils.translation import gettext as _
from djpcms.template import loader
from djpcms.forms.utils import saveform, deleteinstance
from djpcms.utils.text import nicename
from djpcms.views.regex import RegExUrl
from djpcms.views.baseview import djpcmsview
from djpcms.utils.urls import iri_to_uri
from djpcms.utils.ajax import jremove, CustomHeaderBody, jredirect, jempty 


__all__ = ['View',
           'GroupView',
           'ModelView',
           'SearchView',
           'AddView',
           'DeleteAllView',
           'ObjectView',
           'ViewView',
           'DeleteView',
           'ChangeView',
           'ALL_URLS',
           'ALL_REGEX',
           'IDREGEX',
           'UUID_REGEX',
           'SLUG_REGEX']


ALL_REGEX = '.*'
IDREGEX = '(?P<id>\d+)'
SLUG_REGEX = '[-\.\+\#\'\:\w]+'
UUID_REGEX = '(?P<id>[-\w]+)'

ALL_URLS = RegExUrl('(?P<path>{0})'.format(ALL_REGEX), append_slash = False)


def model_defaultredirect(self, request, next = None, instance = None, **kwargs):
    '''Default redirect for a model view is the View url for that model
if an instance is available'''
    if self.redirect_to_view:
        view = self.appmodel.getview(self.redirect_to_view)
        next = view(request, instance = instance).url
    elif instance:
        next = self.appmodel.viewurl(request,instance) or next
    return super(ModelView,self).defaultredirect(request,
                                                 next = next,
                                                 instance = instance,
                                                 **kwargs)
    

def ajax_dataTable(djp,data):
    #TODO move this to a different location
    view = djp.view
    appmodel = view.appmodel
    sort_by = {}
    qs = view.appquery(djp)
    headers = view.list_display or appmodel.list_display
    if hasattr(headers,'__call__'):
        headers = headers(djp)
    search = data['sSearch']
    if search:
        qs = qs.search(search)
        
    for col in range(int(data['iSortingCols'])):
        c = int(data['iSortCol_{0}'.format(col)])
        d = '-' if data['sSortDir_{0}'.format(col)] == 'desc' else ''
        col = html.table_header(appmodel.list_display[c])
        qs = qs.sort_by('{0}{1}'.format(d,col.code))
    start = data['iDisplayStart']
    p = html.Paginator(djp.request,
                       qs,
                       per_page = data['iDisplayLength'],
                       start = data['iDisplayStart'])
    items = appmodel.table_generator(djp, headers, p.qs)
    tbl =  html.Table(headers,
                      items,
                      appmodel = appmodel,
                      paginator = p)
    aaData = []
    for item in tbl.items(djp):
        id = item['id']
        aData = {} if not id else {'DT_RowId':id}
        aData.update(((i,v) for i,v in enumerate(item['display'])))
        aaData.append(aData)
    data = {'iTotalRecords':p.total,
            'iTotalDisplayRecords':p.total,
            'sEcho':data['sEcho'],
            'aaData':aaData}
    return ajax.simplelem(data)
    

class View(djpcmsview):
    '''A specialised view class derived from :class:`djpcms.views.baseview.djpcmsview`
and used for handling views which belongs to
:ref:`djpcms applications <topics-applications-index>`.

Application views are specified as class attributes of
:class:`djpcms.views.appsite.Application` and therefore initialised
at start up.

Views which derives from this class are special in the sense that they can also
appear as content of :class:`djpcms.plugins.DJPplugin` if
the :attr:`isplugin` attribute is set to ``True`` during construction.
In other words, application views can automagically be turned into plugins
so that they can be rendered in any page of your site.

All parameters are optionals and usually a small subset of them needs to be used.

:keyword parent:

    A string indicating the closest parent application view.
    If not supplied, ``djpcms`` will calculate it
    during validation of the applications during startup. It is used to
    assign a value to the :attr:`parent` attribute.
    
    Default ``None``.
    
:keyword regex:

    Regular expression string indicating the view relative url.
    This is the part of the url which the view add to its parent
    view path. For more information check the :func:`djpcms.views.View.route`
    function and :attr:`djpcms.views.View.path` attribute.
    
    Default ``None``.
    
:keyword insitemap:

    If True the view is included in site-map.
    
    Default ``True``.
    
:keyword isplugin:

    If ``True`` the view can be placed in any page via the plugin API.
    (Check :class:`djpcms.plugins.ApplicationPlugin` for more info).
    Its value is assigned to the :attr:`isplugin` attribute.
    
    Default ``False``.
    
:keyword description:

    Useful description of the view in few words
    (no more than 20~30 characters). Used only when the
    :attr:`djpcms.views.View.isplugin` flag is set to ``True``.
    In this case its value is used when
    displaying menus of available plugins. If not defined it is
    calculated from the attribute name of the view
    in the :class:`djpcms.views.Application` where it is declared.

    Default ``None``.

:keyword form:

    Form class or ``None``. If supplied it will be assigned to
    the :attr:`_form` attribute.
    It is a form which can be used for interaction.
    
    Default ``None``.
    
:keyword methods:

    Tuple used to specify the response method allowed ('get', 'post', put') ro ``None``.
    If specified it replaces the :attr:`_methods` attribute.
    
    Default ``None``.
    
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
    
    Default ``None``.
    
:keyword permission: A permission flag.

    Default ``None``.

:keyword headers:

    List of string to display as table header when the
    view display a table.
    
    Default ``None``.

:keyword redirect_to_view:

    String indicating a redirection to another view within
    the same application. Check :attr:`redirect_to_view`
    for more information.
    
    Default: ``None``.
    
    
This is a trivial example of an application exposing two very simple
views::

    from djpcms import views
    
    class MyApplication(views.Application):
        home = views.View(renderer = lambda djp : 'Hello world')
        test = views.View(regex = 'testview',
                          renderer = lambda djp : 'Another view')
    
.. attribute:: appmodel

    Instance of :class:`djpcms.views.Application` which defines the view. This attribute
    is evaluate at runtime and it is not psecified by the user.
    
.. attribute:: parent

    instance of :class:`View` or None.
    
.. attribute:: _form

    Form class associated with view. Default ``None``.
    
.. attribute:: isapp

    if ``True`` the view will be added to the application list and can have its own page object. Default ``False``.
    
.. attribute:: isplugin

    if ``True`` the view can be rendered as :class:`djpcms.plugins.ApplicationPlugin`.
    
    Default ``False``.

.. attribute:: in_navigation

    If ``0`` the view won't appear in :ref:`Navigation <topics-included-navigator>`.
    
    Default: ``0``
    
.. attribute:: view_template

    Template file or list of template files used to render
    the view (not the whole page).
    
    Default ``djpcms/components/pagination.html``.
    
.. attribute:: plugin_form

    The :attr:`djpcms.plugins.DJPplugin.form` for this view.
    
    Default ``None``.
    
.. attribute:: redirect_to_view

    String indicating a redirection to another view within the same application.
    Used in view with forms to define the behavior after a form has been subbmitted.
    It is used in :meth:`djpcms.views.basevew.djpcmsview.defaultredirect`
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

    If ``True`` and a page is not available for the view, the parent view page will be used (recursive).
    
    Default ``True``.
'''
    default_title = None
    creation_counter = 0
    description = None
    plugin_form    = None
    view_template  = 'djpcms/components/pagination.html'
    force_redirect = False
    astable = False
    isplugin = False
    regex = None
    in_nav = 0
    _form = None
    _form_ajax = None
    form_method = 'POST'
    
    def __init__(self,
                 regex = None,
                 parent = None,
                 insitemap = True,
                 isplugin = None,
                 description = None,
                 methods       = None,
                 plugin_form   = None,
                 renderer = None,
                 title = None,
                 linkname = None,
                 permission = None,
                 in_navigation = None,
                 template_name = None,
                 view_template = None,
                 force_redirect = None,
                 icon = None,
                 form = None,
                 form_ajax = None,
                 form_method = None,
                 list_display = None,
                 astable = None,
                 table_generator = None,
                 success_message = None,
                 redirect_to_view = None,
                 inherit_page = True,
                 append_slash = True,
                 **kwargs):
        self.name        = None
        self.description = description if description is not None else self.description
        self.parent    = parent
        self.isplugin  = isplugin if isplugin is not None else self.isplugin
        self.in_nav    = in_navigation if isinstance(in_navigation,int) else self.in_nav
        self.appmodel  = None
        self.insitemap = insitemap
        self.urlbit    = RegExUrl(regex if regex is not None else self.regex,
                                  append_slash)
        self.regex     = None
        self.func      = None
        self.code      = None
        self.inherit_page = inherit_page
        self.redirect_to_view = redirect_to_view
        self.list_display = list_display or self.list_display
        self.astable   = astable if astable is not None else self.astable
        self.template_name = template_name or self.template_name
        if self.template_name:
            t = self.template_name
            if not (isinstance(t,list) or isinstance(t,tuple)):
                t = (t,)
            self.template_name = tuple(t)
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
        if view_template:
            self.view_template = view_template
        if force_redirect is not None:
            self.force_redirect = force_redirect
        self._form     = form if form else self._form
        # Overrides
        self.PERM = permission if permission is not None else self.PERM
        self.ICON = icon if icon is not None else self.ICON
        self._methods = methods if methods else self._methods
        self.ajax_enabled = kwargs.pop('ajax_enabled',self.ajax_enabled)
        self._form_ajax = form_ajax if form_ajax is not None else self._form_ajax
        self.form_method = form_method or self.form_method
        self.plugin_form = plugin_form or self.plugin_form
        self.creation_counter = View.creation_counter
        View.creation_counter += 1
        
    @property
    def baseurl(self):
        if self.appmodel:
            return self.appmodel.baseurl
        else:
            return ''
    
    @property
    def model(self):
        if self.appmodel:
            return self.appmodel.model
    
    @property
    def site(self):
        if self.appmodel:
            return self.appmodel.site
    
    def route(self):
        if self.appmodel:
            return self.appmodel.route() + self.regex
        else:
            return self.regex
    
    def get_url(self, djp):
        return self.route().get_url(**djp.kwargs)
        
    def title(self, djp):
        title = None
        page = djp.page
        if page:
            title = page.title
        if not title:
            title = self.default_title or self.appmodel.description
        return title.format(djp.kwargs)
    
    def linkname(self, djp):
        link = None
        page = djp.page
        if page:
            link = page.link
        if not link:
            return self.title(djp)
        else:
            return link.format(djp.kwargs)
    
    def names(self):
        return self.regex.names
    
    def media(self):
        return self.appmodel.media()
    
    def in_navigation(self, request, page):
        if not self.appmodel.hidden:
            if page:
                if self.regex.names and page.url != self.path:
                    return 0
                else:
                    return page.in_navigation
            else:
                return self.in_nav
        else:
            return 0
    
    def isroot(self):
        '''True if this application view represents the root view of the application.'''
        return self.appmodel.root_view is self
    
    def get_form(self, djp,
                 form = None,
                 form_ajax = None,
                 method = None,
                 **kwargs):
        form_ajax = form_ajax if form_ajax is not None else self._form_ajax
        return self.appmodel.get_form(djp,
                                      form or self._form,
                                      form_ajax = form_ajax,
                                      method = method or self.form_method,
                                      **kwargs)
        
    def is_soft(self, djp):
        page = djp.page
        return False if not page else page.soft_root       
        
    def has_permission(self, request = None, page = None, obj = None, user = None):
        if super(View,self).has_permission(request, page, obj, user = user):
            return self.site.permissions.has(request, self.PERM, obj)
        else:
            return False
    
    def appquery(self, djp):
        '''This function implements the query, based on url entries.
By default it calls the :func:`djpcms.views.appsite.Application.basequery` function.'''
        return self.appmodel.basequery(djp)
    
    def table_generator(self, djp, qs):
        '''Generator of a table view. This function is invoked by :meth:`View.render_query`
when :attr:`View.astable` attribute is set to ``True``.'''
        return self.appmodel.table_generator(djp, qs)
    
    def data_generator(self, djp, qs):
        return self.appmodel.data_generator(djp, qs)
    
    def processurlbits(self, appmodel):
        '''Process url bits and store information for navigation and urls
        '''
        self.appmodel = appmodel
        if self.parent:
            self.regex = self.parent.regex + self.urlbit
        else:
            self.regex = self.urlbit
            
    def for_user(self, djp):
        return self.appmodel.for_user(djp)
    
    def warning_message(self, djp):
        return None
    
    def __deepcopy__(self, memo):
        return copy(self)  
    
    
class GroupView(View):
    '''An application to display list of children applications.
It is the equivalent of :class:`SearchView` for :class:`djpcms.views.Application`
without a model.'''
    astable = True # Table view by default
    def render(self, djp):
        qs = self.appquery(djp)
        return self.appmodel.render_query(djp, qs)
    
    
class ModelView(View):
    '''A :class:`View` class for views in :class:`djpcms.views.appsite.ModelApplication`.
    '''
    def defaultredirect(self, request, **kwargs):
        return model_defaultredirect(self, request, **kwargs)

    
class SearchView(ModelView):
    '''A :class:`ModelView` class for searching objects in a model.
By default :attr:`View.in_navigation` is set to ``True``.
There are three additional parameters that can be set:

:keyword astable: used to force the view not as a table. Default ``True``.
:keyword table_generator: Optional function to generate table content. Default ``None``.
:keyword search_text: string identifier for text queries.
    '''
    isplugin = True
    astable = 'ajax'
    in_nav = 1
    search_text = 'q'
    
    def appquery(self, djp):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        if self.astable == 'ajax' and not djp.request.is_xhr:
            return ()
        else:
            qs = super(SearchView,self).appquery(djp)
            request = djp.request
            search_string = request.REQUEST.get(self.search_text,None)
            if search_string:
                qs = qs.search(search_string)
            return qs
    
    def render(self, djp):
        '''Perform the custom query over the model objects and return a paginated result. By default it delegates the
renderint to the :method:`djpcms.views.Application.render_query` method.
        '''
        return self.appmodel.render_query(djp, self.appquery(djp))
            
    def ajax__autocomplete(self, djp):
        qs = self.appquery(djp)
        params = djp.request.REQUEST
        if 'maxRows' in params:
            qs = qs[:int(params['maxRows'])]
        return CustomHeaderBody('autocomplete',
                                list(self.appmodel.gen_autocomplete(qs)))
    
    def ajax_get_response(self, djp):
        data = djp.request.REQUEST
        if 'iSortingCols' in data:
            return ajax_dataTable(djp,data)
        return super(SearchView,self).ajax_get_response(djp)
    

class AddView(ModelView):
    PERM = djpcms.ADD
    ICON = 'ui-icon-circle-plus'
    ajax_enabled = False
    default_title = 'add'
    '''A :class:`ModelView` class which renders a form for adding instances
and handles the saving as default ``POST`` response.'''
    def __init__(self, regex = 'add', isplugin = True,
                 in_navigation = 1, **kwargs):
        super(AddView,self).__init__(regex  = regex,
                                     isplugin = isplugin,
                                     in_navigation = in_navigation,
                                     **kwargs)
    
    def save(self, request, f, commit = True):
        return self.appmodel.object_from_form(f, commit)
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return saveform(djp, force_redirect = self.force_redirect)
    
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        return model_defaultredirect(self, request, next = next,
                                     instance = instance, **kwargs)


class DeleteAllView(ModelView):
    '''An POST only :class:`ModelView` which deletes all objects
in a model. Quite drastic.'''
    PERM = djpcms.DELETEALL
    DEFAULT_METHOD = 'post'
    ICON = 'ui-icon-alert'
    default_title = 'delete all objects'
    ajax_enabled = True
    regex = 'deleteall'
    _methods = ('post',)
    
    def default_post(self, djp):
        self.appmodel.delete_all(djp)
        url = self.appmodel.root_view(djp).url
        if djp.request.is_xhr:
            return jredirect(url)
        else:
            return http.ResponseRedirect(url)
        
        
class ObjectView(ModelView):
    '''A :class:`ModelView` class view for model instances.
A view of this type has an embedded object available which is used to generate the full url.'''
    object_view = True
    
    def get_url(self, djp):
        kwargs = djp.kwargs
        instance=  None
        if 'instance' in kwargs:
            instance = kwargs['instance']
        if not isinstance(instance,self.model):
            request = getattr(djp,'request',None)
            instance = self.appmodel.get_object(request, **kwargs)
            if instance:
                djp.kwargs['instance'] = instance
        if instance:
            kwargs.update(self.appmodel.objectbits(instance))  
        else:
            raise http.Http404('Could not retrieve model instance\
 from url arguments: {0}'.format(djp.kwargs))
        
        return super(ObjectView,self).get_url(djp)

    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        return model_defaultredirect(self, request, next = next,
                                     instance = instance, **kwargs)
    

class ViewView(ObjectView):
    '''An :class:`djpcms.views.ObjectView` class specialised for displaying an object.
    '''
    default_title = '{0[instance]}'
    def __init__(self, regex = IDREGEX, **kwargs):
        super(ViewView,self).__init__(regex = regex, **kwargs)
    
    def linkname(self, djp):
        return str(djp.instance)
        
    def render(self, djp):
        '''Override the :meth:`djpcms.views.djpcmsview.render` method
to display a html string for an instance of the application model.
By default it calls the :meth:`djpcms.views.ModelApplication.render_object`
method of the :attr:`djpcms.views.View.appmodel` attribute.
        '''
        return self.appmodel.render_object(djp)
    
    def sitemapchildren(self):
        return self.appmodel.sitemapchildren(self)    
    
    
# Delete an object. POST method only. not GET method should modify databse
class DeleteView(ObjectView):
    '''An :class:`ObjectView` class specialised for deleting an object.
    '''
    PERM = djpcms.DELETE
    DEFAULT_METHOD = 'post'
    ajax_enabled = True
    default_title = 'delete {0[instance]}'
    _methods      = ('post',)
    
    def __init__(self, regex = 'delete', parent = 'view', **kwargs):
        super(DeleteView,self).__init__(regex = regex,
                                        parent = parent,
                                        **kwargs)
        
    def remove_object(self, instance):
        return self.appmodel.remove_object(instance)
    
    def default_post(self, djp):
        return deleteinstance(djp, force_redirect = self.force_redirect)
    
    def nextviewurl(self, djp):
        view = djp.view
        if view.object_view and getattr(view,'model',None) == self.model:
            return self.appmodel.root_view(djp).url
        else: 
            return djp.url
      

# Edit/Change an object
class ChangeView(ObjectView):
    PERM = djpcms.CHANGE
    default_title = 'edit {0[instance]}'
    '''An :class:`ObjectView` class specialised for changing an instance of a model.
    '''
    def __init__(self, regex = 'change', parent = 'view', **kwargs):
        super(ChangeView,self).__init__(regex = regex, parent = parent, **kwargs)
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def save(self, request, f, commit = True):
        return self.appmodel.object_from_form(f, commit)
    
    def default_post(self, djp):
        return saveform(djp, True, force_redirect = self.force_redirect)
    
