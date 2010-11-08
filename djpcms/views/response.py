from copy import copy

from django import http
from django.shortcuts import render_to_response
from django.template import RequestContext

from djpcms.conf import settings
from djpcms.uploads import apply_styling
from djpcms.utils.ajax import jredirect, jhtmls
from djpcms.template import Template, Context
from djpcms.utils import lazyattr, mark_safe, smart_str
from djpcms.utils.navigation import Navigator, Breadcrumbs


class DjpResponse(http.HttpResponse):
    '''Djpcms Http Response class. It which contains information associated with a given url.
        
        .. attribute: request
        
            a HttpRequest instance
            
        .. attribute: view
        
            instance of :class:`djpcms.views.baseview.djpcmsview`
            
        .. attribute: url
        
            url associated with response. Note this url is not always the same as request.path.
    '''
    def __init__(self, request, view, *args, **kwargs):
        super(DjpResponse,self).__init__()
        self._container = None
        self.request    = request
        self.view       = view
        self.css        = settings.HTML_CLASSES
        self.args       = args
        self.kwargs     = kwargs
        self.wrapper    = None
        self.prefix     = None
        self._errors    = None
        self.media      = view.get_media()
        self._plugincss = {}
    
    def __repr__(self):
        return self.url
    
    def __str__(self):
        return self.__repr__()
    
    def __call__(self, prefix = None, wrapper = None):
        djp = copy.copy(self)
        djp.prefix  = prefix
        djp.wrapper = wrapper
        return djp
    
    def adderror(self, msg):
        err = self._errors
        if not err:
            err = []
        err.append(msg)
        self._errors = err
    
    def is_ajax(self):
        return self.request.is_ajax()
    
    def is_soft(self):
        return self.view.is_soft(self)
    
    def own_view(self):
        return self.url == self.request.path
    
    def get_linkname(self):
        return self.view.linkname(self) or self.url
    linkname = property(get_linkname)
        
    def get_title(self):
        return self.view.title(self.page, **self.kwargs)
    title = property(get_title)
    
    def bodybits(self):
        return self.view.bodybits(self.page)
    
    def contentbits(self):
        return self.view.contentbits(self.page)
    
    def set_content_type(self, ct):
        h = self._headers['content-type']
        h[1] = ct
        
    @lazyattr
    def in_navigation(self):
        return self.view.in_navigation(self.request, self.page)
    
    @lazyattr
    def _get_page(self):
        '''Get the page object
        '''
        return self.view.get_page(self)
    page = property(_get_page)
    
    @lazyattr
    def get_url(self):
        '''
        Build the url for this application view
        '''
        return self.view.get_url(self, **self.kwargs)
    url = property(get_url)
    
    @lazyattr
    def _get_template(self):
        return self.view.get_template(self.page)
    template_file = property(_get_template)
    
    @lazyattr
    def _get_parent(self):
        '''
        Parent Response object
        '''
        return self.view.parentresponse(self)
    parent = property(_get_parent)
    
    @lazyattr
    def get_children(self):
        self.instance
        return self.view.children(self, **self.kwargs) or []
    children = property(get_children)
    
    def _get_instance(self):
        instance = self.kwargs.get('instance',None)
        if not instance:
            self.url
            return self.kwargs.get('instance',None)
        else:
            return instance
    def _set_instance(self, instance):
        self.kwargs['instance'] = instance
    instance = property(fget = _get_instance, fset = _set_instance)
    
    def has_own_page(self):
        '''Return ``True`` if the response has its own :class:djpcms.models.Page` object.
        '''
        page = self.page
        if page:
            appv = getattr(self.view,'code',None)
            if appv:
                return page.application_view == appv
            else:
                return page.url == self.url
        return False
            
    
    def robots(self):
        '''
        Robots
        '''
        if self.view.has_permission(None, self.instance):
            if not self.page or self.page.insitemap:
                return u'ALL'
        return u'NONE,NOARCHIVE'
        
    def response(self):
        '''return the type of response or an instance of HttpResponse
        '''
        view    = self.view
        request = self.request
        is_ajax = request.is_ajax()
        
        # Check for page view permissions
        if not view.has_permission(request, self.page, self.instance):
            return view.permissionDenied(self)
        
        method  = request.method.lower()
        methods = view.methods(request)
        if method not in (method.lower() for method in methods):
            return http.HttpResponseNotAllowed(methods)
        
        func = getattr(view,'%s_response' % method,None)
        if not func:
            raise ValueError("Allowed view method %s does not exist in %s." % (method,view))
        
        return func(self)        
    
    def render_to_response(self, more_context = None,
                           template_file = None, **kwargs):
        """
        A shortcut method that runs the `render_to_response` Django shortcut.
 
        It will apply the view's context object as the context for rendering
        the template. Additional context variables may be passed in, similar
        to the `render_to_response` shortcut.
 
        """
        css = self.css
        context  = RequestContext(self.request)
        d = context.push()
        if more_context:
            d.update(more_context)
        media = self.media
        style = apply_styling(self.request)
        if style:
            media.add_css(style)
        sitenav = Navigator(self,
                            classes = css.main_nav,
                            levels = settings.SITE_NAVIGATION_LEVELS)
        d.update({'djp':        self,
                  'media':      media,
                  'page':       self.page,
                  'cssajax':    self.css,
                  'is_popup':   False,
                  'admin_site': False,
                  'sitenav':    sitenav})
        if settings.ENABLE_BREADCRUMBS:
            b = getattr(self,'breadcrumbs',None)
            if b is None:
                 b = Breadcrumbs(self,min_length = settings.ENABLE_BREADCRUMBS)
            d['breadcrumbs'] = b
        template_file = template_file or self.template_file
        return render_to_response(template_file, context_instance=context, **kwargs)
        
    def redirect(self, url):
        if self.request.is_ajax():
            return jredirect(url = url)
        else:
            return http.HttpResponseRedirect(url)
        
    def instancecode(self):
        '''If an instance is available, return a unique code for it. Otherwise return None.'''
        from djpcms.views import appsite 
        instance = self.instance
        if not instance:
            return None
        appmodel = appsite.site.for_model(instance.__class__)
        if appmodel:
            return appmodel.instancecode(self.request, instance)
        else:
            return '%s:%s' % (instance._meta,instance.id)
    