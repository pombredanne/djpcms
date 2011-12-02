'''Utility module for creating a navigations and breadcrumbs
'''
import djpcms
from djpcms.html import Widget, ListWidget
from djpcms.utils import mark_safe
    

__all__ = ['Navigator','Breadcrumbs']


class Navigator(object):
    
    def __init__(self, soft = False, levels = 2, secondary_after = 100,
                 primary = None, secondary = None):
        self.soft = soft
        self.levels = max(levels,1)
        self.secondary_after = secondary_after
        self.primary = primary if primary is not None else Widget('ul')
        self.secondary = secondary if secondary is not None else Widget('ul')
        self.primary.addClass('nav')
        self.secondary.addClass('nav secondary-nav')
    
    def render(self, request):
        w = Widget('div', cn = 'topbar container')
        urlselects = []
        request = self.buildselects(request,urlselects)
        for li,secondary in navstream(request,
                                      urlselects,
                                      self.secondary_after,
                                      self.levels-1):
            if secondary:
                self.secondary.add(li)
            else:
                self.primary.add(li)
        if self.primary:
            w.add(self.primary)
        if self.secondary:
            w.add(self.secondary)
        return w.render(request)
    
    def buildselects(self, request, urlselects):
        if self.soft and request.view.is_soft(request):
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
    
    
def navstream(request, urlselects, secondary_after, level):
    css = request.view.settings.HTML
    scn = css.get('secondary_in_list')
    link_active = css.get('link_active')
    link_default = css.get('link_default')
    for request,nav in sorted(((c,c.in_navigation)\
                for c in request.auth_children()), key = lambda x : x[1]):
        if not nav:
            continue
        url = request.url
        link = Widget('a',request.linkname,href=url)
        li = Widget('li',link)
        secondary = secondary_after and nav > secondary_after
        if url in urlselects and link_active:
            li.addClass(link_active)
        elif link_default:
            li.addClass(link_default)
        if level:
            slis = list(navstream(request, urlselects, None, level-1))
            if slis:
                ul = Widget('ul')
                for sli,_ in slis:
                    ul.add(sli)
                li.add(ul)
        yield li,secondary
            

class Breadcrumbs(ListWidget):
    '''Given a url it build a list of previous url elements.
Each element is a dictionary contaning ``name`` and ``url``. The last element in the list, the
the current url, won't contain the ``url`` value in the dictionary so that an internal link to
the same page is not created in the HTML document.

The ``name`` value is calculated in the view method :ref:`topics-views-title`.

Breadcrumbs are available in the context dictionary with key ``breadcrumbs``.

See :ref:`topics-views-context-dictionary`
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

