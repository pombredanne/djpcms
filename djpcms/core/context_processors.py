from datetime import datetime
import logging

from djpcms import views, html, UnicodeMixin, CHANGE, ADD
from djpcms.utils import iri_to_uri, escape

from .exceptions import ApplicationNotAvailable
from .messages import get_messages


logger = logging.getLogger('djpcms.core.context_processor')


class PageLinks(object):
    '''Utility for displaying links
for page editing or creation or exit editing.'''
    def __init__(self, request):
        self.ul = html.Widget('ul')
        view = request.view
        Page = view.Page
        if Page:
            self.page = request.page
            apps = list(request.view.root.for_model(Page))
            self.app = apps[0] if apps else None
            self.isediting = False
            self.cdjp = None
            if self.app:
                try:
                    cdjp = self.cdjp = info.djp(request)
                except:
                    cdjp = None
                if cdjp:
                    epage = cdjp.instance
                    self.isediting = isinstance(epage,Page) and \
                                isinstance(cdjp.view,views.ChangeView)
                    if self.isediting:
                        self.page = epage
                if self.isediting:
                    self.ul.add(self.exitlink(self.cdjp.instance.url))
                else:
                    site = self.app.site
                    if not self.page:
                        if Page and site.permissions.has(self.request, ADD, Page):
                            self.ul.add(self.addlink())
                    elif site.permissions.has(self.request, CHANGE, self.page):
                        self.ul.add(self.changelink())
                    self.userlinks()
                
        pk = view.settings.PROFILING_KEY
        if request.user and request.user.is_superuser and pk:
            if view.settings.PROFILING_KEY not in request.REQUEST:
                a = html.Widget('a','profile',href='{0}?{1}'\
                        .format(request.path,pk))
                self.ul.add(a)
    
    def addlink(self):
        path = self.app.addurl(self.request)
        if path:
            info = self.request.DJPCMS
            view = info.view
            kwargs = info.kwargs.copy()
            kwargs['url'] = self.request.path if not view else view.path
            path = iri_to_uri(path,kwargs)
            return html.Widget('a', title="add page contents", cn = 'add',
                               href = path).render(inner = 'add page')
        else:
            return ''
    
    def changelink(self):
        path = self.app.changeurl(self.request, self.page)
        if path:
            path = iri_to_uri(path,self.request.DJPCMS.kwargs)
            return html.Widget('a', href = path,
                                title = 'Edit page contents',
                                cn = 'add').render(inner = 'edit')
        else:
            return ''

    def exitlink(self, path):
        try:
            path = path % dict(self.request.GET.items())
        except KeyError:
            return ''
        return html.Widget('a', href = path, cn = 'exit',
                            title = 'Exit page editing').render(inner = 'exit')
    
    def userlinks(self):
        site = self.request.DJPCMS.site
        userapp = site.for_model(site.User)
        if userapp:
            request = self.request
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
        plink = PageLinks(request).ul.addClass('horizontal user-nav')
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

