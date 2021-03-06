from collections import namedtuple
from inspect import isgenerator, isfunction, ismethod

from djpcms import forms
from djpcms.utils import orms
from djpcms.utils.httpurl import parse_qsl
from djpcms.html import anchor_or_button
from djpcms.cms import permissions


__all__ = ['application_action',
           'application_views',
           'application_links',
           'application_link',
           'instance_field_view_value',
           'application_views_links',
           'table_toolbox',
           'paginationResponse',
           'bulk_delete']


application_action = namedtuple('application_action',
                                'view display permission')
menu_link = namedtuple('menu_link',
                       'view display title permission icon method ajax url')

iscallable = lambda v: isfunction(v) or ismethod(v)

def valid_request(request):
    if request is None or request.url is None:
    #if request is None or request.url is None or not request.has_permission():
        return False
    return True

bulk_delete = application_action('bulk_delete', 'delete', permissions.DELETEALL)


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
                     request.icon,
                     view.DEFAULT_METHOD,
                     view.ajax_enabled,
                     request.url)

def application_views(request,
                      exclude=None,
                      include=None,
                      instance=None,
                      ajax_enabled=None,
                      urlargs=None):
    '''A generator of :class:`Application` views available to the user.

:parameter exclude: optional iterable of :class:`View` names to exclude. It
    provided it overrides the :attr:`Application.exclude_links`.
:parameter include: optional iterable of :class:`View` names to include.
:parameter instance: optional instance of :attr:`Application.model`.
    If provided only instance views will be collected.
:parameter ajax_enabled: if ``True`` only ajax enabled views are considered.
:parameter urlargs: Additional url parameters to use.
:rtype: a generator of dictionaries containing :class:`View` information.
'''
    appmodel = request.view.appmodel
    if not appmodel:
        raise StopIteration
    exclude = set(exclude if exclude is not None else appmodel.exclude_links)
    if appmodel.model:
        instance = request.instance or instance
        instance = instance if isinstance(instance, appmodel.model) else None
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
        if not isinstance(elem, application_action):
            view = appmodel.views.get(elem)
            if hasattr(view, 'root_view'):
                view = view.root_view
            # if this is the current view skip
            if not view or view.hidden or view is request.view:
                continue
            # If an instance is available include only object views
            elif instance is not None and not view.object_view and weak_include:
                continue
            elif ajax_enabled and not view.ajax_enabled:
                continue
            descr = view.description or view.name
            req = request.for_path(view.path, instance=instance,
                                   urlargs=urlargs)
            if not valid_request(req) or not req.has_permission():
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
                yield application_action_to_menu_link(elem, req.url)


def instance_field_view_value(request, instance, field_name, name=None,
                              urlargs=None):
    '''Retrieve a view for a field of an *instance* (if that field is
an instance of a registered model) and its correspondent value.

:parameter instance: a model instance.
:parameter field_name: an *instance* field attribute name.
:parameter name: optional view name
:rtype: a two element tuple ``(view, field_value)``

It is used by :meth:`Application.viewurl`.'''
    if field_name:
        value = getattr(instance, field_name, None)
        if iscallable(value):
            value = value()
        # check that this is not an instance of a model
        mapper = orms.mapper(value)
        if mapper:
            if isinstance(value, mapper.model):
                instance = value
                value = None
            else:
                value = mapper
        elif value is None and name is None:
            return None, None
    else:
        value = None
    return request.for_model(instance=instance,
                             name=name,
                             urlargs=urlargs), value


def views_serializable(views):
    for elem in views:
        elem = elem._asdict()
        view = elem['view']
        if hasattr(view,'view'):
            elem['view'] = view.view.name
        yield elem


def application_links(views, asbuttons=True, icon=True, text=True,
                      icon_size=None):
    '''A generator of two dimensional tuples containing
the view name and a rendered html tag (either an anchor or a button).

:parameter views: iterator over views obtained from
                    :func:`application_views`
:parameter asbuttons: optional flag for displaying links as button tags.
:parameter icon_size: optional size for icon.
'''
    for elem in views:
        if not isinstance(elem, menu_link):
            elem = request_to_menu_link(elem)
        request = elem.view
        view = request.view
        icon = elem.icon if icon else None
        a = anchor_or_button(elem.display if text else '',
                             href=elem.url,
                             icon=icon,
                             title=elem.title,
                             asbutton=asbuttons,
                             size=icon_size)
        a.addClass(view.name).addData({'view': view.name,
                                       'method': elem.method,
                                       'warning' :view.warning_message(request),
                                       'text': view.link_text})
        if elem.ajax:
            method = elem.method.lower()
            a.addClass('ajax')
            if method == 'post':
                data = dict(
                    view.site.submit_data_middleware.extra_form_data(request))
                a.addData('submit', data)
        if asbuttons:
            a.addClass(view.link_class)
        yield view.name, a


def application_views_links(request, asbuttons=True, icon=True, text=True,
                            **kwargs):
    '''Shurtcut function which combines :func:`application_views`
and :func:`application_links` generators. It returns a generator over
anchor or button :class:`djpcms.html.Widget`.'''
    views = application_views(request, **kwargs)
    for _,w in application_links(views,
                                 asbuttons=asbuttons,
                                 icon=icon,
                                 text=text):
        yield w


def application_link(view, value=None, asbutton=True, icon=True, text=True,
                     icon_size=None):
    if view is not None:
        for _, link in application_links((view,), asbutton, icon=icon,
                                         icon_size=icon_size):
            if value is not None:
                link.data_stream[-1] = value
            return link


