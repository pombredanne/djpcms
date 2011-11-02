import sys
import traceback
from copy import copy

import djpcms
from djpcms import forms, http, html
from djpcms.utils.ajax import jredirect, jservererror
from djpcms.template import loader
from djpcms.utils import lazyattr, logtrace
from djpcms.core.exceptions import ViewDoesNotExist, PermissionDenied,\
                                     PathException

from .navigation import Navigator, Breadcrumbs


__all__ = ['DjpResponse',
           'DummyDjp']

def formatline(line):
    if line.split()[0] == 'File':
        return '<p>{0}</p>'.format(line)
    else:
        return '<h3>{0}</h3>'.format(line)
    
def handle_ajax_error(self,e):
    #Internal function for handling AJAX server errors
    if self.root.settings.DEBUG:
        exc_info = sys.exc_info()
        logtrace(self.view.logger, self.request, exc_info)
        lines = traceback.format_exception(*exc_info)
        stack_trace = '\n'.join((formatline(line) for line in lines))
        #stack_trace = '<p>{0}</p>'.format(
        #            '</p>\n<p>'.join(lines))
        return jservererror(self.request, stack_trace)
    else:
        raise e


def get_template(self):
    page = self.page
    # First Check if page has a template
    if page and page.template:
        return page.template
    view = self.view
    t = view.template_name
    if not t and view.appmodel:
        t = view.appmodel.template_name
    de = self.site.settings.DEFAULT_TEMPLATE_NAME
    if t:
        if de not in t:
            t += de
        return t
    else:
        if page:
            return page.get_template()
        else:
            return de


