'''Utility module for creating a navigations and breadcrumbs
'''
import djpcms
from djpcms.html import Widget, ListWidget
from djpcms.utils import mark_safe
    

__all__ = ['Navigator','Breadcrumbs']


class Navigator(object):
    '''Build a navigator for the web site.

:parameter levels: number of nesting in navigation.

    Default: ``2``
    
:parameter container: The container class for the inner part of the navigation.
    If available a ``div`` element with this class is created inside the
    navigation element.

    Default: ``None``.
    
:paremeter soft: If ``True`` this is a soft navigation, meaning it is a
    navigation relative to the closest view which has
    :meth:`djpcms.views.djpcmsview.is_soft` returning ``True``.
    
    Default: ``False``.
'''
    link_active_class = 'active'
    
    def __init__(self, levels = 2, secondary_after = 100,
                 primary = None, secondary = None,
                 container = None, fixed = False, soft = False):
        self.soft = soft
        self.container = container
        if container is not None and not isinstance(container,Widget):
            self.container = Widget('div', cn = self.container)
        self.fixed = fixed
        self.levels = max(levels,1)
        self.secondary_after = secondary_after
        self.primary = primary if primary is not None else Widget('ul')
        self.secondary = secondary if secondary is not None else Widget('ul')
        self.primary.addClass('nav')
        self.secondary.addClass('nav secondary-nav')
    
    def render(self, request):
        topbar = Widget('div', cn = 'topbar')
        if self.fixed:
            widget = Widget('div', topbar, cn = 'topbar-fixed')
        else:
            widget = topbar
        if self.container is not None:
            topbar.add(self.container.root)
            topbar = self.container
        urlselects = []
        request = self.buildselects(request,urlselects)
        for li,secondary in navstream(request,
                                      urlselects,
                                      self.secondary_after,
                                      self.link_active_class,
                                      self.levels-1):
            if secondary:
                self.secondary.add(li)
            else:
                self.primary.add(li)
        if self.primary:
            topbar.add(self.primary)
        if self.secondary:
            topbar.add(self.secondary)
        return widget.render(request)
    
    def buildselects(self, request, urlselects):
        if self.soft and request.view.is_soft(request):
            return request
        parent = request.parent
        if parent is not None:
            try:
                url = request.url
                if url:
                    urlselects.append(url)
            except:
                pass
            return self.buildselects(parent, urlselects)
        return request
    
    
def navstream(request, urlselects, secondary_after, link_active, level):
    for request,nav in sorted(((c,c.in_navigation)\
                for c in request.auth_children()), key = lambda x : x[1]):
        if not nav:
            continue
        url = request.url
        link = Widget('a',request.linkname,href=url)
        li = Widget('li',link)
        secondary = secondary_after and nav > secondary_after
        if url in urlselects:
            li.addClass(link_active)
        if level:
            slis = list(navstream(request, urlselects, None, link_active,
                                  level-1))
            if slis:
                ul = Widget('ul')
                for sli,_ in slis:
                    ul.add(sli)
                li.add(ul)
        yield li,secondary
            

class Breadcrumbs(object):
    '''Given a url it build a ``ul`` list of previous url elements.
    '''    
    def __init__(self, min_length = 1, divider = None):
        divider = divider or '&rsaquo;'
        self.divider = "<span class='divider'>"+divider+"</span>"
        self.min_length = min_length
        
    def items(self, request):
        crumbs = []
        while request:
            crumbs.append(request)
            request = request.parent
        
        cutoff = self.min_length-1
        if cutoff:
            crumbs = crumbs[:-cutoff]
        
        position = len(crumbs)
        for request in crumbs:
            li = Widget('li', cn = 'position{0}'.format(position))
            name = request.view.breadcrumb(request)
            if position < len(crumbs):
                url = request.url
                title = request.title
                a = Widget('a',name,title=title,href=url)
                li.add(a)
                li.add(self.divider)
            else:
                li.add(name)
            position -= 1
            yield li
        
    def render(self, request):
        ul = Widget('ul')
        for li in reversed(tuple(self.items(request))):
            ul.add(li)
        if ul:
            return Widget('div', ul, cn = 'breadcrumbs').render(request)
        else:
            return ''

