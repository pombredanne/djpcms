from collections import namedtuple
from inspect import isgenerator

from djpcms import ajax, DELETE
from djpcms.html import Widget


__all__ = ['application_action','application_views',
           'application_links','table_toolbox',
           'instance_link',
           'paginationResponse','bulk_delete']


application_action = namedtuple('application_action',
                                'view display permission')
table_menu_link = namedtuple('table_menu_link',
                             'view display title permission icon method ajax')


bulk_delete = application_action('bulk_delete','delete',DELETE)


def instance_link(djp, instance, name = 'view', asbuttons = False):
    appmodel = djp.site.for_model(instance, all = True)
    if appmodel:
        views = list(application_views(appmodel,djp,
                                       include = (name,),
                                       instance=instance))
        for _,url in application_links(views, asbuttons = asbuttons):
            return url
        
    return str(instance)


def application_views(djp,
                      exclude = None,
                      include = None,
                      instance = None):
    '''Create a list of application views available to the user.
This function is used in conjunction with
an :class:`Application` instance.

:parameter djp: instance of a :class:`DjpResponse`.
:parameter exclude: optional iterable of view names to exclude.
:parameter include: optional iterable of view names to include.
    If provided it override :attr:`Application.exclude_links`.
    Default ``None``
:parameter instance: optional instance of **appmodel.model**.
    If provided only instnce views will be collected.
:rtype: a generator of dictionaries containing :class:`View` information.
'''
    permissions = djp.site.permissions
    appmodel = djp.appmodel
    request = djp.request
    links = []
    exclude = exclude if exclude is not None else appmodel.exclude_links
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
            url = dview.url
            if not url or not dview.has_permission():
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
    '''A generator of two dimensional tuples containing
the view name and a rendered html tag (either an anchor or a button).

:parameter views: iterator over views obtained from
                    :func:`application_views`
:parameter asbuttons: optional flag for displaying links as button tags.
'''
    tag = 'button' if asbuttons else 'a'
    for elem in views:
        djp = elem['view']
        view = djp.view
        css = djp.settings.HTML
        a = Widget(tag).addAttr('title',elem['title'])\
                           .addClass(view.name)\
                           .addData({'view':view.name,
                                     'method':elem['method'],
                                     'warning':view.warning_message(djp),
                                     'text':view.link_text})
        if elem['ajax']:
            a.addClass(css.ajax)
        
        if a.tag == 'a':
            a.addAttr('href',elem['url'])
            #a.addClass(elem['icon'])
        else:
            a.addData('icon', elem['icon']).addData('href',elem['url'])\
             .addClass(view.link_class)
        yield (view.name, a.render(inner = elem['display'])) 
    

def application_link(view, asbutton = True):
    return list(application_links((view,),asbutton))[0][1]
    

def headers_from_groups(pagination, groups):
    ld = pagination.list_display
    ldsubset = set()
    for group in groups:
        ldsubset.update(group['cols'])
    for col in ld:
        if col.code in ldsubset:
            yield col
            
            
def table_toolbox(djp, all = True):
    '''\
Create a toolbox for a table if possible. A toolbox is created when
an application based on model is available.

:parameter djp: an instance of a :class:`djpcms.views.DjpResponse`.
:rtype: A dictionary containing information for building the toolbox.
    If the toolbox is not available it returns ``None``.
'''
    appmodel = djp.appmodel
    pagination = djp.pagination    
    request = djp.request
    site = djp.site
    has = site.permissions.has
    bulk_actions = []
    toolbox = {}
    
    for name,description,pcode in pagination.bulk_actions:
        if has(request, pcode, None):
            bulk_actions.append((name,description))
    
    if bulk_actions:
        toolbox['actions'] = {'choices':bulk_actions,
                              'url':djp.url}
        
    if not all:
        return toolbox
    
    menu = list(views_serializable(\
                    application_views(djp, include = pagination.actions)))
    if menu:
        toolbox['tools'] = menu
        
    groups = appmodel.table_column_groups(djp)
    if isgenerator(groups):
        groups = tuple(groups)
    if groups:
        if len(groups) > 1:
            toolbox['groups'] = groups
        toolbox['headers'] = tuple(headers_from_groups(pagination,groups))
    else:
        toolbox['headers'] = pagination.list_display

    return toolbox


def paginationResponse(djp, query):
    if isinstance(query,dict):
        query = query.get('qs')
    if isgenerator(query):
        query = list(query)
    
    toolbox = table_toolbox(djp)
    render = True
    needbody = True
    pagination = djp.pagination
    inputs = djp.request.REQUEST
    headers = toolbox['headers']
    ajax = None
    load_only = None
    page_menu = None
    body = None
    
    if pagination.ajax:
        ajax = djp.url
        if djp.request.is_xhr:
            render = False
            needbody = True
        else:
            needbody = False
    
    sort_by = {}
    search = inputs.get('sSearch')
    if search:
        query = query.search(search)
        
    if pagination.astable:
        sortcols = inputs.get('iSortingCols')
        load_only = djp.appmodel.load_fields(headers)
        if sortcols:
            head = None
            for col in range(int(sortcols)):
                c = int(inputs['iSortCol_{0}'.format(col)])
                if c < num_headers:
                    d = '-' if inputs['sSortDir_{0}'.format(col)] == 'desc'\
                             else ''
                    head = headers[c]
                    qs = qs.sort_by('{0}{1}'.format(d,head.attrname))
            
    # Reduce the ammount of data
    if load_only and hasattr(query,'load_only'):
        query = query.load_only(*load_only)
        
    start = inputs.get('iDisplayStart',0)
    per_page = inputs.get('iDisplayLength',pagination.size)
    pag,body = pagination.paginate(query, start, per_page, withbody = needbody)
    
    if body is not None and pagination.astable:
        body = djp.appmodel.table_generator(djp, toolbox['headers'], body)
        
    if render:
        return pagination.widget(body, pagination = pag,
                                 ajax = ajax, toolbox = toolbox,
                                 appmodel = djp.appmodel).render(djp)
    else:
        return pagination.ajaxresponse(djp, body, pagination = pag,
                                       ajax = ajax, toolbox = toolbox,
                                       appmodel = djp.appmodel)
    