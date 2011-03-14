import operator
import re
from copy import copy
from datetime import datetime

from py2py3 import zip

from djpcms import get_page
from djpcms.utils.translation import gettext as _
from djpcms.template import loader
from djpcms.forms import autocomplete
from djpcms.forms.utils import saveform, deleteinstance
from djpcms.utils import construct_search, isexact
from djpcms.utils.text import nicename
from djpcms.views.regex import RegExUrl
from djpcms.views.baseview import djpcmsview


__all__ = ['View',
           'GroupView',
           'ModelView',
           'SearchView',
           'AddView',
           'ObjectView',
           'ViewView',
           'DeleteView',
           'ChangeView',
           'AutocompleteView',
           'IDREGEX',
           'SLUG_REGEX']


IDREGEX = '(?P<id>\d+)'
SLUG_REGEX = '[-\.\+\#\'\:\w]+'

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

:keyword parent: A string indicating the closest parent application view.
                 If not supplied, ``djpcms`` will calculate it
                 during validation of the applications during startup. It is used to
                 assign a value to the :attr:`parent` attribute. Default ``None``.
:keyword regex: Regular expression string indicating the view relative url.
                This is the url which the view add to its parent url. Default ``None``.
:keyword isapp: If ``True`` the view will be treated as an application view and therefore added to the list
                of applications which can be associated with a :class:`djpcms.models.Page` object.
                Its value is assigned to the :attr:`isapp` attribute. Default ``False``.
:keyword isplugin: If ``True`` the view can be rendered as :class:`djpcms.plugins.ApplicationPlugin`.
                  Its value is assigned to the :attr:`isplugin` attribute. Default ``False``.
:keyword form: Form class or ``None``. If supplied it will be assigned to the :attr:`_form` attribute.
               It is a form which can be used for interaction. Default ``None``.
