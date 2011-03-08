'''Utility module for creating a navigation list
'''
from py2py3 import itervalues

from djpcms import sites, UnicodeMixin
from djpcms.template import loader
from djpcms.utils import lazyattr, SLASH


def children_responses(djp):
    request = djp.request
    page = djp.page
    view = djp.view
    url = djp.url
    root = sites.tree.node(url)
    for node in itervalues(root.children):
        cview = node.view
        if cview:
            cdjp = cview(request,**djp.kwargs)
            try:
                cdjp.url
            except:
                continue
            if hasattr(cdjp,'in_navigation'):
                nav = cdjp.in_navigation()
                if nav:
                    yield cdjp,nav


class lazycounter(UnicodeMixin):
    '''A lazy view counter used to build navigations type iterators
    '''
    def __new__(cls, djp, **kwargs):
        obj = super(lazycounter, cls).__new__(cls)
        obj.djp = djp.underlying()
        obj.classes = kwargs.pop('classes',None)
        obj.kwargs = kwargs
        return obj

    def __unicode__(self):
        return self.render()
    
    def __len__(self):
        return len(self.elems())
    
    def count(self):
        return len(self)
    
    def __iter__(self):
        return self.items()

    @lazyattr
    def elems(self):
        return self._items(**self.kwargs)
    
    def items(self):
        elems = self.elems()
        for elem in elems:
            yield elem
            
    def render(self):
        '''Render the navigation list
        '''
        raise NotImplementedError
    
    def _items(self, **kwargs):
        '''It should return an iterable object (but not a generator)
        '''
        raise NotImplementedError
    


class Navigator(lazycounter):
    '''A navigator for the web site
    '''
    def __init__(self, *args, **kwargs):
        self.soft    = self.kwargs.pop('soft',False)
        self.url     = self.kwargs.pop('url','')
        self.name    = self.kwargs.pop('name','')
        self.levels  = self.kwargs.pop('levels',1)
        self.mylevel = self.kwargs.pop('mylevel',0)
        self.liclass = self.kwargs.pop('liclass',None)
        
    def make_item(self, djp, classes):
        return Navigator(djp,
                         levels = self.levels,
                         mylevel = self.mylevel+1,
                         liclass = classes,
                         url  = djp.url,
                         name = djp.linkname,
                         soft = self.soft,
                         **self.kwargs)
    
    def buildselects(self, djp, urlselects):
        if self.soft and djp.is_soft():
            return djp
        #TO BE REMOVED AND REPLACED WITH SITEMAP
        parent = djp.parent
        if parent:
            try:
                url = djp.url
                if url:
                    urlselects.append(url)
            except:
                pass
            return self.buildselects(parent, urlselects)
        return djp
        
    def _items(self, urlselects = None, secondary_after = 100, **kwargs):
        djp = self.djp
        css = djp.css
        if urlselects is None:
            urlselects = []
            djp = self.buildselects(djp,urlselects)
            self.kwargs['urlselects'] = urlselects
        scn = css.secondary_in_list                
        items = []
        for djp,nav in sorted(children_responses(djp), key = lambda x : x[1]):
            url = djp.url
            classes = []
            if nav > secondary_after:
                classes.append(scn)
            if url in urlselects:
                classes.append(css.link_selected)
            items.append(self.make_item(djp, ' '.join(classes)))
        return items

    def render(self):
        if self.mylevel <= self.levels:
            return loader.render('djpcms/bits/navitem.html', {'navigator': self})
        else:
            return ''         


class Breadcrumbs(lazycounter):
    '''
    Breadcrumbs for current page
    '''
    template = ("breadcrumbs.html",
                "djpcms/components/breadcrumbs.html")
    
    def __init__(self, *args, **kwargs):
        self.min_length = self.kwargs.pop('min_length',1)
    
    def make_item(self, djp, classes, first):
        c = {'name':    djp.title,
             'classes': ' '.join(classes)}
        if not first:
            try:
                c['url'] = djp.url
            except:
                pass
        return c
        
    def _items(self, **kwargs):
        first   = True
        classes = []
        djp     = self.djp
        crumbs  = []
        while djp:
            val     = self.make_item(djp,classes,first)
            first = False
            djp   = djp.parent
            crumbs.append(val)
        
        cutoff = self.min_length
        if len(crumbs) >= cutoff:
            cutoff -= 1
            if cutoff:
                crumbs = crumbs[:-cutoff]
            return list(reversed(crumbs))
        else:
            return []
    
    def render(self):
        return loader.render(self.template,{'breadcrumbs':self})