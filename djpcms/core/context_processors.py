import json
from datetime import datetime
import logging

from djpcms import views, html, UnicodeMixin, CHANGE, ADD
from djpcms.utils import iri_to_uri, escape

from .exceptions import ApplicationNotAvailable
from .messages import get_messages


logger = logging.getLogger('djpcms.core.context_processor')

def addlink(request, app):
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
    path = self.app.changeurl(request, self.page)
    if path:
        path = iri_to_uri(path,request.DJPCMS.kwargs)
        return html.Widget('a', href = path,
                            title = 'Edit page contents',
                            cn = 'add').render(inner = 'edit')
    else:
        return ''

def exitlink(request, path):
    try:
        path = path % dict(request.GET.items())
    except KeyError:
        return ''
    return html.Widget('a', href = path, cn = 'exit',
                        title = 'Exit page editing').render(inner = 'exit')


def userlinks(request, asbuttons = False):
    request = request.view_for_model(request.view.User)
    if request:
        if request.user.is_authenticated():
            for a in views.application_views_links(request,
                                        asbuttons = asbuttons,
                                        include = ('userhome','logout'),
                                        instance = request.user):
                yield a
            pk = request.view.settings.PROFILING_KEY
            if request.user.is_superuser and pk:
                if request.view.settings.PROFILING_KEY not in request.REQUEST:
                    yield html.Widget('a','profile',href='{0}?{1}'\
                                      .format(request.path,pk))
        else:
            for a in views.application_views_links(user_request,
                                                   asbuttons = asbuttons,
                                                   include = ('login',)):
                yield a
                
                
def page_links(request, asbuttons = False):
    '''Utility for displaying user navigation links.'''
    ul = html.Widget('ul')
    view = request.view
    Page = view.Page
    if Page:
        page = request.page
        page_request = request.view_for_model(Page)
        isediting = False
        if page_request is not None:
            if page_request.view.appmodel == view.appmodel:
                ul.add(exitlink(request, page.url))
            else:
                for name,link in views.application_links(
                                views.application_views(page_request,
                                                        instance = page),
                                asbuttons = asbuttons):
                    #path = iri_to_uri(request.path,request.urlargs)
                    ul.add(link)
                    
    for link in userlinks(request, asbuttons):
        ul.add(link)
            
    return ul
                
                
def get_grid960(page, settings):
    float_layout = settings.DEFAULT_LAYOUT if not page else page.layout
    return html.grid960(fixed = not float_layout)


def djpcms(request):
    '''The main template context processor. It must be always included.'''
    page = request.page
    settings = request.view.settings
    base_template = settings.DEFAULT_TEMPLATE_NAME[0]
    grid = get_grid960(page,settings)
    try:
        plink = page_links(request).addClass('horizontal user-nav')
    except:
        logger.error('Unhadled exception while getting page links',
                     exc_info = True)
        plink = html.Widget(data_stream = (grid.empty,))
    user = request.user
    debug = settings.DEBUG
    html_options = settings.HTML.copy()
    html_options.update({'debug':debug,
                         'media_url': settings.MEDIA_URL})
            
    ctx = {'pagelink':plink,
           'base_template': base_template,
           'htmldoc': html.htmldoc(None if not page else page.doctype),
           'request': request,
           'user': user,
           'is_authenticated': False if not user else user.is_authenticated(),
           'debug': debug,
           'release': not debug,
           'now': datetime.now(),
           'settings': settings,
           'MEDIA_URL': settings.MEDIA_URL,
           'html_options': json.dumps(html_options),
           'media': request.media,
           'grid': grid}
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
    sitenav = views.Navigator(request,
                       right = page_links(request),
                       levels = settings.SITE_NAVIGATION_LEVELS)
    return {'sitenav': html.LazyHtml(request,sitenav)}
    
    
def breadcrumbs(request):
    if settings.ENABLE_BREADCRUMBS:
        b = Breadcrumbs(request, min_length = settings.ENABLE_BREADCRUMBS)
        return {'breadcrumbs': html.LazyHtml(request,b)}
    else:
        return {}
    