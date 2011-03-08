from py2py3 import itervalues

from djpcms import UnicodeMixin
from djpcms.utils import parentpath, SLASH
from djpcms.views import DjpResponse, pageview
from djpcms.core.exceptions import ImproperlyConfigured

from .serialize import *

__all__ = ['Node',
           'SiteMap']
    
class DummyRequest(object):
    
    def __init__(self,site):
        self.site = site
        

class Node(UnicodeMixin):
    '''Sitemap Node'''
    def __init__(self, urlmap, url = SLASH, view = None, ancestor = None):
        self.urlmap = urlmap
        self.url = url
        self.site = None
        self.view = view
        self.page = None
        self.children = {}
        self.ancestor = ancestor
        if ancestor:
            self.site = ancestor.site 
            ancestor.children[url] = self
            
    def __unicode__(self):
        return self.url
    
    def djp(self, request = None):
        '''Create a :class:`djpcms.views.DjpResponse` object with a dummy request if not available'''
        if not request:
            request = DummyRequest(self.site)
        view = self.view or pageview(self.page)
        return DjpResponse(request, view)
    
    def child(self, url):
        urlmap = self.urlmap
        purl = parentpath(url)
        if purl is None:
            if self.view:
                raise ImproperlyConfigured('There seems to be a problem in sitemap.')
            self.view = app.root_view
        elif purl == self.url:
            urlmap[url] = node = Node(urlmap, url = url, ancestor = self)
            return node
        else:
            for child in itervalues(self.children):
                node = child.child(url)
                if node:
                    return node
    
    def addapplications(self, apps):
        burl = self.url[:-1]
        urlmap = self.urlmap
        unprocessed = []
        for app in apps:
            url = app.baseurl
            purl = parentpath(url)
            if purl is None:
                if self.view:
                    raise ImproperlyConfigured('There seems to be a problem in sitemap.')
                self.view = app.root_view
            elif purl == SLASH:
                url = burl + url
                urlmap[url] = Node(urlmap, url = url, view = app.root_view, ancestor = self)
            else:
                unprocessed.append(app)
        if unprocessed:
            for child in itervalues(self.children):
                unprocessed = child.addapplications(unprocessed)
                if not unprocessed:
                    return unprocessed
        return unprocessed
    
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

    
class SiteMap(object):
    
    def __init__(self):
        self._nodes = {}
        self.root = r = Node(self)
        self[r.url] = r
        
    def make_sitenode(self, url, site):
        node = self.node(url)
        node.site = site
        return node
        
    def node(self, url):
        if url not in self._nodes:
            return self.root.child(url)
        else:
            return self._nodes[url]
        
    def __len__(self):
        return len(self._nodes)
    
    def __setitem__(self, url, node):
        self._nodes[url] = node
        
    def __getitem__(self, url):
        return self._nodes[url]
    
    def get_sitemap(self, Page, refresh = False):
        if Page:
            pages = Page.objects.all()
        return self.root
    
    def tojson(self, fields, refresh = True):
        data = JsonData(fields = fields)
        root = self.root.tojson(fields)
        data.add(root)
        return data
        
        