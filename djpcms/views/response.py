import sys
import traceback
from copy import copy

import djpcms
from djpcms.utils.ajax import jredirect, jservererror
from djpcms.template import loader
from djpcms.utils import lazyattr, storegenarator, logtrace
from djpcms.core.exceptions import ViewDoesNotExist, PermissionDenied, PathException
from djpcms.html.utils import LazyRender

from .navigation import Navigator, Breadcrumbs


__all__ = ['DjpResponse',
           'DummyDjp']


def handle_ajax_error(self,e):
    #Internal function for handling AJAX server errors
    if self.site.settings.DEBUG:
        exc_info = sys.exc_info()
        logtrace(self.view.logger, self.request, exc_info)
        stack_trace = '<p>{0}</p>'.format('</p>\n<p>'.join(traceback.format_exception(*exc_info)))
        return jservererror(stack_trace, url = self.url)
    else:
        raise e


def get_template(self):
    page = self.page
    # First Check if page has a template
    if page:
        if page.template:
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
    '''Djpcms response class. It contains information associated with a given url
which can and often is different from the current request path. Usually is initialized as::

    djp = view(request, **kwargs)
    
where ``kwargs`` is a fictionary of arguments used to build the ``url`` (including 
model instances).
        
.. attribute:: request

    a HttpRequest instance containing the request environment information.
    
.. attribute:: view

    An instance of :class:`djpcms.views.baseview.djpcmsview` responsible for
    handling the request.
    
.. attribute:: url

    url associated with response. Note this url is not always the same as request.path.

.. attribute:: media

    Object carrying information about the media to be added to the HTML page.
    It is filled during rendering of all plugins and views.
'''
    def __init__(self, request, view, wrapper = None, prefix = None, **kwargs):
        self.request    = request
        self.view       = view
        self.kwargs     = kwargs
        site            = view.site
        self.site       = site
        self.settings   = site.settings
        self.http       = site.http
        self.wrapper    = wrapper
        self.prefix     = prefix
    
    def __unicode__(self):
        try:
            return self.url
        except:
            return self.view.__unicode__()
    
    def mapper(self, model):
        from djpcms.core.orms import mapper
        return mapper(model)
    
    @property
    def css(self):
        return self.settings.HTML_CLASSES
    
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
        url = self.url
        try:
            return self.tree[url]
        except KeyError:
            if self.view:
                return self.tree[self.view.path()]
            else:
                raise
    
    def is_soft(self):
        return self.view.is_soft(self)
    
    def own_view(self):
        return self.url == self.request.path
    
    def get_linkname(self):
        return self.view.linkname(self) or self.url
    linkname = property(get_linkname)
        
    def get_title(self):
        return self.view.title(self)
    title = property(get_title)
    
    def bodybits(self):
        return self.view.bodybits(self.page)
    
    def contentbits(self):
        return self.view.contentbits(self.page)
    
    def set_content_type(self, ct):
        h = self._headers['content-type']
        h[1] = ct
        
    def __get_media(self):
        media = getattr(self,'_media',None)
        if not media:
            media = self.view.get_media()
            setattr(self,'_media',media)
        return media
    def __set_media(self, other):
        setattr(self,'_media',other)
    media = property(__get_media,__set_media)
    
    def getdata(self, name):
        '''Extract data out of url dictionary. Return ``None`` if ``name`` is not in the dictionary.'''
        self.url
        return self.kwargs.get(name,None)
    
    @lazyattr
    def in_navigation(self):
        return self.view.in_navigation(self.request, self.page)
    
    def render(self):
        '''\
Render the underlying view.
A shortcut for :meth:`djpcms.views.djpcmsview.render`'''
        return self.view.render(self)
        
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
        
    def html(self):
        '''Render itself'''
        return LazyRender(self)
            
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
        view    = self.view
        request = self.request
        is_ajax = request.is_xhr
        page    = self.page
        site    = self.site
        http    = site.http
        method  = request.method.lower()
        
        # Check for page view permissions
        if not view.has_permission(request, page, self.instance):
            raise PermissionDenied()
        
        # chanse to bail out early
        re = view.preprocess(self)
        if isinstance(re,http.HttpResponse):
            return re
            
        if not is_ajax:
            # If user not authenticated set a test cookie
            if hasattr(request,'user'):
                if not request.user.is_authenticated() and method == 'get':
                    request.session.set_test_cookie()

            if method not in (m.lower() for m in view.methods(request)):
                raise http.HttpException(405,
                                         msg='method {0} is not allowed'.format(method))
        
            return getattr(view,'%s_response' % method)(self)
        else:
            # AJAX RESPONSE
            try:
                if method not in (m.lower() for m in view.methods(request)):
                    raise ViewDoesNotExist('{0} method not available'.format(method))
                res = getattr(view,'ajax_%s_response' % method)(self)
            except ViewDoesNotExist as e:
                res = jservererror(str(e), url = request.path)
            except Exception as e:
                res = handle_ajax_error(self,e)
            try:
                return self.http.HttpResponse(res.dumps(),
                                              mimetype = res.mimetype())
            except Exception as e:
                res = handle_ajax_error(self,e)
                return self.http.HttpResponse(res.dumps(),
                                              mimetype = res.mimetype())
    
    def render_to_response(self, context):
        css = self.css
        sitenav = Navigator(self,
                            classes = css.main_nav,
                            levels = self.settings.SITE_NAVIGATION_LEVELS)
        
        context.update({'robots':     self.robots(),
                        'media':      self.media,
                        'sitenav':    sitenav})
        if self.settings.ENABLE_BREADCRUMBS:
            b = getattr(self,'breadcrumbs',None)
            if b is None:
                b = Breadcrumbs(self,min_length = self.settings.ENABLE_BREADCRUMBS)
            context['breadcrumbs'] = b
        
        context = loader.context(context, self.request)
        html = loader.mark_safe(loader.render(self.template_file,
                                              context))
        return self.http.HttpResponse(html,mimetype = 'text/html')
        
    @storegenarator
    def children(self):
        '''return a generator over children responses. It uses the
:func:`djpcms.node` to retrive the node in the sitemap and cosequently its children.'''
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
            
    @storegenarator
    def auth_children(self):
        request = self.request
        for c in self.children():
            if c.view.has_permission(request, c.page):
                yield c
                
    def redirect(self, url):
        if self.is_xhr:
            return jredirect(url = url)
        else:
            return self.http.HttpResponseRedirect(url)
        
    def instancecode(self):
        '''If an instance is available, return a unique code for it. Otherwise return None.''' 
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
    