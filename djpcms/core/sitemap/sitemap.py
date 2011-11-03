from time import time
from threading import Lock

from py2py3 import itervalues

from djpcms import UnicodeMixin
from djpcms.utils import parentpath, SLASH
from djpcms.views import DjpResponse, pageview
from djpcms.html import field_repr
from djpcms.core.orms import mapper
from djpcms.core.exceptions import ImproperlyConfigured, PathException

from .serialize import *

__all__ = ['Node',
           'SiteMap']
    
    
class DummyRequest(object):
    
    def __init__(self,site):
        self.site = site
        self.user = None
        

class NodeInfo(object):
    
    def __init__(self, node):
        self.node = node
        self.djp = node.djp()
    
    @property
    def url(self):
        return self.node.path
    
    @property
    def application(self):
        if self.node.view:
            return self.node.view.appmodel.name
        else:
            return ''
        

class Node(UnicodeMixin):
    '''The :class:`Sitemap` Node class.'''
    def __init__(self, urlmap, path = SLASH, view = None):
        self.urlmap = urlmap
        self.path = path
        self._site = None
        self.view = view
        
    @property
    def page(self):
        return self.urlmap.get_page(self.path)
    
    def children(self, strict = True):
        '''Return a generator of child nodes.

:parameter strict: If ``True`` only direct children will be included.
                   
                   Default ``True``.
'''
        path = self.path
        mp   = self.urlmap
        for p in mp:
            if p.startswith(path):
                if strict:
                    if parentpath(p) == path:
                        yield mp[p]
                else:
                    yield mp[p] 
        
    def children_map(self, strict = True):
        '''Utility method which returns a dictionary of children nodes,
where the key is given by the children path.

:parameter strict: If ``True`` only direct children will be included.
                   
                   Default ``True``.
'''
        return dict((c.path,c) for c in self.children(strict))
    
    @property
    def site(self):
        if self._site is None:
            if self.view:
                return self.view.site
            else:
                self._site = self.urlmap.get_site(self.path)
        return self._site
            
    @property
    def ancestor(self):
        if self.path == SLASH:
            return None
        else:
            p = parentpath(self.path)
            if p in self.urlmap:
                return self.urlmap[p]
        
    def __unicode__(self):
        return self.path
    
    def djp(self, request = None, **kwargs):
        '''Create a :class:`djpcms.views.DjpResponse` object with a dummy
 request if not available'''
        if not request:
            request = DummyRequest(self.site)   
        view = self.get_view()
        return DjpResponse(request, view, **kwargs)
    
    def get_view(self):
        '''Return an instance of `:class:`djpcms.views.djpcmsview` at node.'''
        if self.view:
            return self.view
        else:
            page = self.page 
            if page:
                site = self.site
                if site is not None:
                    return pageview(page,site)
        raise PathException('Cannot get view for node {0}'.format(self))
        
    def tojson(self, fields):
        '''Convert ``self`` into an instance of :class:`JsonTreeNode`
for json serialization.'''
        djp = self.djp()
        node = JsonTreeNode(None, self.path,
                values = [field_repr(field['name'], djp) for field in fields],
                children = [])
        for child in self.children():
            node.add(child.tojson(fields))
        return node

    
class SiteMap(dict):
    '''Djpcms sitemap'''
    def __init__(self, site):
        super(SiteMap,self).__init__()
        self.site = site
        self.root = r = Node(self)
        self[r.path] = r
        self.lastload = None
        self.lock = Lock()
        self._pages = {}
        
    def addsite(self, site):
        '''Add an :class:`djpcms.apps.appsites.ApplicationSite`
to the sitemap.'''
        node = self.node(site.path, site = site, force = True)
        self.addapplications(site.applications)
        return node
        
    def node(self, path, site = None, force = False):
        '''Retrive a :class:`Node` in the sitemap from a ``path`` input.
If the path is not available but its parent path is,
it returns a new node without storing it in the sitemap.
Otherwise it raises a :class:`djpcms.core.exceptions.PathException`.

:parameter path: node path.
:parameter force: if ``True`` and ``path`` is not in the sitemap,
                  a new :class:`Node` is created and added
                  regardless if its ancestor is available.'''
        if path not in self:
            if force:
                node = self[path] = Node(self, path = path)
            else:
                node = None
                if self.load():
                    if path in self:
                        node = self[path]
                if not node:
                    ppath = parentpath(path)
                    if ppath not in self:
                        raise PathException(path)
                    node = Node(self, path = path)
            node._site = site
            return node
        else:
            node = self[path]
            if force:
                node._site = site
            return node
    
    def addapplications(self, apps):
        '''Add a list of applications to the sitemap'''
        for app in apps:
            for view in itervalues(app.views):
                node = self.node(view.path,force=True)
                if node.view:
                    raise ImproperlyConfigured('Node {0} has already \
a view "{1}". Cannot assign a new one "{2}"'.format(node,node.view,view))
                node.view = view
    
    def get_sitemap(self, Page, refresh = False):
        if Page:
            pages = Page.objects.all()
        return self.root
    
    def get_site(self,path):
        r = self.site.resolver.resolve(path[1:])
        return r[0]
        
    def get_page(self,path):
        self.load()
        return self._pages.get(path,None)
        
    def load(self):
        '''Load flat pages to sitemap'''
        Page = mapper(self.site.Page) if self.site.Page else None
        if Page:
            nt = time()
            if not self.lastload or nt - self.lastload >\
                                     self.site.settings.SITEMAP_TIMEOUT:
                self.lastload = nt
            else:
                return False
            pages = {}
            for p in Page.all():
                path = p.url
                if path not in self:
                    self[path] = Node(self, path = path)
                pages[path] = p
            self._pages = pages
            return True
        else:
            return False
    
    def update_flat_pages(self):
        self.lock.acquire()
        try:
            for node in list(self.values()):
                if not node.view:
                    del self[node.path]
        finally:
            self.lock.release()
        self.lastload = None
        self.load()
    
