import djpcms
from djpcms.html import Widget, WidgetMaker, Anchor, List, NON_BREACKING_SPACE
from djpcms.views import application_link

from . import classes
    

__all__ = ['Navigator', 'Breadcrumbs']


class Navigator(WidgetMaker):
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
    tag = 'div'
    main_layout = ('brand', 'nav')
    secondary_layout = ('search', 'nav')
    
    def __init__(self, levels=4, secondary_after=100,
                 nav_element=None, primary=None, secondary=None,
                 container=None, brand=None, search=None, soft=False,
                 main_layout=None, secondary_layout=None, **kwargs):
        super(Navigator, self).__init__(**kwargs)
        self.main_layout = main_layout if main_layout\
                            is not None else self.main_layout
        self.secondary_layout = secondary_layout if secondary_layout\
                                 is not None else self.secondary_layout
        if brand and not isinstance(brand, Widget):
            brand = Anchor(cn='brand', href='/').add(brand)
        self.brand = brand
        self.search = search
        self.soft = soft
        self.nav_element = nav_element
        self.levels = max(levels,1)
        self.secondary_after = secondary_after
        nav = List(key='primary', cn='nav')
        self.add(*self.elements(self.main_layout, nav))
        nav = List(key='secondary', cn=('nav secondary-nav'))
        self.add(*reversed(self.elements(self.secondary_layout, nav)))
    
    def elements(self, layout, nav):
        float = 'right' if nav.hasClass('secondary-nav') else 'left'
        elems = []
        for elem in layout:
            if elem == 'nav':
                elem = nav
            else:
                elem = getattr(self, elem, None)
                if elem is not None:
                    elem.css({'float':float})
            if elem is not None:
                elems.append(nav)
        return elems
                
    def get_context(self, request, widget, context):
        if request.valid:
            primary = widget.children['primary']
            secondary = widget.children['secondary']
            urlselects = []
            request = self.buildselects(request, urlselects)
            for li ,s in navstream(request, urlselects, self.secondary_after,
                                   self.levels-1):
                if s:
                    secondary.add(li)
                else:
                    primary.add(li)
        return context
    
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
    
    
def navstream(request, urlselects, secondary_after, level):
    for request, nav in sorted(((c, c.in_navigation)\
                for c in request.auth_children()), key = lambda x : x[1]):
        if not nav:
            continue
        link = application_link(request, asbutton=False)
        li = Widget('li',link)
        secondary = secondary_after and nav > secondary_after
        if link.attrs['href'] in urlselects:
            li.addClass(classes.state_active)
        if level:
            slis = list(navstream(request, urlselects, None, level-1))
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
    def __init__(self, min_length=2, divider=None, cn=None,
                 render_empty=True, tag='div'):
        divider = divider or '&rsaquo;'
        self.divider = "<span class='divider'>"+divider+"</span>"
        self.min_length = min_length
        self.render_empty = render_empty 
        self.widget = Widget(tag, cn=cn or classes.breadcrumbs)
        
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
        if request.valid:
            ul = Widget('ul')
            for li in reversed(tuple(self.items(request))):
                ul.add(li)
            if ul:
                self.widget.add(ul)
                return self.widget.render(request)
        if self.render_empty:
            return NON_BREACKING_SPACE
        else:
            return ''

