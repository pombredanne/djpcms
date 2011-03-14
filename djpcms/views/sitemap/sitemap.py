from py2py3 import itervalues

from djpcms import UnicodeMixin
from djpcms.utils import parentpath, SLASH
from djpcms.utils.text import nicename
from djpcms.views import DjpResponse, pageview
from djpcms.core.orms import mapper
from djpcms.core.exceptions import ImproperlyConfigured, PathException

from .serialize import *

__all__ = ['Node',
           'SiteMap']
    
    
class DummyRequest(object):
    
    def __init__(self,site):
        self.site = site
        

class NodeInfo(object):
    
    def __init__(self, node):
        self.node = node
        self.djp = node.djp()
    
    @property
    def url(self):
        return self.node.path
    
    @property
    def template(self):
        return self.djp.template_file
    
    @property
    def application(self):
        if self.node.view:
            return self.node.view.appmodel.name
        else:
            return ''
        

class Node(UnicodeMixin):
    '''a :class:`Sitemap` Node'''
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
        
    def children_map(self, strict = True):
        '''Utility method which returns a dictionary of children, where
        the key is given by the children path.
        '''
        return dict((c.path,c) for c in self.children(strict))
    
    @property
    def site(self):
        return self._site if self._site is not None else self.ancestor.site
            
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
        view = self.get_view()
        return DjpResponse(request, view)
    
    def get_view(self):
        '''Return an instance of `:class:`djpcms.views.djpcmsview` at node.'''
        if self.view:
            return self.view
        elif self.page:
            return pageview(self.page,self.site)
        else:
            raise PathException('Cannot get view for node {0}'.format(self))
        
    def tojson(self, fields):
        '''Convert ``self`` into an instance of :class:`JsonTreeNode`
for json serialization.'''
        values = []
        info = NodeInfo(self)
        for field in fields:
            attr = getattr(info,field,None)
            if hasattr(attr,'__call__'):
                attr = attr()
            values.append(attr if attr is not None else '')
        node = JsonTreeNode(None, self.path,
                            values = values,
                            children = [])
        for child in self.children():
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
    
    def get_sitemap(self, Page, refresh = False):
        if Page:
            pages = Page.objects.all()
        return self.root
    
    def tojson(self, fields, refresh = True):
        '''Serialize as a JSON string.'''
        nice_fields = [{'name':name,'description':nicename(name)} for name in fields]
        data = JsonData(fields = nice_fields)
        root = self.root.tojson(fields)
        data.add(root)
        return data
    
    def get_page(self,path):
        from djpcms.models import Page
        if Page:
            mp = mapper(Page)
            try:
                return mp.get(url = path)
            except mp.DoesNotExist:
                return None
        
        
        