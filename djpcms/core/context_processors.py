from datetime import datetime
import logging

from djpcms import sites, UnicodeMixin, CHANGE, ADD
from djpcms.models import Page
from djpcms.core.exceptions import ApplicationNotAvailable
from djpcms.core.messages import get_messages
from djpcms.utils import iri_to_uri, escape
from djpcms.html import grid960, htmldoc, List, icons


class PageLink(UnicodeMixin):
    '''Utility for displaying links for page editing/creation.'''
    def __init__(self, request, page):
        self.request = request
        self.page = page
    
    def __unicode__(self):
        if not hasattr(self,'_html'):
            self._html = self.render()
        return self._html
    
    def __len__(self):
        return len(self.__unicode__())
    
    def render(self):
        app = sites.for_model(Page)
        if app:
            cdjp = self.request.DJPCMS.djp(self.request)
            if cdjp and isinstance(cdjp.instance,Page):
                return self.exitlink(cdjp.instance.url)
            else:
                site = app.site
                if not self.page:
                    if Page and site.permissions.has(self.request, ADD, Page):
                        return self.addlink(app)
                elif site.permissions.has(self.request, CHANGE, self.page):
                    return self.changelink(app)
        return ''
    
    def addlink(self, app):
        path = app.addurl(self.request)
        if path:
            info = self.request.DJPCMS
            view = info.view
            kwargs = info.kwargs.copy()
            kwargs['url'] = self.request.path if not info.view else info.view.path()
            path = iri_to_uri(path,kwargs)
            return icons.circle_plus(path,'add page',title="add page contents",button=False)
        else:
            return ''
    
    def changelink(self, app):
        path = app.changeurl(self.request, self.page)
        if path:
            kwargs = iri_to_uri(path,self.request.DJPCMS.kwargs)
            return icons.pencil(path,'edit',title = 'Edit page contents',button=False)
        else:
            return ''

    def exitlink(self, path):
        path = path % dict(self.request.GET.items())
        return icons.circle_close(path,'exit edit',title = 'Exit page editing',button=False)
    

def get_grid960(page):
    float_layout = 0 if not page else page.layout
    return grid960(fixed = not float_layout)


def djpcms(request):
    info = request.DJPCMS
    site = info.site
    page = info.page
    settings = site.settings    
    base_template = settings.DEFAULT_TEMPLATE_NAME[0]
    
    user = getattr(request,'user',None)
    ctx = {'pagelink':PageLink(request,page),
           'base_template': base_template,
           'css':settings.HTML_CLASSES,
           'grid': get_grid960(page),
           'htmldoc': htmldoc(None if not page else page.doctype),
           'jsdebug': 'true' if settings.DEBUG else 'false',
           'request': request,
           'user': user,
           'is_authenticated': False if not user else user.is_authenticated(),
           'debug': settings.DEBUG,
           'release': not settings.DEBUG,
           'now': datetime.now(),
           'MEDIA_URL': settings.MEDIA_URL}
    
    # lets check if there is a user application. The likelihood is that there is one :)
    userapp = site.for_model(site.User)
    if userapp:
        ctx.update({
                    'login_url': userapp.appviewurl(request,'login'),
                    'logout_url': userapp.appviewurl(request,'logout'),
                    })
        if getattr(userapp,'userpage',False):
            url = userapp.viewurl(request, request.user)
        else:
            url = userapp.baseurl
        ctx.update({'user_url': url})
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

