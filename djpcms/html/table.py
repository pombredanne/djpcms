'''\
Utilities for displaying interactive table with pagination and actions.

It uses the Datatable jQuery plugin on the client side.

http://www.datatables.net/
'''
from djpcms.utils import media
from djpcms.utils import ajax

from .nicerepr import *
from .base import Widget, WidgetMaker
from .apptools import table_header, table_toolbox
from .pagination import Paginator 

__all__ = ['Table','dataTableResponse']


class TableMaker(WidgetMaker):
    '''A widget maker which render a dataTable.'''
    tag = 'div'
    default_class = 'data-table'
    table_media = media.Media(
            js = [
                  'djpcms/datatables/jquery.dataTables.js',
                  'djpcms/datatables/ColVis/js/ColVis.js',
                  'djpcms/datatables/TableTools/js/TableTools.min.js',
                  'djpcms/djptable.js'],
            css = {'screen':
                    ['djpcms/datatables/TableTools/css/TableTools_JUI.css']
                    }
        )
    template = '''{% if title %}
<h3 class='table-title ui-widget-header'>{{ title }}</h3>{% endif %}
<table>
<thead>
 <tr>{% for head in headers %}{% if head.description %}
  <th class="hint" title="{{ head.description }}">{% else %}
  <th>{% endif %}{{ head.sTitle }}</th>{% endfor %}
 </tr>
</thead>
<tbody>{% if rows %}{% for row in rows %}
<tr{% if row.id %} class="{{ row.id }}"{% endif %}>{% for item in row.display %}
<td>{{ item }}</td>{% endfor %}
</tr>{% endfor %}{% endif %}
</tbody>{% if footer %}
<tfoot>
 <tr>{% for head in headers %}
  <th>{{ head.sTitle }}</th>{% endfor %}
 </tr>
</tfoot>{% endif %}
</table>
'''
    
    def get_context(self, djp, widget, key):
        title = None
        if djp:
            title = djp.block.title if djp.block else None
        ctx = {'headers':widget.data['options']['aoColumns'],
               'footer':widget.footer,
               'title':title}
        appmodel = widget.internal['appmodel']
        toolbox = widget.toolbox
        if toolbox:
            widget.data.update(toolbox)
        if not widget.ajax:
            ctx['rows'] = widget.items(djp)
        return ctx
    
    def make_headers(self, headers):
        '''Generator of html headers tags'''
        for head in headers:
            w = Widget('th', cn = head.code)
            if head.description:
                w.addData('description',head.description)
            yield w.render(inner = head.name)
    
    def aoColumns(self, headers):
        '''Return an array of column definition to be used by the dataTable
javascript plugin'''
        for head in headers:
            cn = [head.code]
            if head.extraclass:
                cn.append(head.extraclass)
            so = head.sortable
            if so:
                cn.append('sortable')
            yield {'bSortable':head.sortable,
                   'sClass':' '.join(cn),
                   'sName':head.code,
                   'sTitle':head.name,
                   'sWidth':head.width,
                   'description':head.description}
            
    def media(self, djp = None):
        return self.table_media


class Table(Widget):
    '''A Table :class:`djpcms.html.Widget` packed with functionalities
and rendered using the dataTable_ jQuery plugin.

:parameter headers: iterable over headers. Must be provided.
:parameter body: optional iterable over data to display.
:parameter appmodel: optional :class:`djpcms.views.Application` instance.
:parameter model: optional model class. If not provided the model in appmodel
    will be used.
:parameter toolbox: optional dictionary with table toolbox data. Created using
    the :func:`djpcms.html.table_toolbox` function.
:parameter footer: flag indicating if a table footer is required.

    Default ``False``.

.. _dataTable: http://www.datatables.net/
    '''
    maker = TableMaker()
    size_choices = (10,25,50,100)
    
    def __init__(self, headers, body = None, appmodel = None,
                 model = None, paginator = None, toolbox = None,
                 ajax = None, size = 25, size_choices = None,
                 paginate = True, footer = False, title = None,
                 **params):
        self.toolbox = toolbox
        self.ajax = ajax
        self.footer = footer
        self.size_choices = size_choices or self.size_choices
        self.size = size
        self.paginator = paginator
        if appmodel and not model:
            model = appmodel.model
        if not model:
            try:
                model = body.model
            except AttributeError:
                pass
        headers = [table_header(head) for head in headers]
        super(Table,self).__init__(model = model,
                                   appmodel = appmodel,
                                   headers = headers,
                                   body = body,
                                   paginator = paginator,
                                   **params)
        options = {'aoColumns': list(self.maker.aoColumns(headers)),
                   'iDisplayLength':size,
                   'bPaginate':paginate}
        if ajax or (paginator and paginator.multiple):
            options['bProcessing'] = True
            options['bServerSide'] = True
            if ajax:
                options['sAjaxSource'] = ajax
        if 'options' in self.data:
            options.update(self.data['options'])
        self.addData('options',options).addAttr('title',title)

    def items(self, djp):
        body = self.internal['body']
        if body:
            appmodel = self.internal['appmodel']
            headers = self.internal['headers']
            actions = None
            if appmodel and self.toolbox:
                if 'actions' in self.toolbox:
                    actions = self.toolbox.pop('actions')
                
            return (results_for_item(djp, headers, d, appmodel,
                                     actions = actions) for d in body)
        else:
            return ()
        

def dataTableResponse(djp, qs = None, toolbox = None, params = None):
    '''dataTable ajax response'''
    view = djp.view
    request = djp.request
    inputs = request.REQUEST
    appmodel = view.appmodel
    params = params or {}
    render = not request.is_xhr
    # The table toolbox
    toolbox = toolbox or table_toolbox(djp,appmodel)
    headers = toolbox['headers']
    # Attributes to load from query
    load_only = tuple((h.attrname for h in headers))
    nh = len(headers)
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
                if c < nh:
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
    
