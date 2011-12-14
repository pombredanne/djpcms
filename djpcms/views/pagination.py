from collections import namedtuple
from inspect import isgenerator

from djpcms import ajax, DELETE
from djpcms.core.orms import mapper
from djpcms.html import anchor_or_button


__all__ = ['application_action',
           'application_views',
           'application_links',
           'application_link',
           'instance_field_view',
           'application_views_links',
           'table_toolbox',
           'paginationResponse',
           'bulk_delete']


application_action = namedtuple('application_action',
                                'view display permission')
menu_link = namedtuple('menu_link',
                       'view display title permission icon method ajax url')


bulk_delete = application_action('bulk_delete','delete',DELETE)


def application_action_to_menu_link(action, url):
    return menu_link(action.view,
                     action.display,
                     action.display,
                     action.permission,
                     None,
                     None,
                     True,
                     url)
    
def request_to_menu_link(request):
    view = request.view
    return menu_link(request,
                     request.linkname,
                     request.title,
                     view.PERM,
                     view.ICON,
                     view.DEFAULT_METHOD,
                     view.ajax_enabled,
                     request.url)
    
def application_views(request,
                      exclude = None,
                      include = None,
                      instance = None,
                      ajax_enabled = None):
    '''A generator of :class:`Application` views available to the user.

:parameter exclude: optional iterable of :class:`View` names to exclude. It
    provided it overrides the :attr:`Application.exclude_links`.
:parameter include: optional iterable of :class:`View` names to include.
:parameter instance: optional instance of :attr:`Application.model`.
    If provided only instance views will be collected.
:parameter ajax_enabled: if ``True`` only ajax enabled views are considered.
:rtype: a generator of dictionaries containing :class:`View` information.
'''
    appmodel = request.view.appmodel
    exclude = set(exclude if exclude is not None else appmodel.exclude_links)
    if appmodel.model:
        instance = request.instance or instance
        instance = instance if isinstance(instance,appmodel.model) else None
    else:
        instance = None
    
    if not include:
        weak_include = True
        include = appmodel.views
    else:
        # Check that includes are not excluded, if so remove them from
        # the exclude set
        weak_include = False
        exclude = exclude.difference(include)
        
    for elem in include:
        if elem in exclude:
            continue
        if not isinstance(elem,application_action):
            view = appmodel.views.get(elem)
            if hasattr(view,'root_view'):
                view = view.root_view
            # if this is the current view skip
            if not view or view is request.view:
                continue
            elif instance is not None and not view.object_view and weak_include:
                continue
            elif ajax_enabled and not view.ajax_enabled:
                continue
            descr = view.description or view.name
            req = request.for_path(view.path, instance = instance)
            if req is None or not req.has_permission():
                continue
            elem = request_to_menu_link(req)
            yield elem
        else:
            view = appmodel.views.get(elem.view,None)
            if not view:
                if not hasattr(appmodel,'ajax__{0}'.format(elem.view)):
                    continue
                req = request
            else:
                req = request.for_path(view.path)
            if req is not None:
                yield application_action_to_menu_link(elem,req.url)


def instance_field_view(request, instance, field_name, name = None):
    '''Retrieve a view for a field of an *instance* (if that field is
an instance of a registered model).

:parameter instance: a model instance.
:parameter field_name: an *instance* field name.
:parameter name: optional view name

It is used by :meth:`Application.viewurl`.'''
    if field_name:
        value = getattr(instance,field_name,None)
        mp = mapper(value)
        if mp:
            if not isinstance(instance,mp.model):
                instance = value
    return request.for_model(instance = instance, name = name)


def views_serializable(views):
    for elem in views:
        elem = elem._asdict()
        view = elem['view']
        if hasattr(view,'view'):
            elem['view'] = view.view.name
        yield elem
        
        
def application_links(views, asbuttons = True):
    '''A generator of two dimensional tuples containing
the view name and a rendered html tag (either an anchor or a button).

:parameter views: iterator over views obtained from
                    :func:`application_views`
:parameter asbuttons: optional flag for displaying links as button tags.
'''
    for elem in views:
        if not isinstance(elem,menu_link):
            elem = request_to_menu_link(elem)
        request = elem.view
        view = request.view
        a = anchor_or_button(elem.display,
                             href = elem.url,
                             icon = elem.icon,
                             title = elem.title,
                             asbutton = asbuttons)
        a.addClass(view.name).addData({'view':view.name,
                                       'method':elem.method,
                                       'warning':view.warning_message(request),
                                       'text':view.link_text})
        if elem.ajax:
            a.addClass(view.settings.HTML['ajax'])
        
        if asbuttons:
            a.addClass(view.link_class)
            
        yield view.name, a 
    

