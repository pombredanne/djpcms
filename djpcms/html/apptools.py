from collections import namedtuple

from py2py3 import itervalues

from djpcms.html import icons

from .base import HtmlWidget
from .widgets import Select


__all__ = ['application_action',
           'table_menu_link',
           'application_links',
           'table_toolbox',
           'table_header']

table_header = namedtuple('table_header','code name description')
application_action = namedtuple('application_action','view display permission')
table_menu_link = namedtuple('table_menu_link',
                             'view display title permission icon method ajax')


def application_links(appmodel,
                      djp,
                      asbuttons = True,
                      exclude = None,
                      include = None):
    '''Create a list of application links available to the user'''
    tag = 'button' if asbuttons else 'a'
    permissions = djp.site.permissions
    css = djp.css
    request = djp.request
    instance = djp.instance
    links = []
    exclude = exclude or []
    for ex in appmodel.exclude_links:
        if ex not in exclude:
            exclude.append(ex)
    kwargs  = djp.kwargs
    
    if include is None:
        include = appmodel.views
        
    for elem in include:
        if not isinstance(elem,application_action):
            view = appmodel.views.get(elem,None)
            if not view:
                continue
            descr = view.description or view.name
            try:
                title = view.title(djp)
            except:
                continue
            elem = table_menu_link(view.name,
                                   view.name,
                                   title,
                                   view.PERM,
                                   view.ICON,
                                   view.DEFAULT_METHOD,
                                   view.ajax_enabled)
        else:
            view = appmodel.views.get(elem.view,None)
            if not view:
                if not hasattr(appmodel,'ajax__{0}'.format(elem.view)):
                    continue
                
        if not permissions.has(request,
                               elem.permission,
                               model = appmodel.model,
                               obj = instance, 
                               view = view):
            continue
             
        if not view:
            url = djp.url
        else:
            try:
                url = view(request, **kwargs).url
            except:
                continue
        
        a = HtmlWidget(tag).addAttr('title',elem.title).addAttr('href',url)\
                           .addData('method',elem.method)
        if elem.ajax:
            a.addClass(css.ajax)
        if elem.icon:
            if a.tag == 'a':
                a.addClass(elem.icon)
            else:
                a.addData('icon', elem.icon)
        links.append(a.render(inner = elem.display))
    return links


def table_toolbox(appmodel, djp):
    '''\
Create a toolbox for the table if possible. A toolbox is created when
an application based on database model is available.

:parameter djp: an instance of a :class:`djpcms.views.DjpResponse`.
:parameter appmodel: an instance of a :class:`djpcms.views.Application`.
'''
    request = djp.request
    site = djp.site
    menu = application_links(appmodel,
                             djp,
                             include = appmodel.table_links)
    has = site.permissions.has
    choices = [('','Actions')]
    for name,description,pcode in appmodel.table_actions:
        if has(request, pcode, None):
            choices.append((name,description))
    toolbox = {}
    if len(choices) > 1:
        toolbox['actions'] = Select(choices).addData('url',djp.url).render()
    if menu:
        toolbox['links'] = menu
    groups = appmodel.column_groups(djp)
    if groups:
        data = {}
        choices = []
        for name,headers in groups:
            data[name] = headers
            choices.append((name,name))
        if choices:
            s = Select(choices)
            for name,val in data.items():
                s.addData(name,val)
            toolbox['columnviews'] = s.render()
    return toolbox

