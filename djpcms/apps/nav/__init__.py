import json
from datetime import datetime

from djpcms import views, html, CHANGE, ADD, Route
from djpcms.utils import iri_to_uri, escape
from djpcms.html.layout import container, row, column
from djpcms.core.messages import get_messages

topbar_class = 'topbar'
topbar_fixed = 'topbar-fixed'

def userlinks(request, asbuttons = False):
    User = request.view.User
    if User is not None:
        request = request.for_model(User, root = True)
        if request:
            if request.user.is_authenticated():
                for a in views.application_views_links(request,
                                            asbuttons = asbuttons,
                                            include = ('userhome',),
                                            instance = request.user):
                    yield a
                for a in views.application_views_links(request,
                                            asbuttons = asbuttons,
                                            include = ('logout',)):
                    yield a
                pk = request.view.settings.PROFILING_KEY
                if request.user.is_superuser and pk:
                    if request.view.settings.PROFILING_KEY not in request.REQUEST:
                        yield html.Widget('a','profile',href='{0}?{1}'\
                                          .format(request.path,pk))
            else:
                for a in views.application_views_links(request,
                                                       asbuttons = asbuttons,
                                                       include = ('login',)):
                    yield a
                
                
def page_links(request, asbuttons = False):
    '''Utility for displaying page navigation links.'''
    ul = html.Widget('ul')
    view = request.view
    Page = view.Page
    if Page:
        # We are on a page application view
        if view.mapper == Page:
            page = request.instance
            if page:
                route = Route(page.url)
                urlargs = dict(request.GET.items())
                try:
                    path = route.url(**urlargs)
                except:
                    path = '/'
                a = html.anchor_or_button('exit', href = path,
                                          asbutton = asbuttons)
                ul.add(a)
        else:
            page = request.page
            page_request = request.for_model(Page)
            if page_request is not None:
                if page:
                    kwargs = {'next':request.path}
                    include = ('change',)
                else:
                    kwargs = {'url':request.view.path}
                    include = ('add',)
                for link in views.application_views_links(
                                    page_request,
                                    instance = page,
                                    include = include,
                                    asbuttons = asbuttons):
                    kwargs.update(request.urlargs)
                    href = link.attrs['href']
                    link.attrs['href'] = iri_to_uri(href,kwargs)
                    ul.add(link)
                    
    for link in userlinks(request, asbuttons):
        ul.add(link)
            
    return ul


def djpcms(request):
    '''The main template context processor. It must be always included.'''
    settings = request.view.settings            
    return {'request': request,
            'page': request.page,
            'user': request.user,
            'now': datetime.now(),
            'settings': settings,
            'MEDIA_URL': settings.MEDIA_URL,
            'grid': request.cssgrid()}
    return ctx


def messages(request):
    """Returns a lazy 'messages' context variable.
    """
    messages = get_messages(request)
    lmsg = []
    if messages:
        for level in sorted(messages):
            msg = html.Widget('ul')
            lic = 'messagelist ui-state-highlight' if level < logging.ERROR\
                            else 'messagelist ui-state-error'
            for m in messages[level]:
                msg.add(html.Widget('li', m, cn= lic))
            lmsg.append(msg.render())
    return {'messages': lmsg}


def navigator(request):
    settings = request.view.settings
    cn = settings.HTML.get('main_nav')
    sitenav = views.Navigator(secondary = page_links(request),
                              levels = settings.SITE_NAVIGATION_LEVELS)
    return {'sitenav': html.LazyHtml(request,sitenav)}


def _topbar(request):
    '''Build a lazy topbar to be placed at the top of your web page.
There are several customizable parameters available.
    '''
    settings = request.view.settings
    grid = request.cssgrid()
    # If we use a grid create the container
    if grid:
        container = html.Widget('div', cn = grid.column1)
        outer = html.Widget('div', container, cn = grid.container_class)
        outer.add(grid.clear)
    else:
        container = None
    topbar = views.Navigator(secondary = page_links(request),
                             levels = settings.SITE_NAVIGATION_LEVELS,
                             brand = settings.SITE_NAVIGATION_BRAND,
                             fixed = True,
                             container = container)
    return {'topbar': html.LazyHtml(request, topbar)}
    
    
def breadcrumbs(request):
    settings = request.view.settings
    if settings.ENABLE_BREADCRUMBS:
        b = views.Breadcrumbs(min_length = settings.ENABLE_BREADCRUMBS)
        return {'breadcrumbs': html.LazyHtml(request,b)}
    else:
        return {}


class topbar(container):
    default_class = topbar_class
    def __init__(self, brand = None, levels = 2, fixed = True):
        self.brand = brand
        self.levels = levels
        self.fixed = fixed
        inner = container(row(column(1, 1, renderer = self.navigator)))
        super(topbar,self).__init__(inner)
        
    def add_css_data(self, widget):
        if self.fixed:
            widget.addClass(topbar_fixed)
            
    def navigator(self, request, widget, context):
        topbar = views.Navigator(
                            secondary = page_links(request),
                            levels = self.levels,
                            brand = self.brand)
        return topbar.render(request)