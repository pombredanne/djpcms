from collections import namedtuple
from inspect import isgenerator

from djpcms import ajax
from djpcms.html import Table, Paginator, Widget


__all__ = ['application_action','application_views',
           'application_links','table_toolbox',
           'dataTableResponse','instance_link']


application_action = namedtuple('application_action',
                                'view display permission')
table_menu_link = namedtuple('table_menu_link',
                             'view display title permission icon method ajax')



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
    

def headers_from_groups(appmodel, groups):
    ld = appmodel.list_display
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
    if not appmodel:
        return
    view = djp.view
    astable = djp.view.astable
    if not astable or not appmodel.list_display:
        return
    
    request = djp.request
    site = djp.site
    has = site.permissions.has
    choices = []
    for name,description,pcode in appmodel.table_actions:
        if has(request, pcode, None):
            choices.append((name,description))
    
    toolbox = {'as':astable}
    
    if choices:
        toolbox['actions'] = {'choices':choices,
                              'url':djp.url}
        
    if not all:
        return toolbox
    
    menu = list(views_serializable(\
                    application_views(djp, include = appmodel.table_links)))
    if menu:
        toolbox['tools'] = menu
    groups = appmodel.table_column_groups(djp)
    if isgenerator(groups):
        groups = tuple(groups)
    if groups:
        if len(groups) > 1:
            toolbox['groups'] = groups
        toolbox['headers'] = tuple(headers_from_groups(appmodel,groups))
    else:
        toolbox['headers'] = appmodel.list_display

    return toolbox


def dataTableResponse(djp, qs = None, toolbox = None, params = None,
                      headers = None, title = None):
    '''dataTable ajax response'''
    view = djp.view
    request = djp.request
    inputs = request.REQUEST
    appmodel = view.appmodel
    params = params or {}
    if not title:
        block = getattr(djp,'block',None)
        if block and block.title and 'title' not in params:
            title = block.title
    if title:
        params['title'] = title 
    render = not request.is_xhr
    # The table toolbox
    if toolbox is not False:
        toolbox = toolbox or table_toolbox(djp,appmodel)
        headers = headers or toolbox['headers']
    if not headers:
        raise ValueError('No table headers specified. Cannot render a table')
    # Attributes to load from query
    load_only = appmodel.load_fields(headers)
    num_headers = len(headers)
    body = None
    paginate = None
    start = 0
    per_page = appmodel.list_per_page
    page_menu = None
    if qs is None:
        qs = view.appquery(djp)
    
    # We are rendering
    if not render:
        sort_by = {}
        search = inputs.get('sSearch')
        if search:
            qs = qs.search(search)
        sortcols = inputs.get('iSortingCols')
        if sortcols:
            head = None
            for col in range(int(sortcols)):
                c = int(inputs['iSortCol_{0}'.format(col)])
                if c < num_headers:
                    d = '-' if inputs['sSortDir_{0}'.format(col)] == 'desc'\
                             else ''
                    head = headers[c]
                    qs = qs.sort_by('{0}{1}'.format(d,head.attrname))
                
        start = inputs.get('iDisplayStart')
        per_page = inputs.get('iDisplayLength') or per_page
        paginate = True
        
    try:
        total = qs.count()
        query = True
    except:
        query = False
        total = len(qs)
    
    if query:
        qs = qs.load_only(*load_only)
        
    if render:
        # if the ajax flag is not defined in parameters
        if 'ajax' not in params:
            params['ajax'] = djp.url if toolbox.pop('as') == 'ajax' else None
        body = None
        if params.get('ajax'):
            if total > 1.3*per_page:
                page_menu = appmodel.list_per_page_choices
                paginate = True
            
    if paginate:
        paginate = Paginator(total = total,
                             per_page = per_page,
                             start = start,
                             page_menu = page_menu)
        if not render:
            body = paginate.slice_data(qs)
    else:
        body = qs
        
    if body:
        body = appmodel.table_generator(djp,headers,body)
        
    tbl = Table(headers, body,
                appmodel = appmodel,
                paginator = paginate,
                toolbox = toolbox,
                **params)

    
    if render:
        return tbl.render(djp)
    else:
        aaData = []
        for item in tbl.items(djp):
            id = item['id']
            aData = {} if not id else {'DT_RowId':id}
            aData.update(((i,v) for i,v in enumerate(item['display'])))
            aaData.append(aData)
        data = {'iTotalRecords':total,
                'iTotalDisplayRecords':total,
                'sEcho':inputs.get('sEcho'),
                'aaData':aaData}
        return ajax.simplelem(data)
    