def headers_from_groups(list_display, groups):
    ldsubset = set()
    for group in groups:
        ldsubset.update(group['cols'])
    for col in list_display:
        if col.code in ldsubset:
            yield col


def table_toolbox(request, appmodel=None, perm_level=None, all=True):
    '''\
Create a toolbox for a table if possible. A toolbox is created when
an application based on model is available.

:parameter request: an instance of a wsgi :class:`djpcms.Request`.
:rtype: A dictionary containing information for building the toolbox.
    If the toolbox is not available it returns ``None``.
'''
    toolbox = {}
    appmodel = appmodel or request.appmodel
    if not appmodel:
        return toolbox
    pagination = request.view.pagination or appmodel.pagination
    model = appmodel.model
    bulk_actions = []
    toolbox = {}
    for name, description, pcode in pagination.bulk_actions:
        if perm_level is None:
            ok = request.has_permission(pcode, model=model)
        else:
            ok = perm_level >= pcode
        if ok:
            bulk_actions.append((name, description))
    if bulk_actions:
        toolbox['actions'] = {'choices':bulk_actions, 'url':request.url}
    if not all:
        return toolbox
    menu = list(views_serializable(\
                    application_views(request, include=pagination.actions)))
    if menu:
        toolbox['tools'] = menu
    groups = appmodel.table_column_groups(request)
    if isgenerator(groups):
        groups = tuple(groups)

    headers, list_display = pagination.header_info(request)
    if groups:
        if len(groups) > 1:
            toolbox['groups'] = groups
        toolbox['headers'] = tuple(headers_from_groups(list_display, groups))
    else:
        toolbox['headers'] = list_display
    return toolbox


def clean_inputs(input, search_string):
    search = {}
    sort = {}
    params = {'search_columns': search,
              'sort': sort}
    for k, v in input.items():
        if not v:
            continue
        if k.startswith(search_string):
            ss = k.split('_')
            if len(ss) == 2:
                search[int(ss[1])] = parse_qsl(v) or [('contains', v)]
            else:
                params['search'] = v
        elif k.startswith('iSortCol'):
            ss = k.split('_')
            if len(ss) == 2:
                sort[int(v)] = input.get('sSortDir_%s' % ss[1], '')
        elif k.startswith('sSortDir'):
            continue
        else:
            params[k] = v
    return params



def paginationResponse(request, query, block=None, toolbox=None,
                       perm_level=None, **kwargs):
    '''Used by :class:`Application` to perform pagination of a query.

:parameter query: a query on a model.

it looks for the following inputs in the request data:

* `sSearch` for performing search
* `iSortingCols` for sorting.
'''
    render = True
    view = request.view
    pagination = view.pagination
    appmodel = view.appmodel
    if isgenerator(query):
        query = list(query)
    elif hasattr(query, 'model'):
        appmodel = request.app_for_model(query.model)
    if not pagination and appmodel:
        pagination = appmodel.pagination
    if toolbox is None:
        toolbox = table_toolbox(request, appmodel=appmodel,
                                perm_level=perm_level)
    mapper = appmodel.mapper
    inputs = dict(((k,v) for k,v in request.REQUEST.items() if v))
    headers = toolbox['headers']
    ajax = None
    load_only = None
    page_menu = None
    body = None
    needbody = True
    if pagination.ajax:
        ajax = request.get_full_path()
        if request.is_xhr:
            render = False
        else:
            needbody = False
    if needbody and request.GET and mapper:
        query = query.filter(**mapper.query_from_mapping(request.GET))
    #
    # Search text
    search_string = inputs.get('search_string', forms.SEARCH_STRING)
    inputs = clean_inputs(request.REQUEST, search_string)
    search = inputs.get('search')
    if search:
        query = query.search(search)
    #
    # Sorting fields
    sort_by = None
    if pagination.ordering:
        sort_by = pagination.ordering
    if pagination.astable:
        load_only = appmodel.load_fields(headers)
        for c, v in inputs.get('sort').items():
            if c < len(headers):
                head = headers[c]
                sort_by = '%s%s' % ('-' if v == 'desc' else '', head.attrname)
        for c, v in inputs.get('search_columns').items():
            if c < len(headers):
                head = headers[c]
                kwargs = dict((('%s__%s' % (head.attrname, lookup), value) for\
                               lookup, value in v))
                query = mapper.filter_query(query, **kwargs)
    #
    if hasattr(query, 'ordering') and sort_by:
        query = query.sort_by(sort_by)
    #
    # Reduce the ammount of data by loading selected fields
    if load_only and hasattr(query, 'load_only'):
        query = query.load_only(*load_only)
    #
    # Pagination
    start = inputs.get('iDisplayStart', 0)
    per_page = inputs.get('iDisplayLength', pagination.size)
    pag, body = pagination.paginate(query, start, per_page, withbody=needbody)

    if body is not None and pagination.astable:
        body = appmodel.table_generator(request, toolbox['headers'], body)

    if render:
        title = block.title if block else None
        return pagination.widget(request,
                     body, pagination=pag,
                     ajax=ajax, toolbox=toolbox,
                     appmodel=appmodel, title=title).render(request)
    else:
        return pagination.ajaxresponse(request, body, pagination=pag,
                                       ajax=ajax, toolbox=toolbox,
                                       appmodel=appmodel)
