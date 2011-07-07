from datetime import datetime
import logging

from djpcms import views, sites, html, UnicodeMixin, CHANGE, ADD
from djpcms.models import Page
from djpcms.core.exceptions import ApplicationNotAvailable
from djpcms.core.messages import get_messages
from djpcms.utils import iri_to_uri, escape
from djpcms.html import grid960, htmldoc, List, icons


class PageLink(html.List):
    '''Utility for displaying links
for page editing or creation or exit editing.'''
    def __init__(self, request):
        super(PageLink,self).__init__()
        self.request = request
        request = self.request
        info = request.DJPCMS
        self.page = info.page
        # Get the site application for Page
        apps = list(request.DJPCMS.root.for_model(Page))
        if apps:
            self.app = apps[0]
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
                self.append(self.exitlink(self.cdjp.instance.url))
            else:
                site = self.app.site
                if not self.page:
                    if Page and site.permissions.has(self.request, ADD, Page):
                        self.append(self.addlink())
                elif site.permissions.has(self.request, CHANGE, self.page):
                    self.append(self.changelink())
                self.userlinks()
        if request.user.is_superuser and sites.settings.PROFILING_KEY:
            if sites.settings.PROFILING_KEY not in request.REQUEST:
                self.append('<a href={0}?{1}>profile</a>'.format(request.path,\
                                                sites.settings.PROFILING_KEY))
    
    def addlink(self):
        path = self.app.addurl(self.request)
        if path:
            info = self.request.DJPCMS
            view = info.view
            kwargs = info.kwargs.copy()
            kwargs['url'] = self.request.path if not view else view.path
            path = iri_to_uri(path,kwargs)
            return icons.circle_plus(path,'add page',
                                     title="add page contents",button=False)
        else:
            return ''
    
    def changelink(self):
        path = self.app.changeurl(self.request, self.page)
        if path:
            path = iri_to_uri(path,self.request.DJPCMS.kwargs)
            return icons.pencil(path,'edit',
                                title = 'Edit page contents',
                                button=False)
        else:
            return ''

    def exitlink(self, path):
        try:
            path = path % dict(self.request.GET.items())
        except KeyError:
            return ''
        return icons.circle_close(path,'exit',
                                  title = 'Exit page editing',button=False)
    
    def userlinks(self):
        site = self.request.DJPCMS.site
        userapp = site.for_model(site.User)
        if userapp:
            request = self.request
            if request.user.is_authenticated():
                logout_url =  userapp.appviewurl(request,'logout')
                self.addanchor(logout_url,'logout')
                if hasattr(userapp,'userhomeurl'):
                    user_url = userapp.userhomeurl(request)
                    self.addanchor(user_url,request.user.username)
            else:
                self.addanchor(userapp.appviewurl(request,'login'),'login')
                
                
def get_grid960(page, settings):
    float_layout = settings.DEFAULT_LAYOUT if not page else page.layout
    return grid960(fixed = not float_layout)


def djpcms(request):
    '''The main template context processor. It must be always included.'''
    info = request.DJPCMS
    site = info.site
    page = info.page
    settings = site.settings
    base_template = settings.DEFAULT_TEMPLATE_NAME[0]
    try:
        plink = PageLink(request).addClass('horizontal user right')
    except Exception as e:
        plink = html.Widget()
    user = getattr(request,'user',None)
    debug = settings.DEBUG
    ctx = {'pagelink':plink,
           'base_template': base_template,
           'css':settings.HTML_CLASSES,
           'htmldoc': htmldoc(None if not page else page.doctype),
           'request': request,
           'user': user,
           'is_authenticated': False if not user else user.is_authenticated(),
           'debug': debug,
           'release': not debug,
           'now': datetime.now(),
           'MEDIA_URL': settings.MEDIA_URL,
           'grid': get_grid960(page,settings)}
    return ctx


def messages(request):
    """Returns a lazy 'messages' context variable.
    """
    messages = get_messages(request)
    lmsg = []
    if messages:
        for level in sorted(messages):
            msg = List(messages[level], cn = 'messagelist')
            if level < logging.ERROR:
                msg.addClass('ui-state-highlight')
            else:
                msg.addClass('ui-state-error')
            lmsg.append(msg.render())
    return {'messages': lmsg}

