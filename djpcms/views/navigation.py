'''Utility module for creating a navigations and breadcrumbs
'''
import djpcms
from djpcms.html import Widget
from djpcms.utils.const import *
from djpcms.utils import mark_safe
    

class LazyHtml(djpcms.UnicodeMixin):
    '''A lazy view counter used to build navigations type iterators
    '''
    def __new__(cls, djp, **kwargs):
        obj = super(LazyHtml, cls).__new__(cls)
        obj.djp = djp
        obj.classes = kwargs.pop('classes',None)
        obj.kwargs = kwargs
        return obj
    
    def __unicode__(self):
        if not hasattr(self,'_html'):
            self._html = mark_safe(self.render())
        return self._html
    
    def render(self):
        raise NotImplemented
    

class Navigator(LazyHtml):
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
    
    def items(self, urlselects = None, secondary_after = 100, **kwargs):
        djp = self.djp
        css = djp.settings.HTML
        if urlselects is None:
            urlselects = []
            djp = self.buildselects(djp,urlselects)
            self.kwargs['urlselects'] = urlselects
        scn = css.secondary_in_list
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
            yield self.make_item(djp, ' '.join(classes))
    
    def stream(self):
        lis = '\n'.join((Widget('li').addClass(item.liclass)\
                                     .render(inner = item) for\
                                      item in self.items(**self.kwargs)))
        if self.url:
            yield '<a href="{0}">{1}</a>'.format(self.url,self.name)
        if lis:
            if self.classes:
                yield '<ul class="{0}">'.format(self.classes)
            else:
                yield UL
            yield lis
            yield ULEND
            
    def render(self):
        if self.mylevel <= self.levels:
            return '\n'.join(self.stream())
        else:
            return ''
            

class Breadcrumbs(LazyHtml):
    '''
    Breadcrumbs for current page
    '''
    _separator = '<li><span class="breadcrumbs-separator">&rsaquo;</span></li>'
    _inner = "<li class='position{0[position]}'><a href='{0[url]}'\
 title='{0[title]}'>{0[name]}</a></li>"
    _outer = "<li class='position{0[position]}'>{0[name]}</li>"
    _container = '<div class="breadcrumbs">{0}</div>'
    
    def __init__(self, *args, **kwargs):
        self.min_length = self.kwargs.pop('min_length',1)
        
    def items(self):
        djp = self.djp
        crumbs = []
        while djp:
            c = {'name': djp.breadcrumb,
                 'last': False}
            try:
                c['url'] = djp.url
                c['title'] = djp.title
            except:
                pass
            djp = djp.parent
            crumbs.append(c)
        
        cutoff = self.min_length
        if len(crumbs) >= cutoff:
            cutoff -= 1
            if cutoff:
                crumbs = crumbs[:-cutoff]
            crumbs[0]['last'] = True
            for p,c in enumerate(reversed(crumbs)):
                c['position'] = p+1
                yield c
        else:
            raise StopIteration
        
    def stream(self):
        sep = self._separator
        inn = self._inner
        for item in self.items():
            if item['last']:
                yield self._outer.format(item)
            else:
                if 'url' in item: 
                    yield self._inner.format(item)
                else:
                    yield self._outer.format(item)
                yield self._separator
                
    def render(self):
        lis = '\n'.join(self.stream())
        if lis:
            r = self._container.format('<ul>{0}</ul>'.format(lis))
        else:
            r = self._container.format('')
        return r

