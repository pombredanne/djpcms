from collections import namedtuple

from py2py3 import itervalues

from djpcms.html import icons
from djpcms.utils.text import nicename

from .base import Widget
from .widgets import Select


__all__ = ['application_action',
           'table_menu_link',
           'application_links',
           'table_toolbox',
           'table_header']


table_header_ = namedtuple('table_header_',
                           'code name description function sortable width')
application_action = namedtuple('application_action',
                                'view display permission')
table_menu_link = namedtuple('table_menu_link',
                             'view display title permission icon method ajax')

def table_header(code, name = None, description = None, function = None,
                 sortable = True, width = None):
    '''Utility for creating an instance of a :class:`table_header_`.'''
    if isinstance(code,table_header_):
        return code
    name = name or nicename(code)
    function = function or code
    return table_header_(code,name,description,function,sortable,width)


def application_links(appmodel,
                      djp,
                      asbuttons = True,
                      exclude = None,
                      include = None,
                      as_widget = False):
    '''Create a list of application links available to the user.
This function is used in conjunction with an instance of an :class:`djpcms.views.Application`
instance.

:parameter appmodel: instance of a :class:`djpcms.views.Application` class.
:parameter djp: instance of a :class:`djpcms.views.DjpResponse` class.
:parameter asbuttons: optional flag for displaying links as button tags.
                        
                        Default ``True``.
'''
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
            ajax_enabled = view.ajax_enabled
            if ajax_enabled is None:
                continue
            descr = view.description or view.name
            try:
                title = view.title(djp)
            except:
                continue
            elem = table_menu_link(view.name,
                                   nicename(view.name),
                                   title,
                                   view.PERM,
                                   view.ICON,
                                   view.DEFAULT_METHOD,
                                   ajax_enabled)
        else:
            view = appmodel.views.get(elem.view,None)
            if not view:
                if not hasattr(appmodel,'ajax__{0}'.format(elem.view)):
                    continue
        
        if not view:
            url = djp.url
        else:
            view = view(request, **kwargs)
            try:
                url = view.url
            except:
                continue
            if not view.has_permission():
                continue
        
        if as_widget:
            a = Widget(tag).addAttr('title',elem.title)\
                           .addData('method',elem.method)\
                           .addData('warning',view.warning_message())
            if elem.ajax:
                a.addClass(css.ajax)
            if elem.icon:
                if a.tag == 'a':
                    a.addClass(elem.icon).addAttr('href',url)
                else:
                    a.addData('icon', elem.icon).addData('href',url)
            elem = a.render(inner = elem.display)
        else:
            elem = elem._asdict()
            elem['url'] = url
        links.append(elem)
    return links


def table_toolbox(appmodel, djp, all = True):
    '''\
Create a toolbox for the table if possible. A toolbox is created when
an application based on database model is available.

:parameter djp: an instance of a :class:`djpcms.views.DjpResponse`.
:parameter appmodel: an instance of a :class:`djpcms.views.Application`.
'''
    request = djp.request
    site = djp.site
    has = site.permissions.has
    choices = []
    for name,description,pcode in appmodel.table_actions:
        if has(request, pcode, None):
            choices.append((name,description))
    toolbox = {}
    if choices:
        toolbox['actions'] = {'choices':choices,
                              'url':djp.url}
        
    if not all:
        return toolbox
    
    menu = application_links(appmodel,
                             djp,
                             include = appmodel.table_links)
    if menu:
        toolbox['tools'] = menu
    groups = list(appmodel.column_groups(djp))
    if groups:
        toolbox['groups'] = groups
    #if groups:
    #    data = {}
    #    choices = []
    #    for name,headers in groups:
    #        data[name] = headers
    #        choices.append((name,name))
    #    if choices:
    #        s = Select(choices).widget()
    #        s.addData('views',data)
    #        toolbox['columnviews'] = s.render()
    return toolbox

