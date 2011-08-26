from collections import namedtuple

from py2py3 import itervalues

from djpcms.html import icons
from djpcms.utils.text import nicename

from .base import Widget
from .widgets import Select


__all__ = ['application_action',
           'table_menu_link',
           'application_views',
           'application_links',
           'application_link',
           'table_toolbox',
           'table_header']


table_header_ = namedtuple('table_header_',
'code name description function sortable width extraclass')
application_action = namedtuple('application_action',
                                'view display permission')
table_menu_link = namedtuple('table_menu_link',
                             'view display title permission icon method ajax')

def table_header(code, name = None, description = None, function = None,
                 sortable = True, width = None, extraclass = None):
    '''Utility for creating an instance of a :class:`table_header_`.'''
    if isinstance(code,table_header_):
        return code
    name = name or nicename(code)
    function = function or code
    return table_header_(code,name,description,function,sortable,width,
                         extraclass)


def application_views(appmodel,
                      djp,
                      exclude = None,
                      include = None,
                      instance = None):
    '''Create a list of application views available to the user.
This function is used in conjunction with an instance or a model of
an :class:`djpcms.views.Application` instance.

:parameter appmodel: instance of a :class:`djpcms.views.Application` class.
:parameter djp: instance of a :class:`djpcms.views.DjpResponse` class.
:parameter asbuttons: optional flag for displaying links as button tags.
                        
                        Default ``True``.
'''
    permissions = djp.site.permissions
    request = djp.request
    links = []
    exclude = exclude or []
    for ex in appmodel.exclude_links:
        if ex not in exclude:
            exclude.append(ex)
    kwargs  = djp.kwargs.copy()
    kwargs['instance'] = instance
    
    if not include:
        include = appmodel.views
        
    for elem in include:
        if elem in exclude:
            continue
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
            elem = table_menu_link(dview,
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
        
        elem = elem._asdict()
        elem['url'] = url
        yield elem


def views_serializable(views):
    for elem in views:
        elem['view'] = elem['view'].name
        yield elem
        
        
def application_links(views, asbuttons = True):
    '''\
:parameter asbuttons: optional flag for displaying links as button tags.
'''
    tag = 'button' if asbuttons else 'a'
    for elem in views:
        djp = elem['view']
        view = djp.view
        css = djp.settings.HTML
        a = Widget(tag).addAttr('title',elem['title'])\
                           .addClass(view.link_class)\
                           .addData({'view':view.name,
                                     'method':elem['method'],
                                     'warning':view.warning_message(djp),
                                     'text':view.link_text})
        if elem['ajax']:
            a.addClass(css.ajax)
        
        if a.tag == 'a':
            a.addAttr('href',elem['url']).addClass(elem['icon'])
        else:
            a.addData('icon', elem['icon']).addData('href',elem['url'])
        yield (view.name, a.render(inner = elem['display'])) 
    

def application_link(view, asbutton = True):
    return list(application_links((view,),asbutton))[0][1]
    

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
    
    menu = list(views_serializable(\
                    application_views(appmodel,
                                      djp,
                                      include = appmodel.table_links)))
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

