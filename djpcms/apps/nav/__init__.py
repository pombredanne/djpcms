'''Utility module for creating a navigations and bread-crumbs.

Dependency: ``None``
'''
from djpcms import forms, views, html
from djpcms.html.layout import container, row, grid
from djpcms.cms import Route, NEXT_KEY
from djpcms.cms.plugins import DJPplugin
from djpcms.utils.httpurl import iri_to_uri

from .builders import *
from . import classes

layouts = (
           ('v','vertical'),
           ('o','orizontal')
           )
dlayouts = dict(layouts)


class topbar_container(container):
    '''A specialized :class:`djpcms.html.layout.container` conaining
a topbar.'''
    def __init__(self, name='topbar', fixed=True, levels=4,
                 user_page_links=True, page_links=True, brand=None):
        super(topbar_container,self).__init__(name, grid('grid 100'),
                                              renderer=self._render)
        self.addClass(classes.topbar_container)
        self.navigator = Navigator(levels=levels, brand=brand,
                                   cn=classes.topbar)
        self.page_links = page_links
        self.user_page_links = user_page_links
        if fixed:
            self.addClass(classes.topbar_fixed)

    def _render(self, request, namespace, column, blocks):
        '''Render the topbar'''
        if column == 0:
            topbar = self.navigator()
            secondary = topbar.children['secondary']
            if self.user_page_links:
                page_user_links(request, ul=secondary)
            elif self.page_links:
                page_links(request, ul=secondary)
            return topbar.render(request)


def userlinks(request, asbuttons=False):
    request = request.for_model(request.view.User, root = True)
    if request:
        if request.user.is_authenticated():
            for a in views.application_views_links(request,
                                        asbuttons=asbuttons,
                                        include=('view','logout'),
                                        instance=request.user):
                yield a
            pk = request.view.settings.PROFILING_KEY
            if request.user.is_superuser and pk:
                if request.view.settings.PROFILING_KEY not in request.REQUEST:
                    yield html.Widget('a','profile',href='{0}?{1}'\
                                      .format(request.path,pk))
        else:
            for a in views.application_views_links(request,
                                                   asbuttons=asbuttons,
                                                   include=('login',)):
                yield a


def page_links(request, asbuttons=False, ul=None):
    '''Utility for displaying page navigation links.'''
    ul = ul if ul is not None else html.Widget('ul')
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
                    kwargs = {NEXT_KEY: request.path}
                    include = ('change',)
                else:
                    kwargs = {'url': request.view.path}
                    include = ('add',)
                for link in views.application_views_links(
                                    page_request,
                                    instance=page,
                                    include=include,
                                    asbuttons=asbuttons):
                    kwargs.update(request.urlargs)
                    href = link.attrs['href']
                    link.attrs['href'] = iri_to_uri(href, kwargs)
                    ul.add(link)
    return ul


def page_user_links(request, asbuttons=False, ul=None):
    '''Returns a ``ul`` :class:`Widget` for page editing and user links.'''
    ul = page_links(request, asbuttons=asbuttons, ul=ul)
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


##################################################################### PLUGIN

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

    def render(self, request, levels=1, layout='v', **kwargs):
        nav = Navigator(soft=True, levels=int(levels))()
        return nav.addClass(dlayouts.get(layout)).render(request)
