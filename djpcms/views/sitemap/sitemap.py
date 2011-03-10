from py2py3 import itervalues

from djpcms import UnicodeMixin
from djpcms.utils import parentpath, SLASH
from djpcms.views import DjpResponse, pageview
from djpcms.core.exceptions import ImproperlyConfigured, PathException

from .serialize import *

__all__ = ['Node',
           'SiteMap']
    
    
class DummyRequest(object):
    
    def __init__(self,site):
        self.site = site
        

class Node(UnicodeMixin):
    '''a :class:`Sitemap` Node'''
    def __init__(self, urlmap, path = SLASH, view = None):
        self.urlmap = urlmap
        self.path = path
        self._site = None
        self.view = view
        self.page = None
        
    def children(self, strict = True):
        '''Return a generator of child nodes.

:parameter strict: If ``True`` only direct children will be included. Default ``True``.'''
        path = self.path
        mp   = self.urlmap
        for p in mp:
            if p.startswith(path):
                if strict:
                    if parentpath(p) == path:
                        yield mp[p]
                else:
                    yield mp[p] 
        
    @property
    def site(self):
        return self._site if self._site else self.ancestor.site
            
    @property
    def ancestor(self):
        if self.path == SLASH:
            return None
        else:
            return self.urlmap[parentpath(self.path)]
        
    def __unicode__(self):
        return self.path
    
    def djp(self, request = None):
        '''Create a :class:`djpcms.views.DjpResponse` object with a dummy request if not available'''
        if not request:
            request = DummyRequest(self.site)
        view = self.view or pageview(self.page)
        return DjpResponse(request, view)
    
    def tojson(self, fields):
        '''Convert ``self`` into an instance of :class:`JsonTreeNode`
for json serialization.'''
        values = []
        djp = self.djp()
        for field in fields:
            attr = getattr(djp,field,None)
            if hasattr(attr,'__call__'):
                attr = attr()
            values.append(attr if attr is not None else '')
        node = JsonTreeNode(None, self.url,
                            values = values,
                            children = [])
        for child in itervalues(self.children):
            node.add(child.tojson(fields))
        return node

    
class SiteMap(dict):
    '''Djpcms sitemap'''
    def __init__(self):
        super(SiteMap,self).__init__()
        self.root = r = Node(self)
        self[r.path] = r
        
    def addsite(self, site):
        '''Add an :class:`djpcms.apps.appsites.ApplicationSite`
to the sitemap.'''
        node = self.node(site.route, force = True)
        node._site = site
        self.addapplications(site.applications)
        return node
        
    def node(self, path, force = False):
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
                return node
            else:
                ppath = parentpath(path)
                if ppath not in self:
                    raise PathException(path)
                return Node(self, path = path)
        else:
            return self[path]
    
    def addapplications(self, apps):
        for app in apps:
            for view in itervalues(app.views):
                node = self.node(view.path(),force=True)
                if node.view:
                    raise ImproperlyConfigured('Node {0} has already \
a view "{1}". Cannot assign a new one "{2}"'.format(node,node.view,view))
                node.view = view
                
            # And the application sub-applications
            if app.apps:
                self.addapplications(itervalues(app.apps))
    
    def get_sitemap(self, Page, refresh = False):
        if Page:
            pages = Page.objects.all()
        return self.root
    
    def tojson(self, fields, refresh = True):
        '''Serialize as a JSON string.'''
        data = JsonData(fields = fields)
        root = self.root.tojson(fields)
        data.add(root)
        return data
        
        