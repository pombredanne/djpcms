from copy import copy

from djpcms import UnicodeMixin
from djpcms.utils import lazyproperty, lazymethod

from py2py3 import itervalues


class Node(UnicodeMixin):
    '''A not in a non-recombining tree'''
    def __init__(self, view):
        self.__view = view
        self.__level = view.route.level
        self.__parent = None
        self.__children = []
    
    def __unicode__(self):
        return self.path
    
    @property
    def view(self):
        return self.__view
    
    @property
    def route(self):
        return self.__view.route
    
    @property
    def level(self):
        return self.__level
    
    def __get_parent(self):
        return self.__parent
    def __set_parent(self, p):
        if self.__parent:
            raise ValueError('cannot set parent. It is already set.')
        if p is not None:
            self.__parent = p
            p.append(self)
    parent = property(__get_parent,__set_parent)
    
    @property
    def children(self):
        return self.__children
    
    @property
    def root(self):
        r = self
        while r.parent is not None:
            r = r.parent
        return r
    
    @property
    def path(self):
        return self.view.path
        
    def append(self, node):
        if node.parent is not self:
            raise ValueError('Appending node with wrong parent')
        self.__children.append(node)


class NRT(dict):
    '''Non Recombining Tree implementation. A non recombining tree is a tree
 where no nodes combine. It exclude all trees that have at least one combined
 class:`Node'.'''
    def __init__(self, views, site = None):
        self.site = site
        m = {}
        for view in views:
            route = view.route
            path = route.path
            if path in m:
                raise ValueError('There seems to be multiple values for\
 "{0}" path'.format(path))
            node = Node(view)
            m[node.path] = node
        if not m:
            raise ValueError('No views')
        # order by level
        nodes = sorted(itervalues(m), key = lambda x : x.level)
        start = nodes.pop(0)
        parent_level = start.level
        self.roots = roots = [start]
        for node in nodes:
            if node.level == parent_level:
                roots.append(node)
            else:
                if node.level > parent_level+1:
                    # we go up a level
                    parent_level += 1
                route = node.route
                while route.level > parent_level:
                    route,bit = route.split()
                    if route.path in m:
                        node.parent = m[route.path]
                        break
        super(NRT,self).__init__(m)
        
    @property
    def level(self):
        return self.roots[0].level
    
    def nodes(self):
        return itervalues(self)
        

class MultiNode(UnicodeMixin):
    
    def __init__(self, tree, route, parent = None, urlargs = None):
        self.tree = tree
        self.__route = route
        self.__urlargs = {} if urlargs is None else copy(urlargs)
        self.__parent = parent
        
    def __unicode__(self):
        return self.__route.path
    
    @property
    def route(self):
        return self.__route
    
    @property
    def path(self):
        return self.__route.path
    
    @property
    def urlargs(self):
        return self.__urlargs
    
    @lazyproperty
    def parent(self):
        tree = self.tree
        p = self.__parent
        if p is None:
            route = self.route
            while route.level > tree.level:
                route,_ = route.split()
                p = tree.get(route.path, self.__urlargs)
                if p is not None:
                    return p
        else:
            return self.tree.node(p,self.__urlargs)
        
    def children(self):
        '''tuple containing children nodes'''
        return tuple(self.tree.children(self.path, self.__urlargs))
    
    def url(self):
        try:
            return self.route.url(**self.__urlargs)
        except KeyError:
            return None
    
    
class MultiTree(object):
    '''handle multiple non-recombining tree'''
    def __init__(self, *trees):
        self.trees = trees
        self.site = None
        level = None
        for tree in trees:
            level = min(level,tree.level) if level is not None else tree.level
            if tree.site:
                if self.site:
                    raise ValueError('Critical. Multiple sites')
                self.site = tree.site
        if not self.site:
            raise ValueError('Critical. No sites')
        self.__level = level
        
    @property
    def level(self):
        return self.__level
        
    def node(self, node, urlargs = None):
        raise NotImplementedError
    
    def __containes__(self, path):
        for tree in self.trees:
            if path in tree:
                return True
        return False
    
    def get(self, path, urlargs = None):
        for tree in self.trees:
            if path in tree:
                return self.node(tree[path],urlargs)
            
    def children(self, path, urlargs = None):
        '''Generator of all direct :class:`MultiNode` children for *path*.'''
        node = self.node
        for child in self.__children(path):
            yield node(child, urlargs)
            
    def resolve(self, path):
        '''Resolve the *path* on the multi tree. This is the main function
 of this class. It return an instance of :class:`MultiNode` if the *path*
 matches a node. Otherwise it raises a :class:`djpcms.Http404` exception.'''
        return self.node(*self.__resolve(path))
        
    def __resolve(self, path):
        # first loop check for static urls (with no arguments)
        for tree in self.trees:
             node = tree.get(path)
             if node:
                 # we got a node. If this node has variables raise Http404
                 if node.route.arguments:
                     # raise 404 without any further checking
                     raise Http404(strict = True)
                 return node,{}
        # second loop resolve urls
        for tree in self.trees:
            if tree.site is None:
                continue
            view,args = tree.site.resolve(path[1:])
            return tree[view.path],args
    
    def __children(self, path):
        bits = tuple((b for b in path.split('/') if b))
        level = len(bits)
        for tree in self.trees:
            if path in tree:
                for child in tree[path].children:
                    yield child
            else:
                for child in tree.nodes():
                    if child.level > level and not child.parent:
                        if child.route.bits[:level] == bits:
                            yield child
        

class DjpNode(MultiNode):
    '''Node used by djpcms to handle responses.'''
    def __init__(self, tree, view, page, **kwargs):
        self.page = page
        self.__view = view
        route = view.route if view is not None else page.route
        super(DjpNode,self).__init__(tree,route,**kwargs)
    
    @property
    def view(self):
        view = self.__view
        if view is None:
            from djpcms.views import pageview
            parent = self.parent
            if parent is None:
                handler = self.tree.site
            else:
                view = parent.view
                handler = view.appmodel or view.site
            self.__view = view = pageview(self.page, handler)
        return view
    
    
class DjpcmsTree(MultiTree):
 
    def __init__(self, tree, pages = None):
        self.tree_pages = p = {}
        if pages:
            ptrees = {}
            for page in pages:
                node = tree.get(page.url)
                if node:
                    p[node.path] = page
                else:
                    ptrees[page.url] = page
            ptree = NRT(itervalues(ptrees))
            super(DjpcmsTree,self).__init__(ptree,tree)
        else:
            super(DjpcmsTree,self).__init__(tree)
    
    def node(self, node, urlargs = None):
        view = node.view
        if getattr(view,'root',None) == self.site:
            page = self.tree_pages.get(view.path)
        else:
            page = view
            view = None
        
        return DjpNode(self, view, page, urlargs = urlargs,
                       parent = node.parent)
        