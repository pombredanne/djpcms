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
                      as_widget = False,
                      instance = None):
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
    links = []
    exclude = exclude or []
    for ex in appmodel.exclude_links:
        if ex not in exclude:
            exclude.append(ex)
    kwargs  = djp.kwargs.copy()
    kwargs['instance'] = instance
    
    if include is None:
        include = appmodel.views
        
    for elem in include:
        if not isinstance(elem,application_action):
            view = appmodel.views.get(elem,None)
            if not view:
                continue
            ajax_enabled = view.ajax_enabled
            if instance:
                if not view.object_view:
                    continue
            elif ajax_enabled is None:
                continue
            descr = view.description or view.name
            dview = view(request, **kwargs)
            try:
                url = dview.url
            except:
                continue
            if not dview.has_permission():
                continue
            # The special view class
            #display = nicename(view.name)
            elem = table_menu_link(view.name,
                                   dview.linkname,
                                   dview.title,
                                   view.PERM,
                                   view.ICON,
                                   view.DEFAULT_METHOD,
                                   ajax_enabled)
        else:
            view = appmodel.views.get(elem.view,None)
            if not view:
                if not hasattr(appmodel,'ajax__{0}'.format(elem.view)):
                    continue
                dview = djp
            else:
                dview = view(request, **kwargs)
            url = djp.url
        
        if as_widget:
            a = Widget(tag).addAttr('title',elem.title)\
                           .addData('view',elem.view)\
                           .addData('method',elem.method)\
                           .addData('warning',view.warning_message(dview))
            if elem.ajax:
                a.addClass(css.ajax)
            
            if a.tag == 'a':
                a.addAttr('href',url).addClass(elem.icon)
            else:
                a.addData('icon', elem.icon).addData('href',url)
            elem = (elem.view, a.render(inner = elem.display))
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
    groups = appmodel.column_groups(djp)
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

