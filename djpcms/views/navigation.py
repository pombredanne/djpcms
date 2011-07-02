'''Utility module for creating a navigations and breadcrumbs
'''
from py2py3 import itervalues, to_string

from djpcms import sites, UnicodeMixin
from djpcms.utils.const import *
from djpcms.template import loader
from djpcms.utils import lazyattr
    

class LazyCounter(UnicodeMixin):
    '''A lazy view counter used to build navigations type iterators
    '''
    def __new__(cls, djp, **kwargs):
        obj = super(LazyCounter, cls).__new__(cls)
        obj.djp = djp
        obj.classes = kwargs.pop('classes',None)
        obj.kwargs = kwargs
        return obj

    def __len__(self):
        return len(self.items())
    
    def __unicode__(self):
        return self.render()
    

class Navigator(LazyCounter):
    '''A navigator for the web site
    '''
    def __init__(self, *args, **kwargs):
        self.soft    = self.kwargs.pop('soft',False)
        self.url     = self.kwargs.pop('url','')
        self.name    = self.kwargs.pop('name','')
        self.levels  = self.kwargs.pop('levels',2)
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
    
    @lazyattr
    def items(self, urlselects = None, secondary_after = 100, **kwargs):
        djp = self.djp
        css = djp.css
        if urlselects is None:
            urlselects = []
            djp = self.buildselects(djp,urlselects)
            self.kwargs['urlselects'] = urlselects
        scn = css.secondary_in_list                
        items = []
        for djp,nav in sorted(((c,c.in_navigation()) for c in djp.children()), key = lambda x : x[1]):
            if not nav or not djp.has_permission():
                continue
            url = djp.url
            classes = []
            if nav > secondary_after:
                classes.append(scn)
            if url in urlselects and css.link_active:
                classes.append(css.link_active)
            elif css.link_default:
                classes.append(css.link_default)
            items.append(self.make_item(djp, ' '.join(classes)))
        return items

    @lazyattr
    def render(self):
        if self.mylevel <= self.levels:
            return '\n'.join(self.lines())
        else:
            return ''
    
    def lines(self):
        items = self.items(**self.kwargs)
        if self.url:
            yield '<a href="{0}">{1}</a>'.format(self.url,self.name)
        if items:
            if self.classes:
                yield '<ul class="{0}">'.format(self.classes)
            else:
                yield UL
            for item in items:
                if item.liclass:
                    yield '<li class="{0}">'.format(item.liclass)
                else:
                    yield LI
                yield to_string(item)
                yield LIEND
            yield ULEND
            

class Breadcrumbs(LazyCounter):
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
        
    @lazyattr
    def items(self):
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
    
    @lazyattr
    def render(self):
        return loader.render(self.template,{'breadcrumbs':self.items()})

