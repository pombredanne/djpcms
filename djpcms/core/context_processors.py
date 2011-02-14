from datetime import datetime
from djpcms.core.exceptions import ApplicationNotAvailable
from djpcms.core.messages import get_messages


def djpcms(request):
    site = request.site
    settings = site.settings
    ctx = {'jsdebug': 'true' if settings.DEBUG else 'false',
           'request': request,
           'user': request.user,
           'debug': settings.DEBUG,
           'release': not settings.DEBUG,
           'now': datetime.now,
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

