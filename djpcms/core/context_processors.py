import json
from datetime import datetime
import logging

from djpcms import views, html, UnicodeMixin, CHANGE, ADD, Route
from djpcms.utils import iri_to_uri, escape

from .exceptions import ApplicationNotAvailable
from .messages import get_messages


logger = logging.getLogger('djpcms.core.context_processor')

def addlink(request, app):
    #TODO
    #REMOVE
    path = app.addurl(request)
    if path:
        info = request.DJPCMS
        view = info.view
        kwargs = info.kwargs.copy()
        kwargs['url'] = request.path if not view else view.path
        path = iri_to_uri(path,kwargs)
        return html.Widget('a', title="add page contents", cn = 'add',
                           href = path).render(inner = 'add page')
    else:
        return ''

def changelink(request, app):
    #TODO
    #REMOVE
    path = self.app.changeurl(request, self.page)
    if path:
        path = iri_to_uri(path,request.DJPCMS.kwargs)
        return html.Widget('a', href = path,
                            title = 'Edit page contents',
                            cn = 'add').render(inner = 'edit')
    else:
        return ''


def userlinks(request, asbuttons = False):
    app = request.view.root.for_model(request.view.User)
    if app and app.root_view:
        request = request.for_view(app.root_view)
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
    '''Utility for displaying user navigation links.'''
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
            page_request = request.view_for_model(Page)
            if page_request is not None:
                for link in views.application_views_links(
                                    page_request,
                                    instance = page,
                                    include = ('add','change'),
                                    asbuttons = asbuttons):
                    path = iri_to_uri(request.path,request.urlargs)
                    ul.add(link)
                    
    for link in userlinks(request, asbuttons):
        ul.add(link)
            
    return ul


def djpcms(request):
    '''The main template context processor. It must be always included.'''
    page = request.page
    settings = request.view.settings            
    return {'request': request,
            'page':page,
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


def topbar(request, brand = None):
    '''Build a lazy topbar to be place at the top of your web page.
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
    sitenav = views.Navigator(secondary = page_links(request),
                              levels = settings.SITE_NAVIGATION_LEVELS,
                              brand = settings.SITE_NAVIGATION_BRAND,
                              fixed = True,
                              container = container)
    return {'topbar': html.LazyHtml(request,sitenav)}
    
    
def breadcrumbs(request):
    settings = request.view.settings
    if settings.ENABLE_BREADCRUMBS:
        b = views.Breadcrumbs(min_length = settings.ENABLE_BREADCRUMBS)
        return {'breadcrumbs': html.LazyHtml(request,b)}
    else:
        return {}
    