class DjpResponse(djpcms.UnicodeMixin):
    '''Djpcms response class.
It contains information associated with a given path
which can, and often is, different from the current request path.
Usually, it is initialized by::

    djp = view(request, **kwargs)
    
where ``kwargs`` is a dictionary of parameters used to build the ``url``
(it can also include a model instance).

.. attribute:: request

    A HttpRequest instance containing the request environment information.
    
.. attribute:: view

    An instance of :class:`djpcms.views.djpcmsview` responsible for
    handling the response.
    
.. attribute:: url

    url associated with response.
    Note this url is not always the same as request.path.

.. attribute:: media

    Object carrying information about the media to be added to the HTML page.
    It is filled during rendering of all plugins and views.
    
.. attribute:: site

    Instance of the :class:`djpcms.apps.appsites.ApplicationSite`
    which own the response. If the :attr:`view` is available,
    it is the same value.
    
.. attribute:: root

    Web site holder.
'''
    block = None
    def __init__(self, request, view, **kwargs):
        self.request    = request
        self.view       = view
        self.kwargs     = kwargs
        site            = view.site
        self.site       = site
        self.settings   = site.settings
    
    def __unicode__(self):
        try:
            return self.url
        except:
            return self.view.__unicode__()
    
    def mapper(self, model):
        from djpcms.core.orms import mapper
        return mapper(model)
    
    @property
    def urldata(self):
        self.url
        return self.kwargs
    
    @property
    def root(self):
        return self.site.root
    
    @property
    def tree(self):
        return self.site.root.tree
    
    @lazyattr
    def node(self):
        '''Get the :class:`djpcms.views.sitemap.Node` in the global sitemap
which corresponds to ``self``'''
        try:
            url = self.url
            return self.tree[url]
        except:
            if self.view:
                return self.tree[self.view.path]
            else:
                raise

    @property
    def name(self):
        return self.view.name
        
    @property
    def linkname(self):
        if not hasattr(self,'_linkname'):
            self._linkname = self.view.linkname(self)
        return self._linkname
    
    @property    
    def title(self):
        if not hasattr(self,'_title'):
            return self.view.title(self)
        return self._title
    
    @property    
    def breadcrumb(self):
        if not hasattr(self,'_breadcrumb'):
            return self.view.breadcrumb(self)
        return self._breadcrumb
    
    def for_user(self):
        return self.view.for_user(self)
    
    def is_soft(self):
        return self.view.is_soft(self)
    
    def own_view(self):
        return self.url == self.request.path
    
    def set_content_type(self, ct):
        h = self._headers['content-type']
        h[1] = ct
        
    @property
    def media(self):
        return self.request.DJPCMS.media
    
    def getdata(self, name):
        '''Extract data out of url dictionary. Return ``None`` if ``name``
is not in the dictionary.'''
        self.url
        return self.kwargs.get(name,None)
    
    @lazyattr
    def in_navigation(self):
        return self.view.in_navigation(self.request, self.page)
    
    def render(self):
        '''\
Render the underlying view.
A shortcut for :meth:`djpcms.views.djpcmsview.render`'''
        self.media.add(self.view.media(self))
        return self.view.render(self)
    
    def djp(self, view):
        '''Create a new response base on view'''
        return view(self.request, **self.kwargs)
        
    @lazyattr
    def _get_page(self):
        '''Get the page object
        '''
        return self.node().page
    page = property(_get_page)
    
    @lazyattr
    def get_url(self):
        '''Build the url for this application view.'''
        return self.view.get_url(self)
    url = property(get_url)
    
    @lazyattr
    def _get_template(self):
        return get_template(self)
    template_file = property(_get_template)
    
    @lazyattr
    def _get_parent(self):
        '''Parent Response object, that is a response object associated with
the parent of the embedded view.'''
        node = self.node().ancestor
        if node:
            try:
                return node.get_view()(self.request, **self.urldata)
            except PathException:
                return None
    parent = property(_get_parent)
    
    @property
    def instance(self):
        if self.view.object_view:
            kwargs = self.kwargs
            if 'instance' not in kwargs:
                self.url
            return kwargs['instance']
        else:
            return self.kwargs.get('instance',None)
        
    def id(self):
        page = self.page
        if page:
            return page.id
        
    def application(self):
        appmodel = self.view.appmodel
        if appmodel:
            return appmodel.name
        
    def path(self):
        return self.view.path
    
    def route(self):
        return str(self.view.route())
    
    def doc_type(self):
        page = self.page
        return html.htmldoc(None if not page else page.doctype).name
    
    def html(self):
        '''Render itself'''
        return html.LazyRender(self)
            
    def robots(self):
        '''Robots
        '''
        if self.view.has_permission(self.request, self.page, user = None):
            if not self.page or self.page.insitemap:
                return 'ALL'
        return 'NONE,NOARCHIVE'
    
    def response(self):
        '''return the type of response or an instance of HttpResponse
        '''
        # Check for page view permissions
        request = self.request
        is_ajax = request.is_xhr
        try:
            if not self.has_permission():
                raise PermissionDenied()
            
            view    = self.view
            page    = self.page
            site    = self.site
            method  = request.method.lower()
            
            # chance to bail out early
            re = view.preprocess(self)
            if re:
                return re
                
            if not is_ajax:
                # If user not authenticated set a test cookie
                if hasattr(request,'user'):
                    if not request.user.is_authenticated() and method == 'get':
                        request.session.set_test_cookie()
    
                if method not in (m.lower() for m in view.methods(request)):
                    raise http.HttpException(status = 405,
                            msg = 'method {0} is not allowed'.format(method))
            
                return getattr(view,'%s_response' % method)(self)
            else:
                # AJAX RESPONSE
                if method not in (m.lower() for m in view.methods(request)):
                    raise ViewDoesNotExist(
                    'AJAX "{0}" method not available in view.'.format(method))
                data = request.REQUEST
                ajax_action = forms.get_ajax_action(data)
                ajax_view_function = getattr(view,'ajax_%s_response' % method)
                if ajax_action:
                    ajax_view = 'ajax__' + ajax_action
                    if hasattr(view,ajax_view):
                        ajax_view_function = getattr(view,ajax_view)
                    else:
                        ajax_view_function = getattr(view.appmodel,
                                                     ajax_view,
                                                     ajax_view_function)
                res = ajax_view_function(self)
                return http.Response(res.dumps(),
                                     content_type = res.mimetype())
        except Exception as e:
            if is_ajax:
                res = handle_ajax_error(self,e)
                return http.Response(res.dumps(),
                                         content_type = res.mimetype())
            else:
                raise
    
    def render_to_response(self, context):
        settings = self.settings
        sitenav = Navigator(self,
                            classes = settings.HTML.main_nav,
                            levels = settings.SITE_NAVIGATION_LEVELS)
        context.update({'robots':     self.robots(),
                        'media':      self.media,
                        'sitenav':    sitenav})
        if self.settings.ENABLE_BREADCRUMBS:
            b = getattr(self,'breadcrumbs',None)
            if b is None:
                b = Breadcrumbs(self,
                                min_length = self.settings.ENABLE_BREADCRUMBS)
            context['breadcrumbs'] = b
        
        context = loader.context(context, self.request)
        html = loader.render(self.template_file, context)
        html = html.encode('latin-1','replace')
        return http.Response(html,
                             content_type = 'text/html',
                             encoding = self.settings.DEFAULT_CHARSET)
        
    @djpcms.storegenarator
    def children(self):
        '''return a generator over children responses. It uses the
:func:`djpcms.node` to retrive the node in the sitemap and
consequently its children.'''
        node = self.node()
        request = self.request
        kwargs = self.kwargs
        for node in node.children():
            try:
                cdjp = node.get_view()(request,**kwargs)
                cdjp.url
                yield cdjp
            except:
                continue
    
    @djpcms.memoized
    def has_permission(self):
        return self.view.has_permission(self.request, self.page, self.instance)
    
    @djpcms.memoized
    def warning_message(self):
        return self.view.warning_message(self)
        
    @djpcms.storegenarator
    def auth_children(self):
        for c in self.children():
            if c.has_permission():
                yield c
                
    def redirect(self, url):
        if self.is_xhr:
            return jredirect(url = url)
        else:
            return http.ResponseRedirect(url)
        
    def instancecode(self):
        '''If an instance is available, return a unique code for it.
Otherwise return None.''' 
        instance = self.instance
        if not instance:
            return None
        appmodel = self.site.for_model(instance.__class__)
        if appmodel:
            return appmodel.instancecode(self.request, instance)
        else:
            return '%s:%s' % (instance._meta,instance.id)


class DummyDjp(object):
    '''A dummy :class:`djpcms.views.DjpResponse` class'''
    __slots__ = ('kwargs','page','url')
    def __init__(self, instance = None, kwargs = None, page = None, url = None):
        kwargs = kwargs if kwargs is not None else {}
        if instance:
            kwargs['instance'] = instance
        self.kwargs = kwargs
        self.page = page
        self.url = url
        
    @property
    def request(self):
        return None
    