def application_views_links(request, asbuttons = True, **kwargs):
    '''Shurtcut function which combines :func:`application_views`
and :func:`application_links` generators. It returns a generator over
anchor or button :class:`djpcms.html.Widget`.'''
    views = application_views(request,**kwargs)
    for _,w in application_links(views,asbuttons=asbuttons):
        yield w


def application_link(view, asbutton = True):
    if view is not None:
        return list(application_links((view,),asbutton))[0][1]
    else:
        return None
    

def headers_from_groups(pagination, groups):
    ld = pagination.list_display
    ldsubset = set()
    for group in groups:
        ldsubset.update(group['cols'])
    for col in ld:
        if col.code in ldsubset:
            yield col
            
            
def table_toolbox(request, all = True):
    '''\
Create a toolbox for a table if possible. A toolbox is created when
an application based on model is available.

:parameter request: an instance of a wsgi :class:`djpcms.Request`.
:rtype: A dictionary containing information for building the toolbox.
    If the toolbox is not available it returns ``None``.
'''
    pagination = request.pagination
    appmodel = request.view.appmodel
    has = request.view.permissions.has
    bulk_actions = []
    toolbox = {}
    
    for name,description,pcode in pagination.bulk_actions:
        if has(request, pcode, None):
            bulk_actions.append((name,description))
    
    if bulk_actions:
        toolbox['actions'] = {'choices':bulk_actions,
                              'url':request.url}
        
    if not all:
        return toolbox
    
    menu = list(views_serializable(\
                    application_views(request, include = pagination.actions)))
    if menu:
        toolbox['tools'] = menu
        
    groups = appmodel.table_column_groups(request)
    if isgenerator(groups):
        groups = tuple(groups)
    if groups:
        if len(groups) > 1:
            toolbox['groups'] = groups
        toolbox['headers'] = tuple(headers_from_groups(pagination,groups))
    else:
        toolbox['headers'] = pagination.list_display

    return toolbox

    
def paginationResponse(request, query, block = None, **kwargs):
    '''Used by :class:`Application` to perform pagination of a query.
    
:parameter query: a query on a model.

it looks for the following inputs in the request data:

* `sSearch` for performing search
* `iSortingCols` for sorting.
'''
    if isgenerator(query):
        query = list(query)
    
    toolbox = table_toolbox(request)
    render = True
    needbody = True
    pagination = request.pagination
    view = request.view
    appmodel = view.appmodel
    inputs = request.REQUEST
    headers = toolbox['headers']
    ajax = None
    load_only = None
    page_menu = None
    body = None
    
    if pagination.ajax:
        ajax = request.url
        if request.is_xhr:
            render = False
            needbody = True
        else:
            needbody = False
    
    sort_by = {}
    #search = inputs.get('sSearch')
    #if search:
    #    query = query.search(search)
        
    if pagination.astable:
        sortcols = inputs.get('iSortingCols')
        load_only = appmodel.load_fields(headers)
        if sortcols:
            head = None
            for col in range(int(sortcols)):
                c = int(inputs['iSortCol_{0}'.format(col)])
                if c < len(headers):
                    d = '-' if inputs['sSortDir_{0}'.format(col)] == 'desc'\
                             else ''
                    head = headers[c]
                    qs = query.sort_by('{0}{1}'.format(d,head.attrname))
            
    # Reduce the ammount of data
    if load_only and hasattr(query,'load_only'):
        query = query.load_only(*load_only)
        
    start = inputs.get('iDisplayStart',0)
    per_page = inputs.get('iDisplayLength',pagination.size)
    pag,body = pagination.paginate(query, start, per_page, withbody = needbody)
    
    if body is not None and pagination.astable:
        body = appmodel.table_generator(request, toolbox['headers'], body)
        
    if render:
        return pagination.widget(body, pagination = pag,
                                 ajax = ajax, toolbox = toolbox,
                                 appmodel = appmodel).render(request)
    else:
        return pagination.ajaxresponse(request, body, pagination = pag,
                                       ajax = ajax, toolbox = toolbox,
                                       appmodel = appmodel)
    