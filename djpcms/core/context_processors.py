from datetime import datetime

from djpcms import sites, UnicodeMixin, CHANGE, ADD
from djpcms.models import Page
from djpcms.core.exceptions import ApplicationNotAvailable
from djpcms.core.messages import get_messages
from djpcms.html import grid960, htmldoc


class PageLink(UnicodeMixin):
    
    def __init__(self, request, page):
        self.request = request
        self.page = page
    
    def __unicode__(self):
        site = request.site
        if not self.page:
            if Page and site.permissions.has(self.request, ADD, Page):
                return self.addlink()
        elif site.permissions.has(self.request, CHANGE, self.page):
            return self.editlink()
        return ''
            


def get_grid960(page):
    if page and page.cssinfo:
        return grid960(columns = page.cssinfo.gridsize,
                       fixed = page.cssinfo.fixed)
    else:
        return grid960()


def djpcms(request):
    site = request.site
    page = getattr(request,'page',None)
    if site:
        settings = site.settings
    else:
        settings = sites.settings
        
    base_template = settings.DEFAULT_TEMPLATE_NAME[0]
    
    user = getattr(request,'user',None)
    ctx = {'page':page,
           'pagelink':PageLink(request,page),
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
    return {'messages': get_messages(request)}

