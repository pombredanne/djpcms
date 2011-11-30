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

def userlinks(request):
    userapp = request.for_model(request.view.User)
    if userapp:
        if request.user.is_authenticated():
            logout_url =  userapp.appviewurl(request,'logout')
            self.ul.add(html.Widget('a', 'logout', href = logout_url))
            if hasattr(userapp,'userhomeurl'):
                user_url = userapp.userhomeurl(request)
                a = html.Widget('a', request.user.username, href = user_url)
                self.ul.add(a)
        else:
            login_url = userapp.appviewurl(request,'login')
            if login_url:
                self.ul.add(html.Widget('a', 'login', href = login_url))
                
                
def page_links(request, asbuttons = False):
    '''Utility for displaying links
for page editing or creation or exit editing.'''
    ul = html.Widget('ul')
    view = request.view
    Page = view.Page
    if Page:
        page = request.page
        page_request = request.root_view_for_model(Page)
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
                for link in userlinks(request):
                    ul.add(link)
            
    pk = view.settings.PROFILING_KEY
    if request.user and request.user.is_superuser and pk:
        if view.settings.PROFILING_KEY not in request.REQUEST:
            a = html.Widget('a','profile',href='{0}?{1}'\
                    .format(request.path,pk))
            ul.add(a)
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

