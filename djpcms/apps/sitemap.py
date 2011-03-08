from py2py3 import itervalues

from djpcms import UnicodeMixin
from djpcms.utils import parentpath, SLASH


class Node(UnicodeMixin):
    
    def __init__(self, urlmap, url = SLASH, view = None, parent = None):
        self.urlmap = urlmap
        self.url = url
        self.view = view
        self.children = {}
        self.parent = parent
        if parent:
            parent.children[url] = self
            
    def __unicode__(self):
        return self.url
    
    def child(self, url):
        urlmap = self.urlmap
        purl = parentpath(url)
        if purl is None:
            if self.view:
                raise ImproperlyConfigured('There seems to be a problem in sitemap.')
            self.view = app.root_application
        elif purl == self.url:
            urlmap[url] = node = Node(urlmap, url = url, parent = self)
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
                self.view = app.root_application
            elif purl == SLASH:
                url = burl + url
                urlmap[url] = Node(urlmap, url = url, view = app.root_application, parent = self)
            else:
                unprocessed.append(app)
        if unprocessed:
            for child in itervalues(self.children):
                unprocessed = child.addapplications(unprocessed)
                if not unprocessed:
                    return unprocessed
        return unprocessed
                
    
class SiteMap(object):
    
    def __init__(self):
        self._nodes = {}
        self.root = r = Node(self)
        self[r.url] = r
        
    def node(self, url):
        if url not in self._nodes:
            return self.root.child(url)
        else:
            return self._nodes[url]
        
    def __setitem__(self, url, node):
        self._nodes[url] = node
        
    def __getitem__(self, url):
        return self._nodes[url]