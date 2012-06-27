import djpcms
from djpcms.html import Widget, NON_BREACKING_SPACE
from djpcms.views import application_link
    

__all__ = ['Navigator', 'Breadcrumbs']


class Navigator(object):
    '''Build a navigator for the web site.

:parameter levels: number of nesting in navigation.

    Default: ``2``
    
:parameter nav_element: the navigation element. It must be an instance of
    a class:`djpcms.html.Widget` or ``None``. This is the outer element of the
    navigation. If not provided a topbar element is created.
    
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
    main_layout = ('brand','nav')
    secondary_layout = ('search','nav')
    
    def __init__(self, levels=4, secondary_after=100,
                 nav_element=None, primary=None, secondary=None,
                 container=None, fixed=False,
                 brand=None, search=None, soft=False,
                 main_layout=None, secondary_layout=None):
        self.main_layout = main_layout if main_layout\
                            is not None else self.main_layout
        self.secondary_layout = secondary_layout if secondary_layout\
                                 is not None else self.secondary_layout
        if brand and not isinstance(brand, Widget):
            brand = Widget('a',brand,cn='brand',href='/')
        self.brand = brand
        self.search = search
        self.soft = soft
        self.nav_element = nav_element
        self.container = container
        if container is not None and not isinstance(container, Widget):
            self.container = Widget('div', cn = self.container)
        self.fixed = fixed
        self.levels = max(levels,1)
        self.secondary_after = secondary_after
        self.primary = primary if primary is not None else Widget('ul')
        self.secondary = secondary if secondary is not None else Widget('ul')
        self.primary.addClass('nav')
        self.secondary.addClass('nav secondary-nav')
    
    def elements(self, layout, nav):
        float = 'right' if nav.hasClass('secondary-nav') else 'left'
        for elem in layout:
            if elem == 'nav':
                elem = nav
            else:
                elem = getattr(self,elem,None)
                if elem is not None:
                    elem.css({'float':float})
            if elem is not None:
                yield elem
                
    def render(self, request):
        if self.nav_element is None:
            self.nav_element = Widget('div', cn = 'topbar')
        if self.fixed:
            widget = Widget('div', self.nav_element, cn = 'topbar-fixed')
        else:
            widget = self.nav_element
            
        if self.container is not None:
            self.nav_element.add(self.container.root)
            nav_element = self.container
        else:
            nav_element = self.nav_element
            
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
        for elem in self.elements(self.main_layout, self.primary):
            nav_element.add(elem)
        for elem in self.elements(reversed(self.secondary_layout),\
                                                         self.secondary):
            nav_element.add(elem)
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
    for request, nav in sorted(((c,c.in_navigation)\
                for c in request.auth_children()), key = lambda x : x[1]):
        if not nav:
            continue
        link = application_link(request, asbutton=False)
        li = Widget('li',link)
        secondary = secondary_after and nav > secondary_after
        if link.attrs['href'] in urlselects:
            li.addClass(link_active)
        if level:
            slis = list(navstream(request, urlselects, None, link_active,
                                  level-1))
            if slis:
                ul = Widget('ul')
                for sli,_ in slis:
                    ul.add(sli)
                li.add(ul)
        yield li, secondary
            

class Breadcrumbs(object):
    '''A lazy class for building a site breadcrumb trail to keep track
of current request location. It renders as a ``ul`` element
with class name defaulted to ``"breadcrumbs"``.
    '''
    def __init__(self, min_length=1, divider=None, cn=None,
                 render_empty=True, tag='div'):
        divider = divider or '&rsaquo;'
        self.divider = "<span class='divider'>"+divider+"</span>"
        self.min_length = min_length
        self.render_empty = render_empty 
        self.widget = Widget(tag, cn=cn or 'breadcrumbs')
        
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
            self.widget.add(ul)
            return self.widget.render(request)
        elif self.render_empty:
            return Widget('div',NON_BREACKING_SPACE).render(request)
        else:
            return ''

