import logging

try:
    range = xrange
except:
    pass

import djpcms
from djpcms.utils.ajax import jservererror, jredirect
from djpcms.html import grid960, box, htmldoc
from djpcms.forms import Media
from djpcms.forms.utils import saveform, get_form
from djpcms.views.response import DjpResponse
from djpcms.views.contentgenerator import BlockContentGen
from djpcms.template import loader
from djpcms.core.exceptions import PermissionDenied

    
def response_from_page(djp, page):
    '''Given a :class:`djpcms.views.DjpResponse` object
and a Page instance, it calculates a new response object.'''
    from djpcms import sites
    if page:
        url = page.url.format(**djp.kwargs)
        site, view, kwargs = sites.resolve(url[1:])
        return view(djp.request)
    else:
        return None
    

def page_edit_url(djp):
    site = djp.site 
    page = djp.page
    request = djp.request
    kwargs = {'path':request.path[1:]}
    if djp.has_own_page():
        if djp.site.has_permission(djp.request,djpcms.CHANGE,page):
            return site.get_url(page.__class__,'change',**kwargs)
    else:
        if djp.site.has_permission(djp.request,djpcms.ADD,page):
            return site.get_url(page.__class__,'add',**kwargs)
        


# THE DJPCMS BASE CLASS for handling views
class djpcmsview(object):
    '''Base class for handling http requests.
    
    .. attribute:: _methods

        Tuple of request methods handled by ``self``. By default ``GET`` and ``POST`` only::
        
            _methods = ('get','post')
    '''
    logger = logging.getLogger('djpcmsview')
    
    template_name = None
    '''Used to override the template name in the :class:`djpcms.models.Page` model instance (if it exists).
Not used very often but here just in case.'''
    parent        = None
    '''The parent view of ``self``. An instance of :class:`djpcmsview` or ``None``'''
    purl          = None
    
    name          = 'flat'
    '''Name of view. Default ``"flat"``.'''
    object_view = False
    '''Flag indicationg if the view class is used to render or manipulate model instances. Default ``False``.'''
    
    _methods      = ('get','post')

    def get_media(self):
        return Media()
    
    def names(self):
        return None
    
    def get_url(self, djp, **urlargs):
        return djp.request.path
    
    def get_page(self, djp):
        '''The :class:`djpcms.models.Page` instances associated with this view.'''
        return None
    
    def is_soft(self, djp):
        return not self.parentresponse(djp)
    
    def __call__(self, request, **kwargs):
        return DjpResponse(request, self, **kwargs)
    
    def methods(self, request):
        '''Allowed request methods for this view.
        By default it returns :attr:`_methods`.
        '''
        return self._methods
    
    def get_template(self, request, page = None):
        '''Given a :class:`djpcms.models.Page` instance, which may be ``None``,
returns the template file for rendering the page.

:parameter request: Http Request instance.
:parameter page: Page instance or ``None``.

If :attr:`template_name` is specified, it uses it, otherwise if ``page`` is available,
it gets the template from :meth:`djpcms.models.Page.get_template`.
If *page* is ``None`` it returns :setting:`DEFAULT_TEMPLATE_NAME`.'''
        # First Check if page has a template
        if page:
            if page.template:
                return page.template
        t = self.template_name
        de = request.site.settings.DEFAULT_TEMPLATE_NAME
        if t:
            if de not in t:
                t += de
            return t
        else:
            if page:
                return page.get_template()
            else:
                return de
        
    def title(self, djp):
        '''View title.'''
        page = djp.page
        if page:
            return page.title
        else:
            return None
    
    def linkname(self, djp):
        page = djp.page
        if page:
            return page.link
        else:
            return 'link'
    
    def parentresponse(self, djp):
        return response_from_page(djp, djp.page.parent)
    
    def specialkwargs(self, page, kwargs):
        return kwargs
    
    def render(self, djp, **kwargs):
        '''Render the Current View plugin and return safe unicode.
        This function is implemented by application views
        '''
        return ''
    
    def preprocess(self, djp):
        pass
    
    def extra_content(self, djp, c):
        pass
    
    def get_context(self, djp, editing = False):
        request = djp.request
        site    = request.site
        http    = request.site.http
        page    = djp.page
        inner_template  = None
        grid    = self.grid960(page)
        
        context = {'grid': grid,
                   'htmldoc': htmldoc(None if not page else page.doctype)}
            
        if page:
            inner_template = page.inner_template
            if not inner_template:
                inner_template = site.add_default_inner_template(page)
            if not editing:
                context['edit_content_url'] = page_edit_url(djp)
            
        if inner_template:
            cb = {'djp':  djp,
                  'grid': grid}
            for b in range(inner_template.numblocks()):
                cb['content%s' % b] = BlockContentGen(djp, b, editing)
            inner = page.inner_template.render(loader.context(cb, autoescape=False))
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)
            if isinstance(inner,http.HttpResponse):
                return inner
        
        context['inner'] = inner
        return context
    
    def ajax_get_response(self, djp):
        return jservererror('AJAX GET RESPONSE NOT AVAILABLE', url = djp.url)

    def get_response(self, djp):
        '''Get response handler.'''
        context = self.get_context(djp)
        return djp.render_to_response(context)
    
    def post_response(self, djp):
        '''Get response handler.'''
        raise NotImplementedError('Post response not implemented')
    
    def ajax_post_response(self, djp):
        request   = djp.request
        post      = request.POST
        
        params   = dict(post.items())
        prefix   = params.get('_prefixed',None)
        ajax_key = params.get(djp.css.post_view_key, None)
        if ajax_key:
            if prefix and prefix in ajax_key:
                ajax_key = ajax_key[len(prefix)+1:]
            ajax_key = ajax_key.replace('-','_').lower()
            
        # Handle the cancel request redirect.
        # Check for next in the parameters,
        # If not there redirect to self.defaultredirect
        if ajax_key == 'cancel':
            next = params.get('next',None)
            next = self.defaultredirect(djp.request, next = next, **djp.kwargs)
            return jredirect(next)
        else:
            ajax_view_function = None
            if ajax_key:
                ajax_view = 'ajax__%s' % ajax_key
                ajax_view_function  = getattr(self,str(ajax_view),None)
            
            # No post view function found. Let's try the default ajax post view
            if not ajax_view_function:
                ajax_view_function = self.default_post;
        
            return ajax_view_function(djp)

    def grid960(self, page = None):
        #TODO Need to move this out of here
        if page and page.cssinfo:
            return grid960(columns = page.cssinfo.gridsize, fixed = page.cssinfo.fixed)
        else:
            return grid960()
    
    def has_permission(self, request, page = None, obj = None):
        '''Check for page view permissions.'''
        if page:
            return request.site.has_permission(request,djpcms.VIEW,page)
        else:
            return True
    
    def in_navigation(self, request, page):
        '''
        Hook for modifying the in_navigation property.
        This default implementation should suffice
        '''
        if page:
            return page.in_navigation
        else:
            return 0
    
    def bodybits(self, page):
        return ''
        if self.editurl:
            b = 'class="edit"'
        elif page:
            css = page.cssinfo
            if css and css.body_class_name:
                b = 'class="%s"' % css.body_class_name
        return mark_safe(b)
    
    def contentbits(self, page):
        return ''
        b = ''
        if page:
            css = page.cssinfo
            if css and css.container_class_name:
                b = ' class="%s"' % css.container_class_name
        return mark_safe(b)
    
    def permissionDenied(self, djp):
        raise PermissionDenied
    
    def defaultredirect(self, request, next = None,
                        instance = None, **kwargs):
        '''This function is used to build a redirect ``url`` for ``self``.
It is called by ``djpcms`` only when a redirect is needed.

:parameter request: HttpRequest object.
:parameter url: optional ``url`` provided.
:parameter instance: optional instance of a model.
:parameter kwargs: additional url bits.

By default it returns ``next`` if available, otherwise ``request.path``.
'''
        if next:
            return request.build_absolute_uri(next)
        else:
            return request.environ.get('HTTP_REFERER')
    
    def children(self, djp, instance = None, **kwargs):
        '''Return children permitted views for self.
It includes views not in navigation. In scanning for children we porposefully
leave a possible object instance out of the key-values arguments.
If we didn't do that, test_navigation.testMultiPageApplication would fail.'''
        views = []
        page  = djp.page
        request = djp.request
        if not page:
            return views
        
        site      = djp.site
        pagecache = djp.pagecache
        pchildren = pagecache.get_children(page)
        
        for child in pchildren:
            try:
                cview = pagecache.view_from_page(child, site = site)
            except djp.http.Http404:
                continue
            if cview.has_permission(request, child, instance):
                cdjp = cview(request, **cview.specialkwargs(child,kwargs))
                try:
                    cdjp.url
                except:
                    continue
                views.append(cdjp)
        return views
    
