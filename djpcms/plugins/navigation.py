from djpcms import forms, views, html, Route
from djpcms.plugins import DJPplugin
from djpcms.utils import iri_to_uri

layouts = (
           ('v','vertical'),
           ('o','orizontal')
           )
dlayouts = dict(layouts)


def userlinks(request, asbuttons = False):
    request = request.for_model(request.view.User, root = True)
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
                a = html.anchor_or_button('exit',
                                          href=path,
                                          icon='exit-page-edit',
                                          asbutton=asbuttons)
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
                    link.attrs['href'] = iri_to_uri(href, kwargs)
                    ul.add(link)
    return ul


def page_user_links(request, asbuttons=False):
    ul = page_links(request, asbuttons=asbuttons)
    for link in userlinks(request, asbuttons):
        ul.add(link)
    return ul


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


def topbar(request):
    '''Build a lazy topbar to be placed at the top of your web page.
There are several customizable parameters available.
    '''
    settings = request.view.settings
    return views.Navigator(secondary = page_user_links(request),
                           levels = settings.SITE_NAVIGATION_LEVELS,
                           brand = settings.SITE_NAVIGATION_BRAND)
    
    
def breadcrumbs(request):
    settings = request.view.settings
    if settings.ENABLE_BREADCRUMBS:
        b = views.Breadcrumbs(min_length = settings.ENABLE_BREADCRUMBS)
        return {'breadcrumbs': html.LazyHtml(request,b)}
    else:
        return {}

class navigationForm(forms.Form):
    levels = forms.ChoiceField(choices = ((1,1),(2,2)))
    layout = forms.ChoiceField(choices = (('v','vertical'),
                                          ('o','orizontal')))


class SoftNavigation(DJPplugin):
    '''Display the site navigation from the closest "soft" root
 for a given number of levels.'''
    name = 'soft-nav'
    description = 'Navigation'
    form = navigationForm
    
    def render(self, request, wrapper, prefix, levels = 1,
               layout = 'v', **kwargs):
        nav_element = html.Widget('div', cn = dlayouts[layout])
        nav = views.Navigator(soft = True, levels = int(levels),
                              nav_element = nav_element)
        return nav.render(request)
    
    
    