:keyword methods: Tuple used to specify the response method allowed ('get', 'post', put') ro ``None``.
                  If specified it replaces the :attr:`_methods` attribute.
                  Default ``None``.
:keyword view_template: Template file used to render the view. Default ``None``.
                        If specified it replaces the :attr:`view_template` attribute.
:keyword renderer: A one parameters functions which can be used to replace the
                   default :meth:`render` method. Default ``None``. The function
                   must return a safe string ready for rendering on a HTML page.
:keyword permission: A three parameters function which can be used to
                     replace the default :meth:`_has_permission` method.
                     Default ``None``. The function
                     return a boolean and takes the form::
                     
                         def permission(view, request, obj):
                             ...
                         
                     where ``self`` is an instance of the view, ``request`` is the HTTP request instance and
                     ``obj`` is an instance of model or ``None``.
:keyword headers: List of string to display as table header when the
                  view display a table. Default ``None``.

:keyword force_redirect: Boolean used to force redirect after form submission.
                         Check :attr:`force_redirect` for more information. Default: ``False``.
:keyword redirect_to_view: String indicating a redirection to another view within
                           the same application. Check :attr:`redirect_to_view`
                           for more information. Default: ``None``.
    
    
Usage::

    from djpcms.views import appview, appsite
    
    class MyApplication(appsite.ApplicationBase):
        home = appview.View(renderer = lambda s, djp : 'Hello world')
        test = appview.View(regex = 'testview', renderer = lambda s, djp : 'Another view')
    
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

    This flag is used often used in conjunction with :attr:`redirect_to_view`
    to force a redirect after a form submission. For example::
    
        class MyApp(appsite.ModelApplication):
            search = ...
            add = appview.AddView(redirect_to_view = 'search',
                                  force_redirect = True) 
    
    This attribute is used to fine-tune the response of your web site.
    
    Default: ``False``.
    
.. attribute:: inherit_page

    If ``True`` and a page is not available for the view, the parent view page will be used (recursive).
    
    Default ``True``.
'''
    default_title = None
    creation_counter = 0
    plugin_form    = None
    view_template  = 'djpcms/components/pagination.html'
    force_redirect = False
    headers        = None
    astable        = False
    _form          = None
    _form_ajax     = None
    
    def __init__(self,
                 parent        = None,
                 regex         = None,
                 splitregex    = False,
                 insitemap     = True,
                 isapp         = False,
                 isplugin      = False,
                 methods       = None,
                 plugin_form   = None,
                 renderer      = None,
                 title         = None,
                 permission    = None,
                 in_navigation = 0,
                 template_name = None,
                 view_template = None,
                 description    = None,
                 force_redirect = None,
                 form           = None,
                 form_ajax     = None,
                 headers       = None,
                 astable        = None,
                 table_generator = None,
                 success_message = None,
                 redirect_to_view = None,
                 inherit_page = True,
                 append_slash = True):
        self.name        = None
        self.description = description
        self.parent    = parent
        self.isapp     = isapp
        self.isplugin  = isplugin
        self.in_nav    = int(in_navigation)
        self.appmodel  = None
        self.insitemap = insitemap
        self.urlbit    = RegExUrl(regex,splitregex,append_slash)
        self.regex     = None
        self.func      = None
        self.code      = None
        self.editurl   = None
        self.inherit_page = inherit_page
        self.redirect_to_view = redirect_to_view
        self.headers   = headers or self.headers
        self.astable   = astable if astable is not None else self.astable
        self.template_name = template_name or self.template_name
        if self.template_name:
            t = self.template_name
            if not (isinstance(t,list) or isinstance(t,tuple)):
                t = (t,)
            self.template_name = tuple(t)
        if title:
            self.title = title 
        if table_generator:
            self.table_generator = table_generator
        if renderer:
            self.render = renderer
        if permission:
            self._has_permission = permission
        if methods:
            self._methods = methods
        if success_message:
            self.success_message = success_message
        if view_template:
            self.view_template = view_template
        if force_redirect is not None:
            self.force_redirect = force_redirect
        self._form     = form if form else self._form
        self._form_ajax  = form_ajax if form_ajax is not None else self._form_ajax
        self.plugin_form = plugin_form or self.plugin_form
        self.creation_counter = View.creation_counter
        View.creation_counter += 1
        
    def __get_baseurl(self):
        return self.appmodel.baseurl
    baseurl = property(__get_baseurl)
    
    def __get_model(self):
        return getattr(self.appmodel,'model',None)
    model = property(fget = __get_model)
    
    @property
    def site(self):
        return self.appmodel.site
    
    def path(self):
        return self.appmodel.path() + self.regex.purl
    
    def get_url(self, djp):
        return self.appmodel.path() + self.regex.get_url(**djp.kwargs)
        
    def title(self, djp):
        page = djp.page
        if page:
            title = page.title
        else:
            title = self.default_title or self.appmodel.description
        return title.format({'instance':self.appmodel.title_object(djp.instance)})
    
    def linkname(self, djp):
        page = djp.page
        if page:
            link = page.link
        else:
            link = self.default_title or self.appmodel.name
        return link.format({'instance':self.appmodel.title_object(djp.instance)})
    
    def names(self):
        return self.regex.names
    
    def get_media(self):
        return self.appmodel.media
    
    def in_navigation(self, request, page):
        if not self.appmodel.hidden:
            if page:
                if self.regex.names and not page.url_pattern:
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
                 **kwargs):
        form_ajax = form_ajax if form_ajax is not None else self._form_ajax
        return self.appmodel.get_form(djp,
                                      form or self._form,
                                      form_ajax = form_ajax,
                                      **kwargs)
        
    def is_soft(self, djp):
        page = djp.page
        return False if not page else page.soft_root
        
    def get_page(self, djp):
        page = get_page(djp.url)
        if not page and djp.url != self.path():
            page = get_page(djp.url)
        return page            
        
    def has_permission(self, request = None, page = None, obj = None, user = None):
        if super(View,self).has_permission(request, page, obj, user = user):
            return self._has_permission(request, obj)
        else:
            return False
        
    def _has_permission(self, request, obj):
        return self.appmodel.has_permission(request, obj)
    
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
    def __init__(self, isapp = True, splitregex = True, **kwargs):
        super(ModelView,self).__init__(isapp = isapp,
                                       splitregex = splitregex,
                                       **kwargs)
    
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
    search_text = 'q'
    '''identifier for queries. Default ``q``.'''
    
    def __init__(self, in_navigation = 1, astable = True, search_text = None, **kwargs):
        self.search_text = search_text or self.search_text
        super(SearchView,self).__init__(in_navigation=in_navigation,
                                        astable=astable,
                                        **kwargs)
    
    def appquery(self, djp):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        qs = super(SearchView,self).appquery(djp)
        request = djp.request
        slist = self.appmodel.search_fields
        search_string = request.data_dict.get(self.search_text,None)
        if slist and search_string:
            bits  = smart_split(search_string)
            #bits  = search_string.split(' ')
            for bit in bits:
                bit = isexact(bit)
                if not bit:
                    continue
                or_queries = [Q(**{construct_search(field_name): bit}) for field_name in slist]
                other_qs   = QuerySet(self.appmodel.modelsearch())
                other_qs.dup_select_related(qs)
                other_qs   = other_qs.filter(reduce(operator.or_, or_queries))
                qs         = qs & other_qs    
        return qs
    
    def render(self, djp):
        '''Perform the custom query over the model objects and return a paginated result
        '''
        qs = self.appquery(djp)
        return self.appmodel.render_query(djp, qs)  


class AddView(ModelView):
    default_title = 'add'
    '''A :class:`ModelView` class which renders a form for adding instances
and handles the saving as default ``POST`` response.'''
    def __init__(self, regex = 'add', isplugin = True,
                 in_navigation = 1, **kwargs):
        super(AddView,self).__init__(regex  = regex,
                                     isplugin = isplugin,
                                     in_navigation = in_navigation,
                                     **kwargs)
    
    def _has_permission(self, request, obj):
        return self.appmodel.has_add_permission(request, obj)
    
    def save(self, request, f):
        return self.appmodel.object_from_form(f)
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return saveform(djp, False, force_redirect = self.force_redirect)
    
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        return model_defaultredirect(self, request, next = next,
                                     instance = instance, **kwargs)

            
class ObjectView(ModelView):
    '''A :class:`ModelView` class view for model instances.
A view of this type has an embedded object available which is used to generate the full url.'''
    object_view = True
    
    def get_url(self, djp):
        kwargs = djp.kwargs
        instance=  None
        if 'instance' in kwargs:
            instance = kwargs['instance']
        if instance:
            kwargs.update(self.appmodel.objectbits(instance))
        else:
            request = getattr(djp,'request',None)
            instance = self.appmodel.get_object(request, **kwargs)
            djp.kwargs['instance'] = instance  
        
        if not instance:
            raise djp.http.Http404
        
        return super(ObjectView,self).get_url(djp)
    
    def title(self, djp):
        return self.appmodel.title_object(djp.instance)

    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        return model_defaultredirect(self, request, next = next,
                                     instance = instance, **kwargs)
    

class ViewView(ObjectView):
    '''An :class:`djpcms.views.ObjectView` class specialised for displaying an object.
    '''
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
    default_title = 'delete'
    _methods      = ('post',)
    
    def __init__(self, regex = 'delete', parent = 'view', isapp = False, **kwargs):
        super(DeleteView,self).__init__(regex = regex,
                                        parent = parent,
                                        isapp = isapp,
                                        **kwargs)
        
    def _has_permission(self, request, obj):
        return self.appmodel.has_delete_permission(request, obj)
    
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
    default_title = 'edit {0}'
    '''An :class:`ObjectView` class specialised for changing an instance of a model.
    '''
    def __init__(self, regex = 'edit', parent = 'view', **kwargs):
        super(ChangeView,self).__init__(regex = regex, parent = parent, **kwargs)
    
    def _has_permission(self, request, obj):
        return self.appmodel.has_change_permission(request, obj)
    
    def title(self, djp):
        page = djp.page
        if page and page.title:
            title = page.tile
        else:
            title = self.default_title
        return title.format({'instance':self.appmodel.title_object(djp.instance)})
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def save(self, request, f, commit = True):
        return self.appmodel.object_from_form(f, commit)
    
    def default_post(self, djp):
        return saveform(djp, True, force_redirect = self.force_redirect)
    

class AutocompleteView(SearchView):
    '''This is an interesting :class:View` class.
It is an **AJAX Get only** view for :ref:`auto-complete <autocomplete>` functionalities.
To use it, add it to a :class:`djpcms.views.appsite.ModelApplication` declaration.

Let's say you have a model::

    from django.db import models
    
    class MyModel(models.Model):
        name = models.CharField(max_length = 60)
        description = models.TextField()
    
And we would like to have an auto-complete view which displays the ``name`` field and search for both
``name`` and ``description`` fields::

    from djpcms.views.appsite import ModelApplication
    
    class MyModelApp(ModelApplication):
        search_fields = ['name','description']
        complete = AutocompleteView(display = 'name')
        
    appsite.site.register('/mymodelurl/', MyModelApp, model = MyModel)
    
The last bit of information is to use a different ``ModelChoiceField`` and ``ModelMultipleChoiceField`` in
your forms. Rather than doing::

    from django.forms import ModelChoiceField, ModelMultipleChoiceField
    
do::
    
    from djpcms.forms import ModelChoiceField, ModelMultipleChoiceField
    
and if your model has an AutocompleteView installed, it will work out of the box.
'''
    _methods = ('get',)
    
    def __init__(self, regex = 'autocomplete', display = 'name', **kwargs):
        self.display = display
        super(AutocompleteView,self).__init__(regex = regex, **kwargs)
        
    def processurlbits(self, appmodel):
        super(AutocompleteView,self).processurlbits(appmodel)
        autocomplete.register(self.appmodel.model,self)
    
    def get_url(self, *args, **kwargs):
        purl = self.regex.get_url()
        return '%s%s' % (self.baseurl,purl)
        
    def get_response(self, djp):
        '''This response works only if it is an AJAX response. Otherwise it raises a ``Http404`` exception.'''
        request = djp.request
        if not request.is_ajax():
            raise djp.http.Http404
        params = dict(request.GET.items())
        query = request.GET.get('q', None)
        search_fields = self.appmodel.search_fields
        if query and search_fields:
            q = None
            for field_name in search_fields:
                name = construct_search(field_name)
                if q:
                    q = q | Q( **{str(name):query} )
                else:
                    rel_name = name.split('__')[0]
                    q = Q( **{str(name):query} )
            qs = self.model.objects.filter(q)                    
            data = ''.join(['%s|%s|%s\n' % (getattr(f,rel_name),f,f.pk) for f in qs])
        else:
            data = ''
        return djp.http.HttpResponse(data)