#    def redirect(self, url):
#        '''Shortcut function for redirecting to *url*.'''
#        return http.HttpResponseRedirect(url)

    def nextviewurl(self, djp):
        '''Calculate the best possible url for a possible next view.
By default it is ``djp.url``'''
        return djp.request.path


class pageview(djpcmsview):
    
    def __init__(self, page):
        self.page    = page
        self.editurl = None  

    def __unicode__(self):
        return self.page.url
        
    def get_url(self, djp, **urlargs):
        return self.page.url
    
    def get_page(self, djp, **kwargs):
        return self.page
    
    def is_soft(self, djp):
        return self.page.soft_root


class wrapview(djpcmsview):
    '''
    Create a view object that wrap another view object  
    '''
    def __init__(self, view, prefix):
        '''
        @param view: instance of djpcmsview
        @param prefix: String defining the prefix to the view url
        
            let's say view.url = '/some/url/' and prefix = 'edit'
            than the wrpview instance will have a url given by
             '/edit/some/url/'
        '''
        self._view   = view
        self.prefix  = prefix
        self.editurl = None
        
    def __unicode__(self):
        return '%s: %s' % (self.prefix,self._view)
    
    def get_page(self, djp):
        return self._view.get_page(djp)
    
    def get_template(self, request, page):
        return self._view.get_template(request, page)
    
    def grid960(self, page):
        return self._view.grid960(page)

