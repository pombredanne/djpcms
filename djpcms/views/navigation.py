'''Utility module for creating a navigations and breadcrumbs
'''
import djpcms
from djpcms.html import Widget
from djpcms.utils.const import *
from djpcms.utils import mark_safe
    

class LazyHtml(djpcms.UnicodeMixin):
    '''A lazy view counter used to build navigations type iterators
    '''
    def __new__(cls, request, **kwargs):
        obj = super(LazyHtml, cls).__new__(cls)
        obj.request = request
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
    
    def make_item(self, request, classes):
        return Navigator(request,
                         levels = self.levels,
                         mylevel = self.mylevel+1,
                         liclass = classes,
                         url  = request.url,
                         name = request.linkname,
                         soft = self.soft,
                         **self.kwargs)
    
    def buildselects(self, request, urlselects):
        if self.soft and request.is_soft():
            return request
        parent = request.parent
        if parent:
            try:
                url = request.url
                if url:
                    urlselects.append(url)
            except:
                pass
            return self.buildselects(parent, urlselects)
        return request
    
    def items(self, urlselects = None, secondary_after = 100, **kwargs):
        request = self.request
        css = request.view.settings.HTML
        
        if urlselects is None:
            urlselects = []
            request = self.buildselects(request,urlselects)
            self.kwargs['urlselects'] = urlselects
        scn = css.get('secondary_in_list')
        link_active = css.get('link_active')
        link_default = css.get('link_default')
        for request,nav in sorted(((c,c.in_navigation)\
                    for c in request.auth_children()), key = lambda x : x[1]):
            if not nav:
                continue
            url = request.url
            classes = []
            if nav > secondary_after:
                classes.append(scn)
            if url in urlselects and link_active:
                classes.append(link_active)
            elif link_default:
                classes.append(link_default)
            yield self.make_item(request, ' '.join(classes))
    
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
        request = self.request
        crumbs = []
        while request:
            c = {'name': request.view.breadcrumb(request),
                 'last': False}
            try:
                c['url'] = request.url
                c['title'] = request.title
            except:
                pass
            request = request.parent
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

